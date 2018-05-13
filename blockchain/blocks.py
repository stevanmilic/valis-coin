blocks = {}


def get_block(block_hash) -> 'Block':
    # NOTE: this the case when we're getting
    #       the previous block of the first block
    if block_hash is None:
        return None

    return blocks[block_hash]
