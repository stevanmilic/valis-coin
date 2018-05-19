import shelve

blockchain = {}
tail_block = None


def get_block(block_hash) -> 'Block':
    # NOTE: this the case when we're getting
    #       the previous block of the first block
    if block_hash is None:
        return None

    return blockchain[block_hash]


def set_block(block_hash, block: 'Block'):
    blockchain[block_hash] = block


def load():
    global blockchain, tail_block
    blockchain = shelve.open('blockchain.dat', flag='c', writeback=True)
    if 'tail_block' in blockchain.keys():
        tail_block = blockchain['tail_block']


def save():
    blockchain['tail_block'] = tail_block
    blockchain.sync()


def close():
    blockchain.close()
