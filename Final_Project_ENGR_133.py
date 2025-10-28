import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from stock_functions import calculate_rsi, calculate_metrics

def validate_dates():
    while True:
        start_date = input("Enter the start date for analysis (YYYY-MM-DD): ")
        end_date = input("Enter the end date for analysis (YYYY-MM-DD): ")
        if len(start_date) == 10 and len(end_date) == 10:
            return start_date, end_date
        else:
            print("Error: Dates must be in the format YYYY-MM-DD (exactly 10 characters).")

def get_stock_data(ticker, start_date, end_date):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date)
        if data.empty:
            print(f"Error: No data found for {ticker}. Check the ticker or date range.")
        return data
    except Exception as e:
        print(f"Failed to fetch data for {ticker}: {e}")
        return pd.DataFrame()

def calculate_ema(prices, period=20):
    if len(prices) < period:
        return [np.nan] * len(prices)
    ema = [0] * len(prices)
    ema[period-1] = sum(prices[:period]) / period
    multiplier = 2 / (period + 1)
    for i in range(period, len(prices)):
        ema[i] = (prices[i] - ema[i-1]) * multiplier + ema[i-1]
    return ema

def plot_stock_prices(stock_data):
    plt.figure(figsize=(12, 6))
    for ticker, data in stock_data.items():
        if not data.empty and ticker != '^GSPC':
            plt.plot(data.index, data['Close'], label=ticker)
    plt.title('Stock Prices')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_rsi(stock_data):
    plt.figure(figsize=(12, 6))
    for ticker, data in stock_data.items():
        if not data.empty and ticker != '^GSPC':
            plt.plot(data.index, data['RSI'], label=f'{ticker} RSI')
    plt.axhline(y=70, color='r', linestyle='--')
    plt.axhline(y=30, color='g', linestyle='--')
    plt.title('Relative Strength Index (RSI)')
    plt.xlabel('Date')
    plt.ylabel('RSI')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_ema(stock_data):
    plt.figure(figsize=(12, 6))
    for ticker, data in stock_data.items():
        if not data.empty and ticker != '^GSPC':
            plt.plot(data.index, data['EMA'], label=f'{ticker} EMA')
    plt.title('Exponential Moving Average (EMA)')
    plt.xlabel('Date')
    plt.ylabel('EMA')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_combined_analysis(stock_data):
    fig, axs = plt.subplots(3, 1, figsize=(12, 18), sharex=True)

    for ticker, data in stock_data.items():
        if not data.empty and ticker != '^GSPC':
            axs[0].plot(data.index, data['Close'], label=ticker)
    axs[0].set_title('Stock Prices')
    axs[0].legend()
    axs[0].grid(True)

    for ticker, data in stock_data.items():
        if not data.empty and ticker != '^GSPC':
            axs[1].plot(data.index, data['RSI'], label=f'{ticker} RSI')
    axs[1].axhline(y=70, color='r', linestyle='--')
    axs[1].axhline(y=30, color='g', linestyle='--')
    axs[1].set_title('Relative Strength Index (RSI)')
    axs[1].legend()
    axs[1].grid(True)

    for ticker, data in stock_data.items():
        if not data.empty and ticker != '^GSPC':
            axs[2].plot(data.index, data['EMA'], label=f'{ticker} EMA')
    axs[2].set_title('Exponential Moving Average (EMA)')
    axs[2].legend()
    axs[2].grid(True)

    plt.tight_layout()
    plt.show()

def analyze_inflation_impact(stock_df, inflation_rate, ticker):
    stock_returns = stock_df['Close'].pct_change()
    real_returns = stock_returns - inflation_rate / 100 / 12
    cumulative_real_returns = (1 + real_returns).cumprod() - 1

    plt.figure(figsize=(12, 6))
    plt.plot(stock_df.index, cumulative_real_returns, label='Real Cumulative Returns')
    plt.plot(stock_df.index, stock_df['Close'] / stock_df['Close'].iloc[0] - 1, label='Nominal Cumulative Returns')
    plt.title(f'Impact of Inflation on {ticker} Returns')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Returns')
    plt.legend()
    plt.grid(True)
    plt.show()

def get_recommendation(metrics, rsi, price, ema):
    short_term = "Hold"
    long_term = "Hold"

    if rsi > 70:
        short_term = "Sell"
    elif rsi < 30:
        short_term = "Buy"
    elif price > ema:
        short_term = "Buy"
    elif price < ema:
        short_term = "Sell"

    if metrics['Total_Return'] > 0.2 and metrics['Sharpe_Ratio'] > 0.5:
        long_term = "Buy"
    elif metrics['Total_Return'] < -0.1 or metrics['Sharpe_Ratio'] < 0:
        long_term = "Sell"

    return short_term, long_term

def get_valid_number(prompt):
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("Error: Please enter a valid number.")

def main():
    start_date, end_date = validate_dates()
    num_stocks = int(get_valid_number("Enter the number of stocks you want to analyze: "))
    tickers = []
    for i in range(num_stocks):
        ticker = input(f"Enter stock ticker symbol {i+1}: ").upper()
        tickers.append(ticker)

    if '^GSPC' not in tickers:
        tickers.append('^GSPC')

    stock_data = {}
    metrics = {}

    for ticker in tickers:
        data = get_stock_data(ticker, start_date, end_date)
        if data.empty:
            continue
        data['RSI'] = calculate_rsi(data['Close'])
        data['EMA'] = calculate_ema(data['Close'])
        stock_data[ticker] = data

        total_return, volatility, sharpe_ratio = calculate_metrics(data)
        metrics[ticker] = {
            'Total_Return': total_return,
            'Volatility': volatility,
            'Sharpe_Ratio': sharpe_ratio
        }

    if not stock_data:
        print("No valid stock data available. Exiting program.")
        return

    plot_stock_prices(stock_data)
    plot_rsi(stock_data)
    plot_ema(stock_data)
    plot_combined_analysis(stock_data)

    current_inflation = get_valid_number("Enter the current month's inflation rate (%): ")

    for ticker in tickers:
        if ticker != '^GSPC' and ticker in stock_data:
            analyze_inflation_impact(stock_data[ticker], current_inflation, ticker)

    print("\nStock Analysis Results:")
    for ticker in tickers:
        if ticker == '^GSPC' or ticker not in stock_data:
            continue

        data = stock_data[ticker]
        last_close = data['Close'].iloc[-1]
        last_rsi = data['RSI'].iloc[-1]
        last_ema = data['EMA'].iloc[-1]

        short_term, long_term = get_recommendation(metrics[ticker], last_rsi, last_close, last_ema)

        print(f"\n{ticker}:")
        print(f"Current Price: ${last_close:.2f}")
        print(f"RSI: {last_rsi:.2f}")
        print(f"EMA: ${last_ema:.2f}")
        print(f"Total Return: {metrics[ticker]['Total_Return']:.2%}")
        print(f"Volatility: {metrics[ticker]['Volatility']:.2%}")
        print(f"Sharpe Ratio: {metrics[ticker]['Sharpe_Ratio']:.2f}")
        print(f"Short-term Recommendation: {short_term}")
        print(f"Long-term Recommendation: {long_term}")

    if current_inflation > 2:
        print(f"High inflation ({current_inflation}%). Consider inflation-protected assets such as real estate, bonds, or commodities.")
    else:
        print(f"Low inflation ({current_inflation}%). Stocks may outperform.")

if __name__ == "__main__":
    main()
