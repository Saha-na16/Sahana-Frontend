from flask import Flask, jsonify, request
import requests
import threading

# Initialize Flask app
app = Flask(__name__)

# Configuration
WINDOW_SIZE = 10
TIMEOUT = 0.5  # 500 milliseconds
third_party_url = 'http://example.com/api/numbers/'  # Placeholder for third-party server URL

# Store numbers and window state
data_store = []
lock = threading.Lock()

# Simulate the third-party server response
def fetch_numbers(number_id):
    # Simulate numbers based on number_id (mocked response)
    if number_id == 'p':  # Prime numbers
        return [1, 3, 5, 7]
    elif number_id == 'f':  # Fibonacci numbers
        return [1, 2, 3, 5]
    elif number_id == 'e':  # Even numbers
        return [2, 4, 6, 8]
    elif number_id == 'r':  # Random numbers
        return [1, 3, 5, 7]
    return []

# Update the data store
def update_window(new_numbers):
    with lock:
        # Remove duplicates and limit size
        for num in new_numbers:
            if num not in data_store:
                data_store.append(num)
                if len(data_store) > WINDOW_SIZE:
                    data_store.pop(0)

# Calculate average
def calculate_average():
    if len(data_store) == 0:
        return 0.0
    return round(sum(data_store) / len(data_store), 2)

# Route to handle number requests and calculate the average
@app.route('/numbers/<number_id>', methods=['GET'])
def get_average(number_id):
    print(f"🔍 Request received for ID: {number_id}")

    # Validating number_id
    if number_id not in ['p', 'f', 'e', 'r']:
        print(f"🚫 Invalid ID: {number_id}")
        return jsonify({'error': 'Invalid number ID'}), 400

    # Fetch new numbers from third-party server (mocked response)
    prev_state = data_store.copy()
    new_numbers = fetch_numbers(number_id)
    if not new_numbers:
        print(f"⚠ No new numbers received for ID: {number_id}")

    # Update the data store and calculate the average
    update_window(new_numbers)
    curr_state = data_store.copy()
    avg = calculate_average()

    # Log the current state and average
    print(f"📊 Updated Window: {curr_state}")
    print(f"📈 Average Calculated: {avg}")

    # Return the response with window state and average
    return jsonify({
        'windowPrevState': prev_state,
        'windowCurrState': curr_state,
        'numbers': new_numbers,
        'avg': avg
    })

# Log all registered routes on startup
@app.before_request
def log_registered_routes():
    print("🔍 Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(rule)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
