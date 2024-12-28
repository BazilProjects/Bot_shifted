import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

def trading_signals(data_path, output_path='signals.csv', plot_graph=True):
    """
    Generates buy and sell signals based on EMA crossovers and price conditions, 
    and optionally plots the results.

    Args:
        data_path (str): Path to the input CSV file with 'close' and 'time' columns.
        output_path (str): Path to save the resulting signals CSV file. Default is 'signals.csv'.
        plot_graph (bool): Whether to plot the graph of close prices and trades. Default is True.

    Returns:
        pd.DataFrame: A DataFrame containing signals and key metrics.
    """
    # Load the data
    data = pd.read_csv(data_path)
    #data['time'] = pd.to_time(data['time'])
    data.set_index('time', inplace=True)

    # Calculate EMAs
    data['ema_3'] = ta.ema(data['close'], length=3)
    data['ema_5'] = ta.ema(data['close'], length=20)
    data['ema_7'] = ta.ema(data['close'], length=7)
    data['rsi'] = ta.rsi(data['close'], rsi_period=14)

    # Define Bullish and Bearish conditions
    # Bullish: Price above both EMAs, and 20 EMA crosses above 50 EMA (Golden Cross)
    data['bullish_signal'] = (
        (data['close'] > data['ema_3']) &
        (data['close'] > data['ema_7']) &
        (data['ema_3'] > data['ema_7']) &
        (data['rsi'] <45) &
        (data['ema_7'] > data['ema_5']) &
        (data['ema_3'].shift(1) <= data['ema_7'].shift(1))
    )

    # Bearish: Price below both EMAs, and 20 EMA crosses below 50 EMA (Death Cross)
    data['bearish_signal'] = (
        (data['close'] < data['ema_3']) &
        (data['close'] < data['ema_7']) &
        (data['ema_3'] < data['ema_7']) &
        (data['rsi'] >55) &
        (data['ema_7'] < data['ema_5']) &
        (data['ema_3'].shift(1) >= data['ema_7'].shift(1))
    )

    # Create Action Column
    data['action'] = 'HOLD'  # Default action
    data.loc[data['bullish_signal'], 'action'] = 'BUY'
    data.loc[data['bearish_signal'], 'action'] = 'SELL'

    # Stop-loss and Take-profit (example setup)
    data['stop_loss'] = data['ema_7']  # Stop-loss based on EMA 50
    data['take_profit'] = data['close'] * 1.02  # Example: 2% profit target

    # Filter only rows with signals
    signals = data[data['action'] != 'HOLD']
    signals.to_csv(output_path)

    if plot_graph:
        # Create the plot
        fig = go.Figure()

        # Add close prices
        fig.add_trace(go.Scatter(x=data.index, y=data['close'], mode='lines', name='Close Price'))

        # Add EMAs
        fig.add_trace(go.Scatter(x=data.index, y=data['ema_3'], mode='lines', name='EMA 3', line=dict(dash='dot', color='green')))
        fig.add_trace(go.Scatter(x=data.index, y=data['ema_7'], mode='lines', name='EMA 7', line=dict(dash='dot', color='red')))
        fig.add_trace(go.Scatter(x=data.index, y=data['ema_5'], mode='lines', name='EMA 5', line=dict(dash='dot', color='yellow')))

        # Highlight buy signals
        buy_signals = data[data['action'] == 'BUY']
        fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['close'], mode='markers', name='Buy Signal', marker=dict(color='green', symbol='triangle-up')))

        # Highlight sell signals
        sell_signals = data[data['action'] == 'SELL']
        fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['close'], mode='markers', name='Sell Signal', marker=dict(color='red', symbol='triangle-down')))

        # Customize layout
        fig.update_layout(
            title='EMA Crossover Strategy',
            xaxis_title='',
            yaxis_title='Price',
            legend_title='Legend',
            template='plotly_white',
        )


        # Show the plot
        fig.show()

    #print(signals[['close', 'ema_3', 'ema_7', 'action', 'stop_loss', 'take_profit']])
    return signals

# Example usage
signals = trading_signals('/home/omenyo/Documents/Github2/Bot_Vector/COLLECT CANDLES/1h/Step Index1h100.csv')
