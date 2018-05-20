import json
from configparser import ConfigParser
from collections import defaultdict
from threading import Thread

import requests

from node import blockchain
from node.model_types import Block

config = ConfigParser()
config.read('config.ini')

txns_pool = []
utxo = defaultdict(int)
node_network = set()

TXNS_POOL_SIZE = 5
FALLBACK_NODES_ADDRESSES = ['127.0.0.1:5000']


def get_node_network():
    """Attempts to retrieve the node network from a list of known nodes

    In case the only node on the list is itself, no nodes get added.
    """
    global node_network

    current_node_address = f"{config['SERVER']['Host']}:{config['SERVER']['Port']}"
    for node_address in FALLBACK_NODES_ADDRESSES:

        if node_address == current_node_address:
            continue

        node_network.add(node_address)

        request = {
            'address': current_node_address,
        }
        response = requests.get(
            f'http://{node_address}/node/node_network',
            data=request,
        )

        node_network = node_network.union(
            set(node for node in response.json()
                if node != current_node_address)
        )


def get_block_by_height(node, height):
    data = requests.get(
        f'http://{node}/node/blockchain',
        json={'height': height},
    ).json()

    if data is None:
        return None

    return Block(data)


def get_blockchain():
    global tail_block

    node_network_list = list(node_network)
    blockchain.tail_block = get_block_by_height(node_network_list[0], None)

    if blockchain.tail_block is None:
        return

    block = blockchain.tail_block
    blockchain.set_block(block.mined_hash, block)

    node_network_length = len(node_network_list)
    index = node_network_length - 1
    while block.previous_hash is not None:
        block = get_block_by_height(
            node_network_list[index],
            block.height - 1,
        )
        # TODO: verify block before accepting it
        blockchain.set_block(block.mined_hash, block)
        index = (index - 1) % node_network_length


def update_utxo(txns):
    for txn in txns:
        utxo[txn.receiver] += txn.amount
        if txn.sender:
            utxo[txn.sender] -= txn.amount


def init_utxo():
    block = blockchain.tail_block
    while block is not None:
        update_utxo(block.txns)
        block = block.previous_block


def init_client():
    """Initializes the client interface towards other nodes.

    - Attempts discovering nodes by requesting them from known nodes
    - Attempts retrieving the blockchain from the discovered nodes
    - Attempls initilization of utxo database used for validating transactions
    """
    get_node_network()

    if node_network:
        get_blockchain()

    if blockchain.tail_block:
        init_utxo()


def notify_nodes(block):
    for node in node_network:
        # TODO: refactor this serialization please :/
        data = dict(block._dict)
        data['timestamp'] = str(data['timestamp'])

        txns = []
        for txn in block.txns:
            txn_data = dict(txn._dict)
            txn_data['timestamp'] = str(txn_data['timestamp'])
            txns.append(txn_data)
        data['txns'] = txns

        requests.post(
            f'http://{node}/node/blockchain',
            data=json.dumps(data),
        )


def announce_mined_block(block):
    """
    Notify other nodes about the mined block, this will cause a broadcast storm
    but oh well ¯\_(ツ)_/¯
    Function is executed in separete thread to unblock the main thread of execution.
    """
    announcement_thread = Thread(target=notify_nodes, args=(block,))
    announcement_thread.start()
