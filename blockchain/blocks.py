import shelve

blocks = {}
tail_block = None


def get_block(block_hash) -> 'Block':
    # NOTE: this the case when we're getting
    #       the previous block of the first block
    if block_hash is None:
        return None

    return blocks[block_hash]


def set_block(block_hash, block: 'Block'):
    blocks[block_hash] = block


def load():
    global blocks, tail_block
    blocks = shelve.open('blocks.dat', flag='c', writeback=True)
    if 'tail_block' in blocks.keys():
        tail_block = blocks['tail_block']


def save():
    blocks['tail_block'] = tail_block
    blocks.sync()


def close():
    blocks.close()
