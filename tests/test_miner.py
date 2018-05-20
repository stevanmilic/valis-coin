from datetime import datetime

import pytest

from node.miner import Miner, DIFFICULTY
from node.model_types import Transaction, Block


@pytest.fixture
def empty_transaction_pool():
    return []


@pytest.fixture
def payload():
    return 'start_payload'


@pytest.fixture
def wallet():
    return 'node_address'


@pytest.fixture
def reward(wallet):
    return Transaction(
        timestamp=datetime.now(),
        receiver=wallet,
        sender=None,
        amount=Miner.calculate_reward(),
    )


def test_hash_conditions(empty_transaction_pool, wallet, reward):
    txns_to_process = empty_transaction_pool

    Miner.mining.set()
    _, mined_hash = Miner.mine(
        '',
        txns_to_process,
        datetime.now(),
        wallet,
    )

    assert len(txns_to_process) == 1
    assert mined_hash.startswith('0' * DIFFICULTY)


@pytest.fixture
def genesis_block(empty_transaction_pool, wallet, reward):
    txns_to_process = empty_transaction_pool

    Miner.mining.set()
    nonce, mined_hash = Miner.mine(
        '',
        txns_to_process,
        datetime.now(),
        wallet,
    )

    return Block(
        height=0,
        timestamp=datetime.now(),
        txns=txns_to_process,
        mined_hash=mined_hash,
        previous_hash=None,
        nonce=nonce,
    )


def test_mining_for_block(genesis_block, wallet, reward):
    txns_to_process = []

    # this the actual transactions that comes from a client
    txns_to_process.append(Transaction(
        timestamp=datetime.now(),
        receiver='someones_address',
        sender=wallet,
        amount=5,
    ))

    Miner.mining.set()
    mined_block = Miner.mine_for_block(
        txns_to_process,
        genesis_block,
        wallet,
    )

    assert mined_block.height == 1
    assert len(mined_block.txns) == 2
    assert mined_block.previous_hash == genesis_block.mined_hash
