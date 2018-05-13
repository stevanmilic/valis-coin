from datetime import datetime

import pytest

from blockchain.miner import Miner, DIFFICULTY
from blockchain.model_types import Transaction, Block


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
        receiver=wallet,
        sender=None,
        amount=Miner.calculate_reward(),
    )


def test_hash_conditions(empty_transaction_pool, wallet, reward):
    txns_to_process = empty_transaction_pool + [reward]

    _, mined_hash = Miner.mine(
        'start_payload',
        txns_to_process,
        wallet,
    )

    assert mined_hash.startswith('0' * DIFFICULTY)


@pytest.fixture
def genesis_block(empty_transaction_pool, wallet, reward):
    txns_to_process = empty_transaction_pool + [reward]

    nonce, mined_hash = Miner.mine(
        'start_payload',
        txns_to_process,
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


def test_mining_for_block(empty_transaction_pool, genesis_block, wallet, reward):
    txns_to_process = empty_transaction_pool + [reward]

    # this the actual transactions that comes from a client
    txns_to_process.append(Transaction(
        receiver='someones_address',
        sender=wallet,
        amount=5,
    ))

    mined_block = Miner.mine_for_block(
        empty_transaction_pool,
        genesis_block,
        wallet,
    )

    assert mined_block.height == 1
    assert mined_block.previous_hash == genesis_block.mined_hash
