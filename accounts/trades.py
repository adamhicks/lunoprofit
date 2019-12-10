from time import sleep
from collections import namedtuple
from decimal import Decimal
from datetime import datetime
from typing import Sequence
from asyncio import sleep

from luno_python.client import Client

TradeEntry = namedtuple(
    "TradeEntry",
    "base counter price volume type timestamp datetime",
)

def desc_trade(trade):
    if trade.type == "BID":
        return f"Bought {trade.base} @ {trade.price}"
    elif trade.type == "ASK":
        return f"Sold {trade.base} @ {trade.price}"
    else:
        return "Unknown trade"

TradeEntry.__repr__ = desc_trade

def from_unix_ns(ts_ns: int) -> datetime:
    unix_ms = ts_ns / 1000
    return datetime.utcfromtimestamp(unix_ms)

def convert_trade(t):
    return TradeEntry(
        base=Decimal(str(t['base'])),
        counter=Decimal(str(t['counter'])),
        price=Decimal(str(t['price'])),
        volume=Decimal(str(t['volume'])),
        type=t['type'],
        timestamp=t['timestamp'],
        datetime=from_unix_ns(t['timestamp']),
    )

async def stream_trades(auth):
    c = Client(api_key_id=auth.key, api_key_secret=auth.secret)

    since = 0
    while True:
        try:
            resp = c.list_user_trades("XBTEUR", since=since)
        except Exception as e:
            if "429" in str(e):
                await sleep(5)
                continue
            else:
                raise

        trades = resp['trades']
        for t in trades:
            trade = convert_trade(t)
            since = trade.timestamp
            yield trade
        
        if not trades:
            await sleep(60)
