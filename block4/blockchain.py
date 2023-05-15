from time import time
from account import Account

from block import Block
from transaction import Transaction
import settings


class Blockchain:
    def __init__(self):
        self.unconfirmed_transactions: list[Transaction] = []
        self.chain: list[Block] = []
        self.accounts: dict[str, Account] = {}

        # Створення Блоку генезіса
        self.chain.append(Block.create_genesis_block())

    def new_block(self):
        block = Block(
            index=self.last_block.index + 1,
            timestamp=time(),
            transactions=self.unconfirmed_transactions,
            previous_hash=self.last_block.hash(),
        )
        # Перезавантаження поточного списку транзакцій
        self.unconfirmed_transactions = []
        self._mine_block(block)
        self._apply_transactions(block.transactions)
        self.chain.append(block)
        return block

    def add_transaction(self, transaction: Transaction):
        account = self.accounts.get(transaction.sender)
        if not account:
            raise Exception("no such sender account")
        if not transaction.verify_signiture(account.public_key):
            raise Exception("invalid signature")
        if not self.accounts.get(transaction.receiver):
            raise Exception("no such receiver account")
        balance = account.balance
        for tr in self.unconfirmed_transactions:
            if tr.sender == transaction.sender:
                balance -= tr.amount
        if (balance - transaction.amount) < 0:
            raise Exception("No Balance")
        self.unconfirmed_transactions.append(transaction)
        return self.last_block.index + 1

    @property
    def last_block(self):
        return self.chain[-1]

    def _mine_block(self, block: Block):
        while not block.hash()[: settings.DIFFICULTY] == "0" * settings.DIFFICULTY:
            block.nonce += 1

    def _apply_transactions(self, transactions: list[Transaction]):
        for tr in transactions:
            self.accounts[tr.sender].update_balance(-tr.amount)
            self.accounts[tr.receiver].update_balance(tr.amount)

    def get_or_register_account(self, public_key: bytes):
        acc = Account.register_account(public_key)
        existing_acc = self.accounts.get(acc.account_id)
        if existing_acc:
            return existing_acc
        self.accounts[acc.account_id] = acc
        return acc
