import pandas as pd



# Fractal High/Low Detection Function
def calculate_fractals(df, window=2):
    df['fractal_high'] = None
    df['fractal_low'] = None

    for i in range(window, len(df) - window):
        # Fractal High
        if all(df['high'][i] > df['high'][i - j] for j in range(1, window + 1)) and \
           all(df['high'][i] > df['high'][i + j] for j in range(1, window + 1)):
            df.at[df.index[i], 'fractal_high'] = df['high'][i]

        # Fractal Low
        if all(df['low'][i] < df['low'][i - j] for j in range(1, window + 1)) and \
           all(df['low'][i] < df['low'][i + j] for j in range(1, window + 1)):
            df.at[df.index[i], 'fractal_low'] = df['low'][i]

    return df

import pandas as pd
import plotly.graph_objects as go

# Load CSV data
def load_data(file_path):
    data = pd.read_csv(file_path)
    data = data.head(600)
    data['time'] = pd.to_datetime(data['time'])  # Ensure the time column is in datetime format
    return data

# Analyze Market Bias
def analyze_bias(data):
    higher_highs = 0
    lower_lows = 0
    market_bias = ""

    for i in range(3, len(data) - 3):
        if (data['high'][i] > data['high'][i - 1] and
            data['high'][i] > data['high'][i - 2] and
            data['high'][i] > data['high'][i - 3] and
            data['high'][i] > data['high'][i + 1] and
            data['high'][i] > data['high'][i + 2] and
            data['high'][i] > data['high'][i + 3]):
            higher_highs += 1

        if (data['low'][i] < data['low'][i - 1] and
            data['low'][i] < data['low'][i - 2] and
            data['low'][i] < data['low'][i - 3] and
            data['low'][i] < data['low'][i + 1] and
            data['low'][i] < data['low'][i + 2] and
            data['low'][i] < data['low'][i + 3]):
            lower_lows += 1

    if higher_highs > 3:
        market_bias = "Bullish"
    elif lower_lows > 3:
        market_bias = "Bearish"
    else:
        market_bias = "Ranging"

    return market_bias

# Detect FVGs
def detect_fvgs(data, market_bias):
    fvg_ranges = []
    for i in range(2, len(data) - 1):
        if market_bias == "Bullish":
            if data['low'][i + 1] > data['high'][i - 1]:
                fvg_ranges.append((i - 1, data['high'][i - 1], data['low'][i + 1]))
        elif market_bias == "Bearish":
            if data['high'][i + 1] < data['low'][i - 1]:
                fvg_ranges.append((i - 1, data['low'][i - 1], data['high'][i + 1]))
    return fvg_ranges

# Detect Order Blocks
def detect_order_blocks(data, market_bias):
    order_blocks = []
    for i in range(1, len(data) - 3):
        price_change = (data['high'][i + 3] - data['low'][i]) / (data['high'][i] - data['low'][i])
        if market_bias == "Bullish" and price_change > 1.0 and data['close'][i - 1] < data['open'][i - 1]:
            order_blocks.append((i - 1, data['high'][i], data['low'][i]))
        elif market_bias == "Bearish" and price_change > 1.0 and data['close'][i - 1] > data['open'][i - 1]:
            order_blocks.append((i - 1, data['low'][i], data['high'][i]))
    return order_blocks

# Check if Last Close is in Current or Previous Relevant Range
def check_last_close(data, fvgs, order_blocks):
    last_close = data['close'].iloc[-1]
    relevant_fvg_ranges = []
    relevant_ob_ranges = []

    # Collect ranges for the last FVGs and order blocks
    for idx, low, high in fvgs[-6:]:  # Get the last six FVGs
        relevant_fvg_ranges.append((low, high))
    
    for idx, low, high in order_blocks[-6:]:  # Get the last six Order Blocks
        relevant_ob_ranges.append((low, high))

    # Check if the last close is in any FVG or OB
    for low, high in relevant_fvg_ranges:
        if low <= last_close <= high:
            return "FVG"

    for low, high in relevant_ob_ranges:
        if low <= last_close <= high:
            return "Order Block"

    return None

