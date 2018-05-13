import threading
from typing import List
from hashlib import sha256
from datetime import datetime
from copy import deepcopy

from blockchain.client import config
from blockchain.model_types import Transaction, Block


DIFFICULTY = 2


class Miner(threading.Thread):

    def __init__(self):
        super().__init__()
        self.mine_info = None
        self.mining = threading.Event()

    @staticmethod
    def calculate_reward() -> int:
        return 10

    @classmethod
    def reward(cls, wallet):
        return Transaction(
            receiver=wallet,
            sender=None,
            amount=cls.calculate_reward(),
        )

    @staticmethod
    def _hashcash(payload, nonce) -> str:
        data = (payload + str(nonce)).encode('utf-8')
        return sha256(sha256(data).digest()).hexdigest()

    @staticmethod
    def _hash_transaction_pool(txns_pool) -> str:
        txns_pool_bytes = str(txns_pool).encode('utf-8')
        return sha256(txns_pool_bytes).hexdigest()

    @classmethod
    def mine(cls, payload, txns_pool, reward_wallet):
        nonce = 0
        mined_hash = cls._hashcash(payload, nonce)

        while not mined_hash.startswith('0' * DIFFICULTY):
            nonce += 1
            mined_hash = cls._hashcash(payload, nonce)

        txns_pool.append(Transaction(
            receiver=reward_wallet,
            sender=None,
            amount=cls.calculate_reward()
        ))

        return nonce, mined_hash

    @classmethod
    def mine_for_block(cls, txns_pool, tail_block, reward_wallet):
        timestamp = datetime.now()

        payload = (
            str(tail_block.previous_hash) +
            str(timestamp) +
            cls._hash_transaction_pool(txns_pool)
        )

        txns_pool.append(cls.reward(reward_wallet))

        nonce, mined_hash = cls.mine(
            payload,
            txns_pool,
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

    def _publish_the_block(self, block):
        # TODO: publish to all nodes and update current node's `tail_block`
        raise NotImplementedError()

    def run(self):
        while self.mining.is_set():
            self.mining.wait()

            mined_block = self.mine_for_block(
                self.mine_info['txns_pool'],
                self.mine_info['tail_block'],
                config['WALLET']['Address'],
            )

            # use seperate thread for this please
            self._publish_the_block(mined_block)

    def process_transaction_pool(self,
                                 txns_pool: List[Transaction],
                                 tail_block: Block):
        self.mine_info = {
            'txns_pool': deepcopy(txns_pool),
            'tail_block': tail_block,
        }
        self.mining.set()


miner = Miner()


def start_miner():
    miner.start()
