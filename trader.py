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
from sklearn.preprocessing import StandardScaler

token = os.getenv('TOKEN') or 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2YjI0NTQ0ZWYzMWI0NzQ4NWMxNzQ1NmUzNzdmYTlhZiIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZXN0LWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1ycGMtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTp3czpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoicmlzay1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsicmlzay1tYW5hZ2VtZW50LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJjb3B5ZmFjdG9yeS1hcGkiLCJtZXRob2RzIjpbImNvcHlmYWN0b3J5LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtdC1tYW5hZ2VyLWFwaSIsIm1ldGhvZHMiOlsibXQtbWFuYWdlci1hcGk6cmVzdDpkZWFsaW5nOio6KiIsIm10LW1hbmFnZXItYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6ImJpbGxpbmctYXBpIiwibWV0aG9kcyI6WyJiaWxsaW5nLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19XSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaW1wZXJzb25hdGVkIjpmYWxzZSwicmVhbFVzZXJJZCI6IjZiMjQ1NDRlZjMxYjQ3NDg1YzE3NDU2ZTM3N2ZhOWFmIiwiaWF0IjoxNzMxODAxNjc3fQ.QDGpGFvszwuNOFS3yHN9V58HDADbYhHUOWWNjbOfUBOIH37U_BiYkBdwGK_pgPpdM-zgLqq3wAIgFx6KqegWW4I_Ro_CDfTEuT3-qFLohSSdqSOddo9qhya8u7U9XM0xHt_R2i9jBAjEi3c51pHnfChPAGpPBI_0CsY6tCXhbQBLDgrqZHLJ4-sLBsgmF0XcnaomtTLBAE7IUWRRoBdRxkUDzSXUVDJeg99cfuDNZGxVqTKfXZdXBIkTzPBGaoABoXwEMEINkYLxsWv4YeTVXQBnDfe4unekHaowFePhUOh9r5bASL9WGr0jZx0ua5MHwb5VdW5gQ22d-YFmmKLKaEPlSawq1ChR8Q6zjAtmoDillwaSXgBvrRdC1b7nCR_aXsFcCbXS1rAkXZBxu8CaNSAA_3SXNiX6n0xeqfaJUgHykh1cNf8q-yCAei_7V5iYMOnj3Vpn9x3B__A-GJxbHUAmF4hzamwyU5s-MtO8P4cJsJWhxrrvsIXwGMlxs2iU2iq3mL3nxQ4imqklB0GsC0soN_y15iTYF7LKz5QT76O_ikbwrpU5goM33eLnQOr482Oqhqi8wZRYkV8XXJSkB-MKoEfyJ-61twJMNB1plioB2WJDquWNoL9Hfl6eeXWZH72SmUxYn6ybAZ8B43_2DqSKU-FFMUcoKyR48zpv70A'
accountId = os.getenv('ACCOUNT_ID') or '78762d25-0350-4425-8d64-d1f3c57745c4'

def decimal_places(number):
    # Convert the number to a string
    num_str = str(number)
    
    # Check if there is a decimal point
    if '.' in num_str:
        # Find the index of the decimal point
        decimal_index = num_str.index('.')
        
        # Count the characters after the decimal point
        num_decimal_places = len(num_str) - decimal_index - 1
        
        return num_decimal_places
    else:
        # If there is no decimal point, return 0
        return 0
def compute_sma(data, window=14):
    return data['open'].rolling(window=window).mean()

