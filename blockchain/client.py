from configparser import ConfigParser

import requests

from blockchain.blocks import blocks
from blockchain.model_types import Node, Block

config = ConfigParser()
config.read('config.ini')

FALLBACK_NODES_ADDRESSES = ['127.0.0.1:5000']

tail_block = None
txns_pool = []
node_network = set()


def get_node_network():
    current_node_address = f"{config['SERVER']['Host']}:{config['SERVER']['Port']}"
    for node_address in FALLBACK_NODES_ADDRESSES:

        if node_address == current_node_address:
            continue

        request = {
            'address': node_address,
        }
        nodes = requests.get(f'http://{node_address}/node/node_network/', params=request)

        node_network.add(
            [Node(node) for node in nodes
             if node.address != current_node_address]
        )


def blockchain_address(node):
    return f'{node.address}/node/blockchain'


def get_tail_block(node):
    return Block(requests.get(
        blockchain_address(node),
        {'height': None},
    ))


def get_blockchain():
    global tail_block

    node_network_list = list(node_network)
    tail_block = get_tail_block(node_network_list[0])

    block = tail_block
    node_network_length = len(node_network_list)
    index = node_network_length - 1
    while block.previous_hash is not None:
        block = Block(requests.get(
            blockchain_address(node_network_list[index]),
            {'height': tail_block.height - 1},
        ))
        blocks[block.mined_hash] = block

        index = (index - 1) % node_network_length


def init_client():
    get_node_network()
    get_blockchain()
