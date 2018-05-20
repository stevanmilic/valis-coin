from typing import List

from apistar import Route, http

from node import client
from node.miner import miner
from node.model_types import Transaction, Block, Node, BlockInfo


def validate_transaction(transaction: Transaction) -> bool:
    unspent_output = client.utxo[transaction.sender]

    for txn in client.txns_pool:
        if txn.receiver == transaction.sender:
            unspent_output += txn.amount
        elif txn.sender == transaction.sender:
            unspent_output -= txn.amount

    return transaction.amount <= unspent_output


def verify_block(block):
    if client.blockchain.tail_block.mined_hash != block.previous_hash:
        return False

    payload = (
        str(client.blockchain.tail_block.previous_hash) +
        str(block.timestamp) +
        miner.hash_transaction_pool(block.txns)
    )

    verify_hash = miner.hashcash(payload, block.nonce)
    return verify_hash == block.mined_hash


def push_transaction(transaction: Transaction) -> http.JSONResponse:
    if not validate_transaction(transaction):
        return http.JSONResponse({'status': 'Error'}, status_code=400)

    client.txns_pool.append(transaction)
    if len(client.txns_pool) == client.TXNS_POOL_SIZE:
        miner.process_txns_pool(client.txns_pool, client.blockchain.tail_block)
        client.txns_pool = []

    return http.JSONResponse({'status': 'Success'}, status_code=200)


def get_node_network(node: Node) -> List[Node]:
    client.node_network.add(node.address)
    return list(client.node_network)


def add_block(block: Block) -> http.JSONResponse:
    if not verify_block(block):
        return http.JSONResponse({'status': 'Error'}, status_code=400)

    # NOTE: this is done in separete thread, hooray
    client.announce_mined_block(block)

    miner.stop_mining()
    client.update_utxo(block.txns)
    client.txns_pool = filter(
        lambda txn: any(b_txn._dict == txn._dict for b_txn in block.txns),
        client.txns_pool
    )

    client.blockchain.set_block(block.mined_hash, block)
    client.blockchain.tail_block = block

    return http.JSONResponse({'status': 'Success'}, status_code=200)


def get_block(block_info: BlockInfo) -> Block:
    if block_info.height is None:
        return client.blockchain.tail_block

    block = client.blockchain.tail_block
    while block is not None:
        if block.height == block_info.height:
            return block
        block = block.previous_block

    return None


routes = [
    Route('/transactions', method='POST', handler=push_transaction),
    Route('/node_network', method='GET', handler=get_node_network),
    Route('/blockchain', method='GET', handler=get_block),
    Route('/blockchain', method='POST', handler=add_block),
]
