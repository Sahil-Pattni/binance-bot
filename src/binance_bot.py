from urllib import urlencode
import requests
import hashlib # SHA-256 encryption for HMAC signing
import hmac # HMAC keyed hashing

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
        timestamp = int(requests.get(f'{BASE}/api/v1/time').json()['serverTime'])

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
    

    def rolling_24hr(self, ticker_pair) -> dict:
        # Gets the rolling 24 hour statistics for a ticker

        url = f'{BASE}/api/v3/ticker/24h'
        params = {'symbol': ticker_pair}

        # Make request
        response = requests.get(url, params=params).json()

        # If error in response, throw BinanceException
        if 'code' in response:
            raise BinanceException(f"Error in pct_change():\n{response['code']}: {response['msg']}")

        # If no errors present, return JSON
        return response
    