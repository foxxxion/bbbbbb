import hashlib
from time import time

import orjson
from pydantic import BaseModel

from transaction import Transaction


class Block(BaseModel):
    index: int
    timestamp: float
    transactions: list[Transaction]
    previous_hash: str
    nonce: int = 0

    def hash(self):
        """
        Створює хеш SHA-256 блоку
        """

        # Потрібно переконатись в тому, що словник упорядкований,
        # інакше будуть непослідовні хеші
        block_string = orjson.dumps(self.dict(), option=orjson.OPT_SORT_KEYS)
        return hashlib.sha256(block_string).hexdigest()

    @classmethod
    def create_genesis_block(cls):
        return cls(index=0, timestamp=time(), transactions=[], previous_hash="0")