# Place Buy Order
def place_buy_order(market_bias, condition, decision):
    if decision!=None:
        if market_bias in ["Bullish", "Ranging"] and condition :#and decision== 'LOW':
            print(f"Placing a buy order. Condition: {condition}, Market Bias: {market_bias}")
            return 'BUY'
        elif market_bias in ["Bearish", "Ranging"] and condition:# and decision == 'HIGH':
            print(f"Condition: {condition}, Market Bias: {market_bias}")
            return 'SELL'
    else:
        return None

def prepare(df):
    # Apply fractal calculation
    df = calculate_fractals(df, window=2)
    # Check the third last row
    third_last_row = df.iloc[-3]

    # Determine if it's a fractal high, fractal low, or none
    if not pd.isna(third_last_row['fractal_high']) and third_last_row['fractal_high'] != 0:
        return 'HIGH'
    elif not pd.isna(third_last_row['fractal_low']) and third_last_row['fractal_low'] != 0:
        return 'LOW'
    else:
        return None
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
from itertools import combinations
from metaapi_cloud_sdk import MetaApi
import asyncio
import os
import websocket
import json
import time
from datetime import datetime, timedelta
import joblib


ema_length=10
macd_fast=12
macd_slow=26
macd_signal=9
seq_len=180


token = os.getenv('TOKEN') or 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2YjI0NTQ0ZWYzMWI0NzQ4NWMxNzQ1NmUzNzdmYTlhZiIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZXN0LWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1ycGMtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTp3czpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoicmlzay1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsicmlzay1tYW5hZ2VtZW50LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJjb3B5ZmFjdG9yeS1hcGkiLCJtZXRob2RzIjpbImNvcHlmYWN0b3J5LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtdC1tYW5hZ2VyLWFwaSIsIm1ldGhvZHMiOlsibXQtbWFuYWdlci1hcGk6cmVzdDpkZWFsaW5nOio6KiIsIm10LW1hbmFnZXItYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6ImJpbGxpbmctYXBpIiwibWV0aG9kcyI6WyJiaWxsaW5nLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19XSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaW1wZXJzb25hdGVkIjpmYWxzZSwicmVhbFVzZXJJZCI6IjZiMjQ1NDRlZjMxYjQ3NDg1YzE3NDU2ZTM3N2ZhOWFmIiwiaWF0IjoxNzMxODAxNjc3fQ.QDGpGFvszwuNOFS3yHN9V58HDADbYhHUOWWNjbOfUBOIH37U_BiYkBdwGK_pgPpdM-zgLqq3wAIgFx6KqegWW4I_Ro_CDfTEuT3-qFLohSSdqSOddo9qhya8u7U9XM0xHt_R2i9jBAjEi3c51pHnfChPAGpPBI_0CsY6tCXhbQBLDgrqZHLJ4-sLBsgmF0XcnaomtTLBAE7IUWRRoBdRxkUDzSXUVDJeg99cfuDNZGxVqTKfXZdXBIkTzPBGaoABoXwEMEINkYLxsWv4YeTVXQBnDfe4unekHaowFePhUOh9r5bASL9WGr0jZx0ua5MHwb5VdW5gQ22d-YFmmKLKaEPlSawq1ChR8Q6zjAtmoDillwaSXgBvrRdC1b7nCR_aXsFcCbXS1rAkXZBxu8CaNSAA_3SXNiX6n0xeqfaJUgHykh1cNf8q-yCAei_7V5iYMOnj3Vpn9x3B__A-GJxbHUAmF4hzamwyU5s-MtO8P4cJsJWhxrrvsIXwGMlxs2iU2iq3mL3nxQ4imqklB0GsC0soN_y15iTYF7LKz5QT76O_ikbwrpU5goM33eLnQOr482Oqhqi8wZRYkV8XXJSkB-MKoEfyJ-61twJMNB1plioB2WJDquWNoL9Hfl6eeXWZH72SmUxYn6ybAZ8B43_2DqSKU-FFMUcoKyR48zpv70A'
accountId = os.getenv('ACCOUNT_ID') or '3d90c2da-2cb6-4929-b339-2e70820cb975'

