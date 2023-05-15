from uuid import uuid4
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.exceptions import InvalidSignature
import orjson
from pydantic import BaseModel, Field


class Transaction(BaseModel):
    sender: str
    receiver: str
    amount: int
    signiture: str | None
    transaction_id: str = Field(default_factory=lambda: str(uuid4()))

    def verify_signiture(self, public_key: Ed25519PublicKey) -> bool:
        assert self.signiture is not None
        trx = orjson.dumps(
            self.dict(exclude={"signiture"}),
            option=orjson.OPT_SORT_KEYS,
        )
        try:
            public_key.verify(bytes.fromhex(self.signiture), trx)
        except InvalidSignature:
            return False
        return True

    def sign(self, private_key: Ed25519PrivateKey):
        trx = orjson.dumps(
            self.dict(exclude={"signiture"}),
            option=orjson.OPT_SORT_KEYS,
        )
        self.signiture = private_key.sign(trx).hex()
