from urllib.parse import urlencode
import requests
import hashlib # SHA-256 encryption for HMAC signing
import hmac # HMAC keyed hashing
import os

# Custom Exception class for Binance related errors
class BinanceException(Exception):
    """
    Wrapper class for base Exception class.

    """
    pass


class BinanceBot:
    """
    Class to interact with Binance API.

    The BinanceBot class interacts with the Binance API to retrieve market 
    and user data.

    Attributes:
        BASE (`str`): The base endpoint prefix for all Binance API calls.

    """

    BASE = 'https://api.binance.com'

    # Initializes a bot with the API keys
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
    

    def __signed_request(self, url, additional_params={}, err_msg="Error") -> dict:
        """
        HMAC SHA-256 GET request.

        Attempts a HMAC (SHA-256) signed GET request using the API key and secret key.
        This type of request is used when accessing reserved information (e.g. user trades).

        Args:
            url (`str`): The API endpoint for the request.
            additional_params (`dict`, optional): A dictionary of any other parameters the request might take. Defaults to an emtpy dictionary.
            err_msg (`str`): The error message prefix for the BinanceException error message.
        
        Returns:
            `dict`: The JSON result of the GET request.
        
        Raises:
            BinanceException: If the request is malformed or incorrect.

        """
        # Make an HMAC signed GET request using the API and secret keys.
        # Used when accessing private user data.

        # pre-requisite timestamp
        timestamp = int(requests.get(f'{self.BASE}/api/v1/time').json()['serverTime'])

        # Prepare request parameters
        params = {'timestamp': timestamp}
        # Add any additional parameters
        params.update(additional_params)

        # HMAC signed with SHA-256 encryption using secret key
        hashed = hmac.new(
            self.secret_key.encode('UTF-8'),
            urlencode(params).encode('UTF-8'),
            hashlib.sha256
        ).hexdigest()

        # Add hashed signature to request parameters
        params['signature'] = hashed

        # Add  API key to headers
        headers = {'X-MBX-APIKEY': self.api_key}

        # Create GET request with params and headers
        response = requests.get(
            url,
            params=params,
            headers=headers
        ).json()

        # Throw BinanceException if returned JSON is an error code.
        if 'code' in response:
            raise BinanceException(f"{err_msg}: code {response['code']}: {response['msg']}")
        else:
            return response

    
    def __unsigned_request(self, url, additional_params={}, err_msg="Error"):
        """
        Non-signed GET request.

        Attempts a regular GET request to the specified endpoint with the specified parameters.

        Args:
            url (`str`): The API endpoint for the request.
            additional_params (`dict`, optional): A dictionary of any other parameters the request might take. Defaults to an emtpy dictionary.
            err_msg (`str`): The error message prefix for the BinanceException error message.
        
        Returns:
            `dict`: The JSON result of the GET request.
        
        Raises:
            BinanceException: If the request is malformed or incorrect.

        """

        response = requests.get(url, params=additional_params).json()
    
        # Throw BinanceException if returned JSON is an error code.
        if 'code' in response:
            raise BinanceException(f"{err_msg}: code {response['code']}: {response['msg']}")
        else:
            return response


    def rolling_24hr(self, ticker) -> dict:
        """
        Gets the rolling 24 hour statistics for a ticker.

        Args:
            ticker (`str`) -- the currency pair.
        
        Returns:
            `dict`: The JSON result of the GET request.
        
        Raises:
            BinanceException: If the request is malformed or incorrect.

        """

        url = f'{self.BASE}/api/v3/ticker/24hr'
        params = {'symbol': ticker}

        return self.__unsigned_request(url, params=params, err_msg="Error on rolling_24hr()")

    
    def price(self, ticker=None) -> float:
        """
        Current market price.

        Gets the current market price for a given ticker, or for all tickers if no ticker is specified.

        Args:
            ticker (`str`, optional) -- the currency pair. Defaults to None.
        
        Returns:
            `float`: The price of the ticker.
        
        Raises:
            BinanceException: If the request is malformed or incorrect.

        """

        url = f'{self.BASE}/api/v3/ticker/price'
        err_msg = "Error on latest_price()"
        # Add params if ticker provided
        kwargs = dict(additional_params={'symbol': ticker}) if ticker is not None else dict()

        return float(self.__unsigned_request(url, err_msg=err_msg, **kwargs)['price'])
    

    def price_at_time(self, ticker, time) -> float:
        url = f'{self.BASE}/api/v3/klines'
        half_minute = 30 * 1000
        params = {
            'symbol': ticker,
            'interval': '1m',
            'startTime': time - half_minute,
            'endTime': time + half_minute
        }
        err_msg = f"Error getting historical price for {ticker}"

        return (self.__unsigned_request(url, additional_params=params, err_msg=err_msg))
    

    def trades(self, ticker, against_tickers=['USDT', 'BTC', 'BNB']) -> dict:
        """
        All trades for a given ticker.

        Gets all trades for the given ticker, against a list of other tickers.

        Args:
            ticker (`str`) -- the currency.
            against_tickers (list: `str`) -- A list of tickers to get trades for the ticker against.
                Defaults to ['USDT', 'BTC', 'BNB'].
        
        Returns:
            `dict`: A dictionary containing JSON results of the GET requests for each currency.
        
        Raises:
            BinanceException: If the request is malformed or incorrect.

        """
        url = f'{self.BASE}/api/v3/myTrades'
        err_msg = f"Error fetching trades on {ticker}."

        # Holds trades for ticker against all `against_tickers`
        all_trades = {}

        for against_ticker in against_tickers:
            # skip if coin is the same
            if against_ticker == ticker:
                continue
            params = {'symbol': f'{ticker}{against_ticker}'}
            all_trades[against_ticker] = self.__signed_request(url, additional_params=params, err_msg=err_msg)

        return all_trades