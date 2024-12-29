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


import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
from itertools import combinations
from metaapi_cloud_sdk import MetaApi
import asyncio
import pickle
import os
import websocket
import json
import time
from datetime import datetime, timedelta
from tensorflow.keras.models import load_model
import joblib
# Load the scalers
scaler_X = joblib.load('scaler_X.pkl')
scaler_y = joblib.load('scaler_y.pkl')

print("Scalers loaded successfully.")


ema_length=10
macd_fast=12
macd_slow=26
macd_signal=9

# Load the model in .keras format
model = load_model("my_model.keras")
print("Model loaded successfully.")



token = os.getenv('TOKEN') or 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2YjI0NTQ0ZWYzMWI0NzQ4NWMxNzQ1NmUzNzdmYTlhZiIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZXN0LWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1ycGMtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTp3czpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoicmlzay1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsicmlzay1tYW5hZ2VtZW50LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJjb3B5ZmFjdG9yeS1hcGkiLCJtZXRob2RzIjpbImNvcHlmYWN0b3J5LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtdC1tYW5hZ2VyLWFwaSIsIm1ldGhvZHMiOlsibXQtbWFuYWdlci1hcGk6cmVzdDpkZWFsaW5nOio6KiIsIm10LW1hbmFnZXItYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6ImJpbGxpbmctYXBpIiwibWV0aG9kcyI6WyJiaWxsaW5nLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19XSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaW1wZXJzb25hdGVkIjpmYWxzZSwicmVhbFVzZXJJZCI6IjZiMjQ1NDRlZjMxYjQ3NDg1YzE3NDU2ZTM3N2ZhOWFmIiwiaWF0IjoxNzMxODAxNjc3fQ.QDGpGFvszwuNOFS3yHN9V58HDADbYhHUOWWNjbOfUBOIH37U_BiYkBdwGK_pgPpdM-zgLqq3wAIgFx6KqegWW4I_Ro_CDfTEuT3-qFLohSSdqSOddo9qhya8u7U9XM0xHt_R2i9jBAjEi3c51pHnfChPAGpPBI_0CsY6tCXhbQBLDgrqZHLJ4-sLBsgmF0XcnaomtTLBAE7IUWRRoBdRxkUDzSXUVDJeg99cfuDNZGxVqTKfXZdXBIkTzPBGaoABoXwEMEINkYLxsWv4YeTVXQBnDfe4unekHaowFePhUOh9r5bASL9WGr0jZx0ua5MHwb5VdW5gQ22d-YFmmKLKaEPlSawq1ChR8Q6zjAtmoDillwaSXgBvrRdC1b7nCR_aXsFcCbXS1rAkXZBxu8CaNSAA_3SXNiX6n0xeqfaJUgHykh1cNf8q-yCAei_7V5iYMOnj3Vpn9x3B__A-GJxbHUAmF4hzamwyU5s-MtO8P4cJsJWhxrrvsIXwGMlxs2iU2iq3mL3nxQ4imqklB0GsC0soN_y15iTYF7LKz5QT76O_ikbwrpU5goM33eLnQOr482Oqhqi8wZRYkV8XXJSkB-MKoEfyJ-61twJMNB1plioB2WJDquWNoL9Hfl6eeXWZH72SmUxYn6ybAZ8B43_2DqSKU-FFMUcoKyR48zpv70A'
accountId = os.getenv('ACCOUNT_ID') or '3d90c2da-2cb6-4929-b339-2e70820cb975'

# Constants
symbol='Step Index'
timeframe='5m'


import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

def trading_signals(data):
    # Calculate EMAs
    data['ema_3'] = ta.ema(data['close'], length=3)
    data['ema_7'] = ta.ema(data['close'], length=7)

    # Define Bullish and Bearish conditions
    # Bullish: Price above both EMAs, and 20 EMA crosses above 50 EMA (Golden Cross)
    data['bullish_signal'] = (
        (data['close'] > data['ema_3']) &
        (data['close'] > data['ema_7']) &
        (data['ema_3'] > data['ema_7']) &
        (data['ema_3'].shift(1) <= data['ema_7'].shift(1))
    )

    # Bearish: Price below both EMAs, and 20 EMA crosses below 50 EMA (Death Cross)
    data['bearish_signal'] = (
        (data['close'] < data['ema_3']) &
        (data['close'] < data['ema_7']) &
        (data['ema_3'] < data['ema_7']) &
        (data['ema_3'].shift(1) >= data['ema_7'].shift(1))
    )

    # Create Action Column
    data['action'] = 'HOLD'  # Default action
    data.loc[data['bullish_signal'], 'action'] = 'BUY'
    data.loc[data['bearish_signal'], 'action'] = 'SELL'

    # Filter only rows with signals
    signals = data['action'].iloc[-1]

    #print(signals[['close', 'ema_3', 'ema_7', 'action', 'stop_loss', 'take_profit']])
    return signals


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

