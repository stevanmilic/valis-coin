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
    """Attempts to retrieve the node network from a list of known nodes

    In case the only node on the list is itself, no nodes get added.
    """
    current_node_address = f"{config['SERVER']['Host']}:{config['SERVER']['Port']}"
    for node_address in FALLBACK_NODES_ADDRESSES:

        if node_address == current_node_address:
            continue

        request = {
            'address': node_address,
        }
        nodes = requests.get(f'http://{node_address}/node/node_network/', params=request)

        node_network.add(
            [Node(node) for node in nodes.json()
             if node != current_node_address]
        )


def get_block_by_height(node, height):
    response = requests.get(
        f'{node.address}/node/blockchain',
        {'height': height},
    )
    return Block(response.data())


def get_blockchain():
    global tail_block

    node_network_list = list(node_network)
    tail_block = get_block_by_height(node_network_list[0], None)

    block = tail_block
    node_network_length = len(node_network_list)
    index = node_network_length - 1
    while block.previous_hash is not None:
        get_block_by_height(
            node_network_list[index],
            tail_block.height,
        )
        blocks[block.mined_hash] = block

        index = (index - 1) % node_network_length


def init_client():
    """Initializes the client interface towards other nodes.

    - Attempts discovering nodes by requesting them from known nodes
    - Attempts retrieving the blockchain from the discovered nodes
    """
    get_node_network()

    if len(node_network) > 0:
        get_blockchain()
