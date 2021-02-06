from binance_bot import BinanceBot, BinanceException
import os

if __name__ == '__main__':
    env = os.environ
    api = env.get('BINANCE_KEY')
    secret = env.get('BINANCE_SECRET')
    ticker = 'BTCUSDT'
    binance = BinanceBot(api, secret)
    try:
        latest = binance.price()
        print(latest)
    except BinanceException as e:
        print(e)
    
    