def prepare_df_2(df):
    # Fractal High/Low Detection Function
    def calculate_fractals(df, window=2):
        df['fractal_high'] = None
        df['fractal_low'] = None
        for i in range(window, len(df) - window):
            if all(df['high'][i] > df['high'][i - j] for j in range(1, window + 1)) and \
            all(df['high'][i] > df['high'][i + j] for j in range(1, window + 1)):
                df.at[df.index[i], 'fractal_high'] = df['high'][i]
            if all(df['low'][i] < df['low'][i - j] for j in range(1, window + 1)) and \
            all(df['low'][i] < df['low'][i + j] for j in range(1, window + 1)):
                df.at[df.index[i], 'fractal_low'] = df['low'][i]
        return df

    # Fractal Calculations
    df = calculate_fractals(df, window=5)
    def calculate_semi_fractals(df, window=2):
        df['semi_fractal_high'] = None
        df['semi_fractal_low'] = None

        for i in range(window, len(df)):
            if all(df['high'][i] > df['high'][i - j] for j in range(1, window + 1)):
                df.at[df.index[i], 'semi_fractal_high'] = df['high'][i]

            if all(df['low'][i] < df['low'][i - j] for j in range(1, window + 1)):
                df.at[df.index[i], 'semi_fractal_low'] = df['low'][i]

        return df

    # Calculate semi-fractals and fractals
    df = calculate_semi_fractals(df, window=5)
    # Signal Columns
    df['fractal_signal'] = np.where(df['fractal_high'].notna(), 1, np.where(df['fractal_low'].notna(), -1, 0))
    df['fractal_signal'] = df['fractal_signal'].map({-1: 0, 0: 1, 1: 2})
    df['fractal_high'] = df['fractal_high'].fillna(0)
    df['fractal_low'] = df['fractal_low'].fillna(0)


    df['semi_fractal_high'] = df['semi_fractal_high'].fillna(0)
    df['semi_fractal_low'] = df['semi_fractal_low'].fillna(0)


    # Time Preprocessing
    df['time'] = pd.to_datetime(df['time']).astype(int) // 10**9

    # Feature Engineering
    df['sma_5'] = df['close'].rolling(window=5).mean()




    df['bollinger_upper'] = df['close'].rolling(window=20).mean() + 2 * df['close'].rolling(window=20).std()
    df['bollinger_lower'] = df['close'].rolling(window=20).mean() - 2 * df['close'].rolling(window=20).std()
    df['short_ma'] = df['close'].rolling(window=5).mean()
    df['long_ma'] = df['close'].rolling(window=10).mean()



    df['rsi'] = ta.rsi(df['close'], length=14)


    conditions = [
        (df['short_ma'] > df['long_ma']) & (df['rsi'] > 40),  # Uptrend condition
        (df['short_ma'] < df['long_ma']) & (df['rsi'] < 60),  # Downtrend condition
    ]
    choices = [1, -1]

    df['trend'] = np.select(conditions, choices, default=0)

    df['brokerTime'] = pd.to_datetime(df['brokerTime']).astype(int) // 10**9
    df['EMA'] = ta.ema(df['close'], length=ema_length)
    df['Returns'] = df['close'].pct_change()
    df['volatility'] = df['Returns'].std() * np.sqrt(252)  # Annualized volatility

    # Calculate MACD
    macd = ta.macd(df['close'], fast=macd_fast, slow=macd_slow, signal=macd_signal)
    df = pd.concat([df, macd], axis=1)
    df=df.drop(
        columns=['symbol', 'timeframe','volume']
    )

    df = df.dropna()

    return df


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
    """
    prices = await connection.get_symbols()
    print(prices)
    """
    try:
        try:
            # Fetch historical price data
            candles = await account.get_historical_candles(symbol=symbol, timeframe=timeframe, start_time=None, limit=120)
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
            decision=prepare(df)

            df2=prepare_df_2(df)

            last_row = scaler_X.transform(df2.iloc[-1:])
            print(df2)
            last_row = last_row.reshape(1, -1, 1)
            future_prediction = model.predict(last_row)
            print(future_prediction)
            future_prediction_rescaled = scaler_y.inverse_transform(future_prediction)
            prediction=future_prediction_rescaled.flatten()[0]
            print(f'Future Pred: {prediction}')
            print(current_market_price)
            stop_loss=current_market_price+8
            take_profit=current_market_price-8
            if decision is not None :
                if decision=='HIGH' and prediction< current_market_price and prediction>take_profit:
                    
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
                stop_loss=current_market_price-8
                take_profit=current_market_price+8
                if decision=='LOW' and prediction>current_market_price and prediction<take_profit:
                    
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