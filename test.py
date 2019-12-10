import asyncio
from aiostream import stream

from accounts.accounts import get_all_accounts, get_current_prices
from accounts.auth import create_auth
from accounts.trades import stream_trades
from accounts.profits import PnLAverageCost


async def process_account():
    a = create_auth("lunokey.txt")

    pnl = PnLAverageCost()   

    async for trade in stream_trades(a):
        pnl.process_trade(trade)
        g = pnl.get_gains()
        print(f"{trade.datetime} - {trade} - total p/l: {g.unrealised} / {g.realised}")


if __name__ == "__main__":
    asyncio.run(process_account())
