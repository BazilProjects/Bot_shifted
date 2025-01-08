import pandas as pd
import matplotlib.pyplot as plt

def trading_signals(data):
    # Calculate Simple Moving Averages (SMA)
    data['sma_3'] = data['close'].rolling(window=3).mean()
    data['sma_7'] = data['close'].rolling(window=7).mean()

    # Define Bullish and Bearish conditions based on SMA crossovers
    # Bullish: 3-period SMA crosses above 7-period SMA (Golden Cross)
    data['bullish_signal'] = (
        (data['sma_3'] > data['sma_7']) &
        (data['sma_3'].shift(1) <= data['sma_7'].shift(1))  # Golden Cross
    )

    # Bearish: 3-period SMA crosses below 7-period SMA (Death Cross)
    data['bearish_signal'] = (
        (data['sma_3'] < data['sma_7']) &
        (data['sma_3'].shift(1) >= data['sma_7'].shift(1))  # Death Cross
    )

    # Create Action Column based on the signals
    data['action'] = 'HOLD'  # Default action
    data.loc[data['bullish_signal'], 'action'] = 'BUY'
    data.loc[data['bearish_signal'], 'action'] = 'SELL'

    return data

# Test the strategy
def backtest_strategy(data):
    data = trading_signals(data)
    
    # Track trades
    trades = []
    position = None  # None, "BUY", or "SELL"
    for i in range(1, len(data)):
        # Execute Buy signal
        if data['action'].iloc[i] == 'BUY' and position != "BUY":
            position = "BUY"
            trades.append(('BUY', data['close'].iloc[i], data.index[i]))
        
        # Execute Sell signal
        elif data['action'].iloc[i] == 'SELL' and position != "SELL":
            position = "SELL"
            trades.append(('SELL', data['close'].iloc[i], data.index[i]))

    return trades, data

# Create example price data
data = pd.DataFrame({
    'close': [1, 2, 3, 4, 5, 6, 5, 6, 7, 6, 5, 6, 7, 8, 7]
}, index=pd.date_range("2025-01-01", periods=15, freq="D"))

# Backtest strategy
trades, data = backtest_strategy(data)

# Plotting the price and trades
plt.figure(figsize=(10, 6))
plt.plot(data.index, data['close'], label='Close Price', color='blue')

# Plot Buy and Sell signals
buy_signals = [trade[2] for trade in trades if trade[0] == 'BUY']
sell_signals = [trade[2] for trade in trades if trade[0] == 'SELL']
plt.scatter(buy_signals, data.loc[buy_signals]['close'], marker='^', color='green', label='Buy Signal', zorder=5)
plt.scatter(sell_signals, data.loc[sell_signals]['close'], marker='v', color='red', label='Sell Signal', zorder=5)

# Add labels and legend
plt.title("Simple Moving Average Crossover Strategy Backtest")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True)

# Show plot
plt.show()
