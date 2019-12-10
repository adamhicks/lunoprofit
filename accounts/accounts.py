from collections import namedtuple

from luno_python.client import Client

Account = namedtuple("Account", "currency account_id balance")

def convert_account(acc):
    return Account(
        currency=acc['asset'],
        account_id=int(acc['account_id']),
        balance=acc['balance'],
    )

def get_all_accounts(auth):
    c = Client(api_key_id=auth.key, api_key_secret=auth.secret)
    return [convert_account(a) for a in c.get_balances()['balance']]

def get_current_prices(auth, currencies):
    c = Client(api_key_id=auth.key, api_key_secret=auth.secret)
    pairs = [cur + "EUR" for cur in currencies]
    print(pairs)
    for p in pairs:
        print(c.get_ticker(p))
    return [
        tick
        for tick in c.get_ticker()['tickers']
        if tick['pair'] in pairs
    ]

def calc_worth(acc, prices):
    if acc.currency == "EUR":
        return acc.balance
    
    if acc.currency not in prices:
        return Decimal("0")
    
    return prices[acc.currency] * acc.balance

def get_all_asset_worth(auth, accs):
    currs = [a.currency for a in accs if a.currency != "EUR"]
    prices = get_current_prices(auth, currs)

    return {
        c: calc_worth(acc, prices) 
        for acc in accs
    }