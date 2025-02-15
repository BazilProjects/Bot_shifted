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

    if higher_highs > 2:
        market_bias = "Bullish"
    elif lower_lows > 2:
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
    for idx, low, high in fvgs[-8:]:  # Get the last six FVGs
        relevant_fvg_ranges.append((low, high))
    
    for idx, low, high in order_blocks[-8:]:  # Get the last six Order Blocks
        relevant_ob_ranges.append((low, high))

    # Check if the last close is in any FVG or OB
    for low, high in relevant_fvg_ranges:
        if low <= last_close <= high:
            return "FVG"

    for low, high in relevant_ob_ranges:
        if low <= last_close <= high:
            return "Order Block"

    return None

"""
# Check if Last Close is in Two Relevant FVGs or Order Blocks
def check_last_close_two(data, fvgs, order_blocks):
    '''
    Check if the last closing price is within the ranges of any two FVGs or any two Order Blocks.

    Args:
        data (pd.DataFrame): A DataFrame containing the 'close' price series.
        fvgs (list of tuples): List of tuples representing FVGs in the format (idx, low, high).
        order_blocks (list of tuples): List of tuples representing Order Blocks in the format (idx, low, high).

    Returns:
        str: "Two FVGs" if the last close is in any two FVG ranges,
             "Two Order Blocks" if the last close is in any two OB ranges,
             None if no overlap is found.
    '''
    # Get the last closing price
    last_close = data['close'].iloc[-1]

    # Collect the ranges of the last 8 FVGs and Order Blocks
    relevant_fvg_ranges = [(low, high) for idx, low, high in fvgs[-8:]]
    relevant_ob_ranges = [(low, high) for idx, low, high in order_blocks[-8:]]

    # Check if the last close is within two FVG ranges
    fvg_count = sum(1 for low, high in relevant_fvg_ranges if low <= last_close <= high)
    if fvg_count >= 2:
        return "Two FVGs"

    # Check if the last close is within two Order Block ranges
    ob_count = sum(1 for low, high in relevant_ob_ranges if low <= last_close <= high)
    if ob_count >= 2:
        return "Two Order Blocks"

    # If not found in any two ranges, return None
    return None
"""
def check_current_flow_direction(df, tail_no=8):
    # Check the last 4 candles
    last_4 = df.tail(tail_no)

    # Determine buy and sell candles
    last_4['candle_type'] = last_4.apply(lambda row: 'buy' if row['close'] > row['open'] else 'sell', axis=1)

    # Count the number of buy and sell candles
    buy_count = (last_4['candle_type'] == 'buy').sum()
    sell_count = (last_4['candle_type'] == 'sell').sum()

    # Determine the majority
    if buy_count > sell_count:
        result = "SELL"
    elif sell_count > buy_count:
        result = "BUY"
    else:
        result =None

    return result
# Place Buy Order
def place_buy_order(df,market_bias, condition, decision):
    #choice=check_current_flow_direction(df)
    #print(choice)
    if market_bias in ["Bullish"] and condition and decision=='LOW':
        print(f"Placing a buy order. Condition: {condition}, Market Bias: {market_bias}")
        return 'BUY'
    elif market_bias in ["Bearish"] and condition and decision=='HIGH':
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


token = os.getenv('TOKEN') or 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiJlNWZkNGRkYWZmZmIyMDk2YTAyMWYzNjZiY2YxYjYwYSIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZXN0LWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1ycGMtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTp3czpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoicmlzay1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsicmlzay1tYW5hZ2VtZW50LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJjb3B5ZmFjdG9yeS1hcGkiLCJtZXRob2RzIjpbImNvcHlmYWN0b3J5LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtdC1tYW5hZ2VyLWFwaSIsIm1ldGhvZHMiOlsibXQtbWFuYWdlci1hcGk6cmVzdDpkZWFsaW5nOio6KiIsIm10LW1hbmFnZXItYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6ImJpbGxpbmctYXBpIiwibWV0aG9kcyI6WyJiaWxsaW5nLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19XSwiaWdub3JlUmF0ZUxpbWl0cyI6ZmFsc2UsInRva2VuSWQiOiIyMDIxMDIxMyIsImltcGVyc29uYXRlZCI6ZmFsc2UsInJlYWxVc2VySWQiOiJlNWZkNGRkYWZmZmIyMDk2YTAyMWYzNjZiY2YxYjYwYSIsImlhdCI6MTczOTYwNzMyOH0.QIqiiv4k-8gcgVSjDsQtKGFHMCPI77VNM2gxsOEAvuX-pZDW4SZNa_X7PXS2nxscWs_9gKHZWqyB1CUsWbu9Lhc6UJUROM_0tdkNPlaVZFrOS6fXwuAiVTaEG7WhCC5pH-3Vi8RwND4fN78Dk2NM1eMwbyvbv__JjLqsiTltwyDJHvbXAko29CIp9LX0MlCvsxpLP-TOnAYZWxvYeXGTTN7SADRfNq5uD7-WQE_oR3AOKEY3KmDdn7SIQryRVqGX_jzg3h3_WVJ_3EckP7uA6krZCPmiAj6oUX2QeWesE4w7RfBR1ekwVmm0QBlY6IiArV5w_4W20xBgr95b8NkRDZm78bwB-Sznzt7nfGN2lYz50TAXGSaMmaUkrlC4iKOYncsWyxtE8EqbGAiCBY_11s-JTuwCzXQ--KeUdt63JwvVosgZNb2Wa9qyckItKpHDtfI_ydWZ3L23RQJrEyiKGpKanDue0FEaL8R5-HRgdEg4l1AnHVbF80ZANY6hwMKMEOGS1fF_u8nhuvOufbq-Q6rCazb0HCdkbX3mahUQ5tlI2vvXkjeQwv-uiu_Ch5wLcLrNTXApIgyZff6xUQeCLT6eBihYa6VF6dvwWFKD-YxF8geK7QVglIYPqpCpKehmFs0GsDW59qRkQnbkdAnUHEcfY5jTX1npEPFNLftiluw'
accountId = os.getenv('ACCOUNT_ID') or '888683f3-579e-4ae0-8822-15afdb34d877'

# Constants
symbol='Step Index'
timeframe='15m'




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
            candles_5m = await account.get_historical_candles(symbol=symbol, timeframe='5m', start_time=None, limit=50)
            print('Fetched the latest candle data successfully')
        except Exception as e:
            raise e
        try:
            if not isinstance(candles, str):
                df=pd.DataFrame(candles)
                df_3=pd.DataFrame(candles_5m)
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
            decision = prepare(df_3)
            print("Decision:", decision)

            market_bias = analyze_bias(df)
            print("Market Bias:", market_bias)

            fvgs = detect_fvgs(df, market_bias)
            print("Fair Value Gaps (FVGs):", fvgs)

            order_blocks = detect_order_blocks(df, market_bias)
            print("Order Blocks:", order_blocks)

            condition = check_last_close(df2, fvgs, order_blocks)
            print("Condition:", condition)


            place_buy_orders=place_buy_order(df,market_bias, condition, decision)

            if place_buy_orders=='SELL':
                stop_loss=current_market_price+5
                take_profit=current_market_price-10
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
                stop_loss=current_market_price-5
                take_profit=current_market_price+10
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

        print('*'*20)
        print('*'*20)
        print('*'*20)
    except Exception as e:
        raise e
        print(f"An error occurred: {e}")
def main():
    asyncio.run(main2())