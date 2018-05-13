from apistar import types, validators

from blockchain.blocks import get_block


class Transaction(types.Type):
    sender = validators.String(max_length=100, allow_null=True)
    receiver = validators.String(max_length=100)
    amount = validators.Integer()


class Block(types.Type):
    height = validators.Integer()
    timestamp = validators.DateTime()
    txns = validators.Array(items=Transaction, allow_null=True, default=[])
    mined_hash = validators.String(max_length=100)
    previous_hash = validators.String(max_length=100, allow_null=True)
    nonce = validators.Integer()

    @property
    def previous_block(self):
        return get_block(self.previous_hash)


class Node(types.Type):
    address = validators.String(max_length=100)
    # last_seen = validators.DateTime()
    # TBD^


class BlockInfo(types.Type):
    height = validators.Integer(allow_null=True)