# Constants
symbol='Step Index'
timeframe='5m'




async def main2():
    print('Up and runing')
    api = MetaApi(token)
    account = await api.metatrader_account_api.get_account(accountId)
    initial_state = account.state
    deployed_states = ['DEPLOYING', 'DEPLOYED']

    if initial_state not in deployed_states:
        # wait until account is deployed and connected to broker
        print('Deploying account')
        await account.deploy()
        print('Waiting for API server to connect to broker (may take a few minutes)')
        await account.wait_connected()
    # Connect to MetaApi API
    connection = account.get_rpc_connection()
    await connection.connect()

    # Wait until terminal state synchronized to the local state
    print('Waiting for SDK to synchronize to terminal state (may take some time depending on your history size)')
    await connection.wait_synchronized()

    try:
        try:
            # Fetch historical price data
            candles = await account.get_historical_candles(symbol=symbol, timeframe=timeframe, start_time=None, limit=50)
            print('Fetched the latest candle data successfully')
        except Exception as e:
            raise e
        try:
            if not isinstance(candles, str):
                df=pd.DataFrame(candles)
            else:
                
                df=pd.DataFrame()
                
        except Exception as e:
            raise e

        if not df.empty:
            prices = await connection.get_symbol_price(symbol)
            #print(prices)
            # Extract bid and ask prices
            bid_price =float(prices['bid'])
            ask_price = float(prices['ask'])
            current_market_price=((bid_price+ask_price)/2)
            current_open=current_market_price
            # Example Code
            df2=df
            decision = prepare(df)
            print("Decision:", decision)

            market_bias = analyze_bias(df)
            print("Market Bias:", market_bias)

            fvgs = detect_fvgs(df, market_bias)
            print("Fair Value Gaps (FVGs):", fvgs)

            order_blocks = detect_order_blocks(df, market_bias)
            print("Order Blocks:", order_blocks)

            condition = check_last_close(df2, fvgs, order_blocks)
            print("Condition:", condition)

            if condition is not None :#and decision is not None:
                place_buy_orders=place_buy_order(market_bias, condition, decision)

                if place_buy_orders=='SELL':
                    stop_loss=current_market_price+3
                    take_profit=current_market_price-6
                    try:
                        
                        result = await connection.create_market_sell_order(
                            symbol=symbol,
                            volume=0.1,
                            stop_loss=stop_loss,
                            take_profit=take_profit,
                        )
                        print(f'Sell_Signal (T)   :Sell Trade successful For Symbol :{symbol}')
                        
                        Trader_success=True
                    except Exception as err:
                        print('Trade failed with error:')
                        print(api.format_error(err))

                
                if  place_buy_orders =='BUY':
                    stop_loss=current_market_price-3
                    take_profit=current_market_price+6
                    try:
                        result = await connection.create_market_buy_order(
                            symbol=symbol,
                            volume=0.1,
                            stop_loss=stop_loss,
                            take_profit=take_profit,
                        )
                        print(f'Buy_Signal (T)   :Buy Trade successful For Symbol :{symbol}')
                        
                        Trader_success=True
                    except Exception as err:
                        print('Trade failed with error:')
                        print(api.format_error(err))
                else:
                    print('Trade Not possible')
            else:
                print('One of the Two Condition and Decision is None')
                
        print('*'*20)
        print('*'*20)
        print('*'*20)
    except Exception as e:
        raise e
        print(f"An error occurred: {e}")
#def main():
asyncio.run(main2())