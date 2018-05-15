from typing import List

from apistar import Route, http

from blockchain import client
from blockchain.miner import miner
from blockchain.model_types import Transaction, Block, Node, BlockInfo


def validate_transaction(transaction: Transaction) -> bool:
    block = client.tail_block

    # this a sender transactions info
    output_amount = input_amount = 0

    while block is not None:
        for valid_transaction in block.transactions:
            if valid_transaction.receiver == transaction.sender:
                input_amount += valid_transaction.amount
            elif valid_transaction.sender == transaction.sender:
                output_amount += valid_transaction.output_amount

        block = block.previous_block

    # how much amount(money) sender has
    net_amount = output_amount - input_amount

    if transaction.amount <= net_amount:
        return True

    return False


def push_transaction(transaction: Transaction) -> http.JSONResponse:
    if not validate_transaction(transaction):
        return http.JSONResponse({'status': 'Error'}, status_code=400)

    client.txns_pool.append(transaction)
    if len(client.txns_pool) == 100:
        miner.process_transaction_pool(client.txns_pool, client.tail_block)

    return http.JSONResponse({'status': 'Success'}, status_code=200)


def notify_mined_block(block: Block) -> http.JSONResponse:
    raise NotImplementedError()


def get_node_network(node: Node) -> List[Node]:
    client.node_network.add(node.address)
    return list(client.node_network)


def get_block(block_info: BlockInfo) -> Block:
    block = client.tail_block

    while block is not None:
        if block.height == block_info.height:
            return block

    return None


routes = [
    Route('/transactions', method='POST', handler=push_transaction),
    Route('/mined_blocks', method='POST', handler=notify_mined_block),
    Route('/node_network', method='GET', handler=get_node_network),
    Route('/blockchain', method='GET', handler=get_block),
]
