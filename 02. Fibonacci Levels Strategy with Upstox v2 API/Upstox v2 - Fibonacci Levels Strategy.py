import requests
import json
import time
from datetime import datetime, timedelta

# Get Authorization Code : https://api.upstox.com/v2/login/authorization/dialog?client_id={Upstox v2 API Key}&redirect_uri={Redirect URL}

# Step 1: Authorization Function to Obtain Access Token
def get_access_token(client_id, client_secret, code, redirect_uri):
    url = "https://api.upstox.com/v2/login/authorization/token"
    payload = f'client_id={API_Key}&client_secret={API_Secret}&code={Authorization_Code}&grant_type=authorization_code&redirect_uri={Redirect_URI}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    response = requests.post(url, headers=headers, data=payload)
    token_data = response.json()
    return token_data.get('access_token')

# Step 2: Get Historical Data Function
def get_historical_data(access_token, instrument_token, from_date, to_date):
    url = f"https://api.upstox.com/v2/historical-candle/NSE_EQ|INE155A01022/day/2024-11-12/2024-11-11" # Change Instrument token & dates as per requirement
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    # print("Historical Data Response:", response.text) # Debug
    return response.json()

# Step 3: Calculate Fibonacci Levels
def calculate_fibonacci_levels(data):
    high_price = max([candle[2] for candle in data])
    low_price = min([candle[3] for candle in data])
    difference = high_price - low_price
    
    levels = {
        '0%': low_price,
        '23.6%': high_price - 0.236 * difference,
        '38.2%': high_price - 0.382 * difference,
        '50%': (high_price + low_price) / 2,
        '61.8%': high_price - 0.618 * difference,
        '100%': high_price
    }
    return levels

# Step 4: Place Order Function
def place_order(access_token, order_payload):
    url = "https://api-hft.upstox.com/v2/order/place"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.post(url, headers=headers, json=order_payload)
    # print("Order Placement Response:", response.text)  # Debug
    return response.json()

# Step 5: Main Strategy Logic
def run_strategy(access_token):
    instrument_token = "NSE_EQ|INE155A01022"  # Upstox v2 Instrument token for Tata Motors Limited
    past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    
    while True:
        historical_data = get_historical_data(access_token, instrument_token, past_date, today)
        
        if historical_data['status'] == 'success':
            candles = historical_data['data']['candles']
            
            fib_levels = calculate_fibonacci_levels(candles)
            print("Fibonacci Levels:", fib_levels)
            
            current_price = candles[-1][4]
            
            if current_price > fib_levels['61.8%']:
                print("Price is above 61.8% level, consider a BUY order.")
                order_payload = {
                    "quantity": 1,
                    "product": "D",
                    "validity": "DAY",
                    "price": 0,
                    "tag": "golden_ratio_strategy",
                    "instrument_token": instrument_token,
                    "order_type": "MARKET",
                    "transaction_type": "BUY",
                    "disclosed_quantity": 0,
                    "trigger_price": 0,
                    "is_amo": False
                }
                order_response = place_order(access_token, order_payload)
                print("Order Response:\n", order_response)
                break
            else:
                print("No trading action taken.\n")
        else:
            print("Failed to retrieve historical data.\n")
        
        time.sleep(5)

# Replace with your actual credentials
CLIENT_ID = "api_key_here"
CLIENT_SECRET = "api_secret_here"
CODE = "authorization_code_here"
REDIRECT_URI = "redirect_uri(same as the one in your upstox app)"

# Get access token
access_token = get_access_token(CLIENT_ID, CLIENT_SECRET, CODE, REDIRECT_URI)

# Run the strategy
if access_token:
    run_strategy(access_token)
else:
    print("Failed to get access token.\n")
