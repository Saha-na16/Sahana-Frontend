from flask import Flask, jsonify, request
import requests
import time
import threading

# Initialize Flask app
app = Flask(__name__)

# Configuration
CACHE_EXPIRY_TIME = 60  # Cache stock prices for 1 minute
THIRD_PARTY_API_URL = 'https://api.coingecko.com/api/v3/simple/price'  # Example: Using CoinGecko for crypto prices (for stock API, you can use Alpha Vantage or Yahoo Finance)
CACHE = {}
CACHE_LOCK = threading.Lock()

# Function to fetch stock prices from a third-party API
def fetch_stock_price(symbol):
    try:
        # Example request for cryptocurrency prices (for stock use Alpha Vantage or Yahoo Finance API)
        response = requests.get(THIRD_PARTY_API_URL, params={'ids': symbol, 'vs_currencies': 'usd'})
        if response.status_code == 200:
            return response.json().get(symbol, {}).get('usd', None)
        return None
    except requests.RequestException as e:
        print(f"Error fetching stock price for {symbol}: {e}")
        return None

# Function to update stock prices in the cache
def update_stock_cache(symbol, price):
    with CACHE_LOCK:
        CACHE[symbol] = {'price': price, 'timestamp': time.time()}

# Route to fetch aggregated stock prices
@app.route('/stock/price', methods=['GET'])
def get_stock_price():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({'error': 'Symbol is required'}), 400

    with CACHE_LOCK:
        if symbol in CACHE:
            cached_data = CACHE[symbol]
            if time.time() - cached_data['timestamp'] < CACHE_EXPIRY_TIME:
                return jsonify({
                    'symbol': symbol,
                    'price': cached_data['price'],
                    'cached': True
                })
    
    # If data is not in cache or cache expired, fetch new price
    price = fetch_stock_price(symbol)
    if price is None:
        return jsonify({'error': 'Unable to fetch stock price'}), 500
    
    # Update cache with the fetched price
    update_stock_cache(symbol, price)

    return jsonify({
        'symbol': symbol,
        'price': price,
        'cached': False
    })

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
