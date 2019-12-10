from re import match
from collections import defaultdict
from decimal import Decimal
from accounts.trades import TradeEntry
from collections import namedtuple

trading_matches = [
    r"Bought",
    r"Sold",
    r"Trading Fee",
]

class ProfitCalc:
    def __init__(self, balances, current_prices):
        self.net_assets = defaultdict(Decimal)
        self.balances = balances
        

    def _is_trading_entry(self, entry):
        for regex in trading_matches:
            if match(regex, entry.desc):
                return True
        return False

    def process_entry(self, entry):
        if not self._is_trading_entry(entry):
            print(entry)
            self.net_assets[entry.currency] += entry.balance_delta
            print(self.net_assets)

Gain = namedtuple("Gain", "realised unrealised total")

class StackedAsset():
    def __init__(self, base, price):
        self.base = base
        self.price = price

    def sell(self, sale_trade, trade_vol):
        volume = min(self.base, trade_vol)
        gain = volume * (sale_trade.price - self.price)
        self.base -= volume
        return gain, trade_vol - volume

class PnLFIFO:
    def __init__(self):
        self.assets = []
        self.realised_gain = Decimal("0")
        self.last_price = None

    def unrealised_gain(self, price):
        holding, holding_cost = Decimal("0"), Decimal("0")
        for a in self.assets:
            holding += a.base
            holding_cost += a.base * a.price

        return (holding * price) - holding_cost

    def process_trade(self, trade: TradeEntry):
        self.last_price = trade.price

        if trade.type == "BID":
            asset = StackedAsset(trade.base, trade.price)
            self.assets.append() # FIFO
            # self.assets.insert(0, asset) # LIFO
        elif trade.type == "ASK":
            vol = trade.base
            while vol > 0 and self.assets:
                asset = self.assets[0]
                gain, vol = asset.sell(trade, vol)
                if asset.base == 0:
                    self.assets.pop(0)

                self.realised_gain += gain
        else:
            raise Exception("Invalid trade")

    def get_gains(self):
        cents = Decimal('.01')
        u, r = self.unrealised_gain(self.last_price), self.realised_gain
        u = u.quantize(cents)
        r = r.quantize(cents)
        return Gain(realised=r, unrealised=u, total=u+r)

class PnLAverageCost:
    def __init__(self):
        self.total_buy_cost = Decimal("0")
        self.current_holding = Decimal("0")
        
        self.realised_profit = Decimal("0")
        self.last_price = None

    def average_cost_price(self):
        if self.current_holding <= 0:
            return Decimal("0")
        return self.total_buy_cost / self.current_holding

    def unrealised_gain(self, price):
        return self.current_holding * (price - self.average_cost_price())

    def process_trade(self, trade: TradeEntry):
        self.last_price = trade.price
        if trade.type == "BID":
            self.current_holding += trade.base
            self.total_buy_cost += trade.counter
        elif trade.type == "ASK":
            cost_basis = self.average_cost_price() * trade.base

            self.current_holding -= trade.base
            self.total_buy_cost -= cost_basis
            self.realised_profit += trade.counter - cost_basis
        else:
            raise Exception("Invalid trade")

        if self.current_holding <= 0:
            self.current_holding = Decimal("0")
            self.total_buy_cost = Decimal("0")
    
    def get_gains(self):
        cents = Decimal('.01')
        r = self.realised_profit.quantize(cents)
        u = self.unrealised_gain(self.last_price).quantize(cents)
        return Gain(realised=r, unrealised=u, total=u+r)