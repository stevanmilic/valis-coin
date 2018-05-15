from apistar import types, validators

from blockchain.blocks import get_block


class PickleType(types.Type):

    def __getstate__(self):
        return self._dict

    def __setstate__(self, _dict):
        object.__setattr__(self, '_dict', _dict)


class Transaction(PickleType):
    sender = validators.String(max_length=100, allow_null=True)
    receiver = validators.String(max_length=100)
    amount = validators.Integer()


class Block(PickleType):
    height = validators.Integer()
    timestamp = validators.DateTime()
    txns = validators.Array(items=Transaction, allow_null=True, default=[])
    mined_hash = validators.String(max_length=100)
    previous_hash = validators.String(max_length=100, allow_null=True)
    nonce = validators.Integer()

    @property
    def previous_block(self):
        return get_block(self.previous_hash)


class Node(PickleType):
    address = validators.String(max_length=100)
    # last_seen = validators.DateTime()
    # TBD^


class BlockInfo(PickleType):
    height = validators.Integer()
