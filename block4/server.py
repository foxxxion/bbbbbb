# Створення екземпляра вузла
import base64
from uuid import uuid4

from fastapi import FastAPI, status
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from blockchain import Blockchain
from transaction import Transaction


app = FastAPI(default_response_class=ORJSONResponse)

# Генерація  унікальної на глобальному рівні адреси для цього вузла
node_identifier = str(uuid4()).replace("-", "")

# Створення екземпляра класу Blockchain
blockchain = Blockchain()


@app.get("/mine")
async def mine():
    block = blockchain.new_block()
    return block


@app.post("/transactions", status_code=status.HTTP_201_CREATED)
async def new_transaction(transaction: Transaction):
    # Створення нової транзакції
    try:
        index = blockchain.add_transaction(transaction)
        return {"message": f"Transaction will be added to Block {index}"}
    except Exception as e:
        return ORJSONResponse(
            {"error": str(e)}, status_code=status.HTTP_400_BAD_REQUEST
        )


@app.get("/transactions")
async def get_transactions():
    return blockchain.unconfirmed_transactions


@app.get("/chain")
async def full_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
    }
    return response


class PublicKey(BaseModel):
    public_key: str


@app.post("/account")
async def create_account(public_key: PublicKey):
    acc = blockchain.get_or_register_account(base64.b64decode(public_key.public_key))
    return {
        "account_id": acc.account_id,
        "balance": acc.balance,
    }


@app.get("/account/{account_id}")
async def get_account(account_id: str):
    acc = blockchain.accounts.get(account_id)
    if acc:
        return {
            "account_id": acc.account_id,
            "balance": acc.balance,
        }
    return ORJSONResponse({"error": "No such account"}, status.HTTP_404_NOT_FOUND)
