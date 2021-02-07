"""Uses BinanceBot to analyze positions"""

from binance_bot import BinanceBot, BinanceException
import pprint
import os

# Global vars
env = os.environ
pp = pprint.PrettyPrinter(indent=4)


def connect() -> BinanceBot:
    """Returns an authorized instance of BinanceBot"""
    api = env.get('BINANCE_KEY')
    secret = env.get('BINANCE_SECRET')
    return BinanceBot(api, secret)


def coin_position(bot, ticker):
    try:
        # current price for the coin
        current_price_usdt = bot.price(f'{ticker}USDT')

        # coins traded against
        against_tickers = ['USDT', 'BTC', 'BNB']

        # get all trades
        all_trades = bot.trades(ticker, against_tickers)

        # USDT trades
        usdt_trades = all_trades['USDT']

        # Convert traded against coins to equiv. USDT value at time of trade
        for coin in all_trades:
            # skip USDT since no conversion required
            if coin == 'USDT':
                continue

            # Get all trades for the coin
            coin_trades = all_trades[coin]

            # Convert to USDT open at candle within one minute of the transaction time.
            # NOTE: this means that the price will be an approximation, not 100% accurate.
            for trade in coin_trades:
                timestamp = int(trade['time'])
                historical_price = float(bot.price_at_time(f'{coin}USDT', timestamp)[0][1])
                trade['price'] = float(trade['price']) * historical_price
            
            # Add to USDT trades once prices have been converted
            usdt_trades.extend(all_trades[coin])

        # Profit/Loss (realized + unrealized) in USDT.
        gains = 0
        # Amount of ticker in balance.
        ticker_amount = 0

        # Sort by transaction time (earliest to latest)
        usdt_trades.sort(key=lambda x: x['time'])

        for trade in usdt_trades:
            price = float(trade['price'])
            qty = float(trade['qty'])
            is_buy = trade['isBuyer']
            time = int(trade['time'])
            action = 'Bought' if is_buy else 'Sold'

            # offset for Binance error
            # if qty == 175 and not is_buy:
            #     qty = 86

            print(f'{action.ljust(7)} {qty:6,.2f} ADA at {price:,.4f} USDT')

            # Change to portfolio
            change = qty * (current_price_usdt - price)

            # Add if buy, subtract if sell
            gains = gains + change if is_buy else gains - change
            ticker_amount = ticker_amount + qty if is_buy else ticker_amount - qty
        
        print(f"\n\nGains: ${gains}")
        print(f"HOLDING: {ticker_amount} ADA ({current_price_usdt * ticker_amount:.2f} USDT)")
        print(f"1 ADA = {current_price_usdt:.3f} USDT")     

    except BinanceException as e:
        print(e)



if __name__ == '__main__':
    bot = connect()

    coin_position(bot, 'ADA')
