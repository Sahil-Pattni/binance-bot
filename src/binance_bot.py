from urllib.parse import urlencode
import requests
import hashlib # SHA-256 encryption for HMAC signing
import hmac # HMAC keyed hashing
import os

# Custom Exception class for Binance related errors
class BinanceException(Exception):
    pass


class BinanceBot:
    # Base url for API
    BASE = 'https://api.binance.com'

    # Initializes a bot with the API keys
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
    

    def __signed_request(self, url, additional_params={}) -> dict:
        # Generate an HMAC signed request using the API and secret keys.
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
        headers = {'X-MBX-APIKEY'}

        # Create GET request with params and headers and return resulting JSON
        return requests.get(
            url,
            params=params,
            headers=headers
        ).json()

    
    def __unsigned_request(self, url, params=None, err_msg="Error"):
        # Attempts to make a GET request with the given url and request parameters.

        if params is not None:
            response = requests.get(url, params=params).json()
        else:
            response = requests.get(url).json()
        
        # Throw BinanceException if returned JSON is an error code.
        if 'code' in response:
            raise BinanceException(f"{err_msg}: code {response['code']}: {response['msg']}")

        return response


    def rolling_24hr(self, ticker) -> dict:
        # Gets the rolling 24 hour statistics for a ticker

        url = f'{self.BASE}/api/v3/ticker/24hr'
        params = {'symbol': ticker}

        return self.__unsigned_request(url, params=params, err_msg="Error on rolling_24hr()")

    
    def price(self, ticker=None) -> dict:
        # Gets the current market price for a given ticker, 
        # or for all tickers if no ticker is specified

        url = f'{self.BASE}/api/v3/ticker/price'
        err_msg = "Error on latest_price()"
        # Add params if ticker provided
        kwargs = dict(params={'symbol': ticker}) if ticker is not None else dict()

        return self.__unsigned_request(url, err_msg=err_msg, **kwargs)



