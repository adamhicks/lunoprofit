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

class PnLAverageCost:
    def __init__(self):
        self.total_buy = Decimal("0")
        self.total_buy_cost = Decimal("0")

        self.current_holding = Decimal("0")
        
        self.realised_profit = Decimal("0")

        self.last_price = None

    def average_cost_price(self):
        if self.total_buy <= 0:
            return Decimal("0")
        return self.total_buy_cost / self.total_buy

    def unrealised_gain(self):
        return self.current_holding * (self.last_price - self.average_cost_price())

    def process_trade(self, trade: TradeEntry):
        self.last_price = trade.price
        if trade.type == "BID":
            self.total_buy += trade.base
            self.total_buy_cost += trade.counter
            self.current_holding += trade.base
        elif trade.type == "ASK":
            self.current_holding -= trade.base
            
            cost_basis = self.average_cost_price() * trade.base
            gain = trade.counter - cost_basis
            self.realised_profit += gain
        else:
            raise Exception("Invalid trade")
        if self.current_holding <= 0:
            self.current_holding = Decimal("0")
            self.total_buy = Decimal("0")
            self.total_buy_cost = Decimal("0")
    
    def get_gains(self):
        cents = Decimal('.01')
        r = self.realised_profit.quantize(cents)
        u = self.unrealised_gain().quantize(cents)
        return Gain(realised=r, unrealised=u, total=u+r)