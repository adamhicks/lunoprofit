from time import sleep
from collections import namedtuple
from decimal import Decimal
from datetime import datetime
from typing import Sequence
from asyncio import sleep

from luno_python.client import Client

# "transactions": [
# {
#     "row_index": 2,
#     "timestamp": 1429908835000,
#     "balance": 0.08,
#     "available": 0.08,
#     "balance_delta": -0.02,
#     "available_delta": -0.02,
#     "currency": "XBT",
#     "description": "Sold 0.02 BTC"
# },

LUNO_MAX_TX = 1000

TransactionEntry = namedtuple(
    "TransactionEntry",
    "id timestamp currency balance available balance_delta available_delta desc details",
)

def from_unix_ns(ts_ns: int) -> datetime:
    unix_ms = ts_ns / 1000
    return datetime.utcfromtimestamp(unix_ms)

def convert_transaction(t):
    return TransactionEntry(
        id=t['row_index'],
        timestamp=from_unix_ns(t['timestamp']),
        currency=t['currency'],
        balance=Decimal(str(t['balance'])),
        available=Decimal(str(t['available'])),
        balance_delta=Decimal(str(t['balance_delta'])),
        available_delta=Decimal(str(t['available_delta'])),
        desc=t['description'],
        details=t['details'],
    )


async def stream_ledger(auth, account_id, ledger_no):
    c = Client(api_key_id=auth.key, api_key_secret=auth.secret)

    current = ledger_no

    while True:
        min_row = current + 1
        max_row = min_row + LUNO_MAX_TX

        try:
            resp = c.list_transactions(account_id, max_row, min_row)
        except Exception as e:
            if "429" in str(e):
                await sleep(5)
                continue
            else:
                raise

        transactions = resp['transactions']
        for t in reversed(transactions):
            tx = convert_transaction(t)
            current = tx.id
            yield tx
        
        if not transactions:
            await sleep(60)
