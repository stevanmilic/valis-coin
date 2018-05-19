from datetime import datetime

from blockchain import blocks
from blockchain import client
from blockchain.miner import start_miner, Miner
from blockchain.server import start_server
from blockchain.model_types import Block


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

    blocks.load()
    blocks.set_block(block.mined_hash, block)
    blocks.tail_block = block
    blocks.save()
    blocks.close()


def main(args=None):
    blocks.load()
    client.init_client()
    start_miner()
    try:
        start_server()
    except KeyboardInterrupt:
        pass
    blocks.close()


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
