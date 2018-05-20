import threading
from typing import List
from hashlib import sha256
from datetime import datetime

from node import client
from node.model_types import Transaction, Block


DIFFICULTY = 2


class Miner(threading.Thread):
    mining = threading.Event()

    def __init__(self):
        super().__init__()
        self.mine_info = None
        # TODO: use this lock ... concurrently
        self.lock = threading.Lock()

    @staticmethod
    def calculate_reward() -> int:
        return 10

    @classmethod
    def reward(cls, wallet):
        return Transaction(
            timestamp=datetime.now(),
            receiver=wallet,
            sender=None,
            amount=cls.calculate_reward(),
        )

    @staticmethod
    def hashcash(payload, nonce) -> str:
        data = (payload + str(nonce)).encode('utf-8')
        return sha256(sha256(data).digest()).hexdigest()

    @staticmethod
    def hash_transaction_pool(txns_pool) -> str:
        txns_pool_bytes = str(txns_pool).encode('utf-8')
        return sha256(txns_pool_bytes).hexdigest()

    @classmethod
    def mine(cls, previous_hash, txns_pool, timestamp, reward_wallet):
        txns_pool.append(cls.reward(reward_wallet))

        payload = (
            str(previous_hash) +
            str(timestamp) +
            cls.hash_transaction_pool(txns_pool)
        )
        nonce = 0

        mined_hash = cls.hashcash(payload, nonce)
        while not mined_hash.startswith('0' * DIFFICULTY):
            if not cls.mining.is_set():
                return None
            nonce += 1
            mined_hash = cls.hashcash(payload, nonce)

        return nonce, mined_hash

    @classmethod
    def mine_for_block(cls, txns_pool, tail_block, reward_wallet):
        timestamp = datetime.now()
        nonce, mined_hash = cls.mine(
            tail_block.previous_hash,
            txns_pool,
            timestamp,
            reward_wallet,
        )

        return Block(
            height=tail_block.height + 1,
            timestamp=timestamp,
            txns=txns_pool,
            mined_hash=mined_hash,
            previous_hash=tail_block.mined_hash,
            nonce=nonce,
        )

    @classmethod
    def publish_the_block(cls, mined_block):
        client.blockchain.tail_block = mined_block
        client.update_utxo(mined_block.txns)
        # NOTE: this is done in separete thread, hooray
        client.announce_mined_block(mined_block)

    def run(self):
        while self.mining.wait():
            mined_block = self.mine_for_block(
                self.mine_info['txns_pool'],
                self.mine_info['tail_block'],
                client.config['WALLET']['Address'],
            )

            # mining could be interrupted by new block which arrived
            # from some other node. if there is no interruption, publish
            if self.mining.is_set():
                self.mining.clear()
                self.publish_the_block(mined_block)

    def process_txns_pool(self,
                          txns_pool: List[Transaction],
                          tail_block: Block):
        # deeocopy of txns_pool
        txns_pool_copy = []
        for txn in txns_pool:
            txns_pool_copy.append(Transaction(dict(txn)))

        self.mine_info = {
            'txns_pool': txns_pool_copy,
            'tail_block': tail_block,
        }
        self.mining.set()

    def stop_mining(self):
        self.mining.clear()


miner = Miner()


def start_miner():
    miner.daemon = True
    miner.start()
