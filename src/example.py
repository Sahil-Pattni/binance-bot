from binance_bot import BinanceBot, BinanceException
import os

if __name__ == '__main__':
    env = os.environ
    api = env.get('BINANCE_KEY')
    secret = env.get('BINANCE_SECRET')

    binance = BinanceBot(api, secret)
    try:
        print(binance.rolling_24hr('BTCUSDT'))
    except BinanceException as e:
        print(e)
