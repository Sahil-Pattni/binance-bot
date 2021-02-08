from binance_bot import BinanceBot, BinanceException
import pprint
import os

if __name__ == '__main__':
    env = os.environ
    pp = pprint.PrettyPrinter(indent=4)
    api = env.get('BINANCE_KEY')
    secret = env.get('BINANCE_SECRET')
    ticker = 'ADA'

    binance = BinanceBot(api, secret)
    try:
        latest = binance.get_margin_trades(ticker)
        pp.pprint(latest)
    except BinanceException as e:
        print(e)
    
    
