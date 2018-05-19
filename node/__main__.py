from datetime import datetime

from node import blockchain
from node import client
from node.miner import start_miner, Miner
from node.server import start_server
from node.model_types import Block


def bootstrap_blockchain():
    txns_to_process = []

    nonce, mined_hash = Miner.mine(
        'start_payload',
        txns_to_process,
        client.config['WALLET']['Address'],
    )

    block = Block(
        height=0,
        timestamp=datetime.now(),
        txns=txns_to_process,
        mined_hash=mined_hash,
        previous_hash=None,
        nonce=nonce,
    )

    blockchain.load()
    blockchain.set_block(block.mined_hash, block)
    blockchain.tail_block = block
    blockchain.save()
    blockchain.close()


def main(args=None):
    blockchain.load()
    client.init_client()
    start_miner()
    try:
        start_server()
    except KeyboardInterrupt:
        pass
    blockchain.close()


def debug():
    import sys

    def info(type, value, tb):
        if hasattr(sys, 'ps1') or not sys.stderr.isatty():
            # we are in interactive mode or we don't have a tty-like
            # device, so we call the default hook
            sys.__excepthook__(type, value, tb)
        else:
            import traceback, pdb
            # we are NOT in interactive mode, print the exception...
            traceback.print_exception(type, value, tb)
            print
            # ...then start the debugger in post-mortem mode.
            pdb.post_mortem(tb)

    sys.excepthook = info

    main()


if __name__ == "__main__":
    main()
