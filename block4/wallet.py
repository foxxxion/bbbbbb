import base64
from pathlib import Path
import sys
import time
from typing import Self
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)
from cryptography.hazmat.primitives import serialization
import httpx

from block import Block
from transaction import Transaction

BLOCKCHAIN_ADDRESS = "http://127.0.0.1:8000"


class Wallet:
    http_client = httpx.Client(base_url=BLOCKCHAIN_ADDRESS)

    def __init__(
        self,
        private_key: Ed25519PrivateKey,
        account_id: str,
        balance: str,
    ) -> None:
        self.private_key = private_key
        self.account_id = account_id
        self.balance = balance

    @classmethod
    def create_account(cls, profile: Path) -> Self:
        key = Ed25519PrivateKey.generate()
        with profile.open("wb") as f:
            f.write(
                key.private_bytes(
                    serialization.Encoding.PEM,
                    serialization.PrivateFormat.PKCS8,
                    serialization.NoEncryption(),
                )
            )
        resp = cls.http_client.post(
            "/account",
            json={
                "public_key": base64.b64encode(
                    key.public_key().public_bytes_raw()
                ).decode(),
            },
        )
        r = resp.json()
        return cls(key, r["account_id"], r["balance"])

    @classmethod
    def load_account(cls, profile: Path):
        with profile.open("rb") as f:
            b = f.read()
        key = serialization.load_pem_private_key(b, password=None)
        assert isinstance(key, Ed25519PrivateKey)
        resp = cls.http_client.post(
            "/account",
            json={
                "public_key": base64.b64encode(
                    key.public_key().public_bytes_raw()
                ).decode(),
            },
        ).json()
        return cls(key, resp["account_id"], resp["balance"])

    def update_account(self):
        resp = self.http_client.get(f"/account/{self.account_id}").json()
        self.balance = resp["balance"]

    def get_chain(self):
        resp = self.http_client.get("/chain").json()
        resp["chain"] = [Block.parse_obj(bl) for bl in resp["chain"]]
        return resp

    def create_transaction(self, recipient: str, amount: int):
        trx = Transaction(
            sender=self.account_id, receiver=recipient, amount=amount, signiture=None
        )
        trx.sign(self.private_key)
        resp = self.http_client.post("/transactions", json=trx.dict())
        if resp.is_success:
            return resp.json()["message"]
        return resp.json()["error"]

    def get_unconfirmed_transactions(self):
        resp = self.http_client.get("/transactions").json()
        trxs = [Transaction.parse_obj(trx) for trx in resp]
        return trxs

    def mining(self):
        block = self.http_client.get("/mine").json()
        self.update_account()
        return Block.parse_obj(block)


def print_transactions(transaction: list[Transaction], prefix: str = ""):
    for tr in transaction:
        print(f"{prefix}Transaction ID: {tr.transaction_id}")
        print(f"{prefix}Sender: {tr.sender}")
        print(f"{prefix}Reciever: {tr.receiver}")
        print(f"{prefix}Amount: {tr.amount}")
        print(f"{prefix}Signiture: {tr.signiture}")
        print()


def print_block(block: Block):
    print(f"Block id: {block.index}")
    print(f"Timestamp: {block.timestamp}")
    print(f"Block hash: {block.hash()}")
    print(f"Previous hash: {block.previous_hash}")
    print(f"Nonce: {block.nonce}")
    print(f"Number of transations: {len(block.transactions)}")
    print("Transactions:")
    print_transactions(block.transactions, "\t")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("no profile arg")
        sys.exit(1)
    pr = Path(f"{sys.argv[1]}.key")
    if pr.exists():
        wallet = Wallet.load_account(pr)
    else:
        wallet = Wallet.create_account(pr)
    while True:
        print(f"Account: {wallet.account_id}")
        print(f"Balance: {wallet.balance}")
        print()
        print("1. Fetch account")
        print("2. Get chain")
        print("3. Get unconfirmed transactions")
        print("4. Create transaction")
        print("5. Trigger mining")
        print("0. Exit")
        user_input = input("Enter number: ")
        match user_input:
            case "0":
                sys.exit(1)
            case "1":
                wallet.update_account()
                print("Done!")
            case "2":
                chain = wallet.get_chain()
                length: int = chain["length"]
                blocks: list[Block] = chain["chain"]
                print("Blockchain:")
                print(f"Chain length: {length}")
                print("Blocks:")
                for block in blocks[-5:]:
                    print_block(block)
                    print()

                input("Press Enter")
                print()
            case "3":
                trxs = wallet.get_unconfirmed_transactions()
                print("Transactions:")
                print_transactions(trxs)
                input("Press Enter")
                print()
            case "4":
                print("Create transaction")
                receiver = input("Receiver: ")
                while True:
                    amount = input("Amount: ")
                    try:
                        amount = int(amount)
                        break
                    except Exception:
                        print("Invalid number")
                resp = wallet.create_transaction(receiver, amount)
                print(resp)
                print()
                input("Press Enter")
                print()
            case "5":
                print("Mining in progress")
                start = time.time()
                block = wallet.mining()
                end = time.time()
                print(f"Block mined in {end - start} seconds")
                print("Mined block:")
                print_block(block)
                print()
                input("Press Enter")
                print()
            case _:
                continue
