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


def get_trades_in_usdt(bot, ticker):
    try:
        # Tickers the argument ticker trades against
        against_tickers = ['USDT', 'BTC', 'BNB']
        spot_trades = bot.spot_trades(ticker, against_tickers=against_tickers)
        margin_trades = bot.margin_trades(ticker, against_tickers=against_tickers)

        # All trades
        all_trades = []

        # Convert prices and commissions to USDT
        for account in [spot_trades, margin_trades]:
            # Check against each coin
            for coin in account:
                coin_trades = account[coin]
                # Skip USDT since no conversion needed
                for trade in coin_trades:
                    timestamp = int(trade['time'])
                    commission_asset = trade['commissionAsset']
                    
                    # No need to convert USDT
                    if coin != 'USDT':
                        # Get coin price in USDT at time of trade.
                        # This is an approximation, the opening price within a minute of the trade
                        usdt_price_at_trade = float(bot.price_at_time(f'{coin}USDT', timestamp)[0][1])
                        # Convert to USDT
                        trade['price'] = float(trade['price']) * usdt_price_at_trade
                    if commission_asset != 'USDT':
                        # Get commission asset price in USDT at time of trade.
                        # This is an approximation, the opening price within a minute of the trade
                        usdt_price_at_trade = float(bot.price_at_time(f'{commission_asset}USDT', timestamp)[0][1])
                        # Convert to USDT
                        trade['commission'] = float(trade['commission']) * usdt_price_at_trade
                    
                # Add to all_trades now that it is in USDT
                all_trades.extend(coin_trades)
        
        return all_trades
        
    except BinanceException as e:
        print(e)


def coin_position(bot, ticker):
    try:
        # Current price of ticker in USDT
        current_price_usdt = bot.price(f'{ticker}USDT')
        # Get all trades
        trades = get_trades_in_usdt(bot, ticker)
        
        # Capital gains (USDT), Amount of coin held, total commission fees
        gains, coin_balance, fees = 0,0,0

        # Sort trades from earliest to latest
        trades.sort(key=lambda x: x['time'])

        for trade in trades:
            price = float(trade['price'])
            qty = float(trade['qty'])
            is_buy = trade['isBuyer']
            time = int(trade['time'])
            commission = float(trade['commission'])
            action = 'BUY' if is_buy else 'SELL'
            # Direction to move position
            direction = 1 if is_buy else -1

            # Print trade
            print(f'{action.ljust(4)} {str(qty).zfill(5)} ADA at {price:,.4f} USDT')

            # Change to portfolio (USDT)
            change = qty * (current_price_usdt - price)
            gains += direction * change
            coin_balance += direction * qty
            gains -= commission
        
        print(f"\n\nGains: ${gains}")
        print(f"HOLDING: {coin_balance} {ticker} ({current_price_usdt * coin_balance:.2f} USDT)")
        print(f"1 {ticker} = {current_price_usdt:.3f} USDT")  

    
    except BinanceException as e:
        print(e)



if __name__ == '__main__':
    bot = connect()

    coin_position(bot, 'ADA')