def compute_rsi(data, window=14):
    delta = data['open'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# Anomaly Detection Function
def detect_anomalies(X, contamination=0.05):
    """
    Detect anomalies in the input features using Isolation Forest.
    """
    isolation_forest = IsolationForest(contamination=contamination, random_state=42)
    anomaly_labels = isolation_forest.fit_predict(X)
    return anomaly_labels  # -1 for anomalies, 1 for normal

def prepare(df,time,open_price):
    features = ['high', 'low', 'close']
    df =df.drop(columns=['symbol', 'timeframe', 'brokerTime', 'volume', 'spread','tickVolume','high', 'low', 'close'])
    df.loc[len(df)] = [time, open_price]
    #print(df)
    df['time'] = pd.to_datetime(df['time'])
    df['time'] = df['time'].astype(int)// 10
    df['previous_close'] = df['open'].shift(1)

    # Feature Engineering
    short_window = 2
    long_window = 6
    rsi_window = 14

    df['SMA_short'] = compute_sma(df, short_window)
    df['SMA_long'] = compute_sma(df, long_window)
    df['RSI'] = compute_rsi(df, rsi_window)

    df["RSI_signal"] = np.where(df["RSI"] < 40, 1, np.where(df["RSI"] > 60, 1, 0))
    #df["trade_action"] = np.where(df["RSI_signal"] == 1, 1, np.where(df["RSI_signal"] == -1, 0, np.nan))


    #df['SMA_RSI_interaction'] = df['SMA_short'] * df['RSI']
    #df['trend_strength'] = df['SMA_long'] - df['SMA_short']


    # Adding rolling statistics
    df['rolling_mean'] = df['open'].rolling(window=5).mean()
    #df['rolling_std'] = df['previous_close'].rolling(window=5).std()

    df['rolling_11'] = df['open']/df['time']
    #print(df)
    # Split data into train/test
    X = df.iloc[-1]#.drop(columns=['next_close','target'])

    return X




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
    
    # Load the saved voting models
    with open('trading_models.pkl', 'rb') as f:
        models = pickle.load(f)
    # Load the saved voting models
    with open('trading_classifier_models.pkl', 'rb') as f:
        classifier_models = pickle.load(f)

    # Iterate through the models and print their details
    for (key, model), (_, classifier_model) in zip(models.items(), classifier_models.items()):
        # Process `model` from `models` and `classifier_model` from `classifier_models`
        parts = key.split('_')
        symbol = parts[0]
        timeframe = parts[1] if len(parts) > 1 else "Unknown"
        print(f"Model Name: {key}")
        print(f"Symbol: {symbol}, Timeframe: {timeframe}")
        try:
            try:
                # Fetch historical price data
                candles = await account.get_historical_candles(symbol=symbol, timeframe=timeframe, start_time=None, limit=20)

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
                print(prices)
                # Extract bid and ask prices
                bid_price =float(prices['bid'])
                ask_price = float(prices['ask'])
                current_market_price=((bid_price+ask_price)/2)
                current_open=current_market_price
                time=prices['time']
                open_price=bid_price
                X_new=prepare(df,time,open_price)
                print(X_new)
                classification_prediction=classifier_model.predict(np.array(X_new).reshape(1,-1))
                regressor_prediction=model.predict(np.array(X_new).reshape(1,-1)).round(decimal_places(df['open'].iloc[-1]))
                if classification_prediction[0]==1 and regressor_prediction > current_market_price:
                    stop_loss=None#current_open-stop_loss_away
                    #take_profit=trademax-(lag_size/2)
                    try:
                        
                        result = await connection.create_market_buy_order(
                            symbol=symbol,
                            volume=0.01,
                            stop_loss=stop_loss,
                            take_profit=regressor_prediction[0],
                        )
                        print(f'Buy_Signal (T)   :Buy Trade successful For Symbol :{symbol}')
                        
                        Trader_success=True
                    except Exception as err:
                        print('Trade failed with error:')
                        print(api.format_error(err))
                elif classification_prediction[0]==0 and regressor_prediction > current_market_price:
                    stop_loss=None#current_open+stop_loss_away
                    #take_profit=trademax+(lag_size/2)
                    try:
                        
                        result = await connection.create_market_sell_order(
                            symbol=symbol,
                            volume=0.01,
                            stop_loss=stop_loss,
                            take_profit=regressor_prediction[0],
                        )
                        print(f'Sell Signal (T)   :Sell Trade successful For Symbol :{symbol}')
                        Trader_success=True

                    except Exception as err:
                        #raise err
                        print('Trade failed with error:')
                        print(api.format_error(err))
                else:
                    print('No trade conditions passed, so no trade placed')
            print('*'*20)
            print('*'*20)
            print('*'*20)
        except Exception as e:
            raise e
            print(f"An error occurred: {e}")
#def main():
asyncio.run(main2())