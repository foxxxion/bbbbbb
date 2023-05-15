import hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)


class Account:
    def __init__(
        self,
        public_key: Ed25519PublicKey,
        balance: int | None = None,
        account_id: str | None = None,
    ) -> None:
        self._public_key = public_key
        self._balance: int = balance or 100
        self._account_id: str = (
            account_id or hashlib.sha256(public_key.public_bytes_raw()).hexdigest()
        )

    @property
    def public_key(self):
        return self._public_key

    @property
    def balance(self):
        return self._balance

    @property
    def account_id(self):
        return self._account_id

    def update_balance(self, amount: int):
        if (self._balance + amount) >= 0:
            self._balance += amount
            return
        raise Exception("No Balance")

    @classmethod
    def register_account(cls, public_key: bytes):
        key = Ed25519PublicKey.from_public_bytes(public_key)
        return cls(key)

    # @classmethod
    # def create_account(cls) -> Self:
    #     key = Ed25519PrivateKey.generate()
    #     return cls(key.public_key())
