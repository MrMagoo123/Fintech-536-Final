import pandas as pd
import time
import shinybroker as sb
import yfinance as yf
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import expected_returns, risk_models


# Function to fetch close price for a given ticker using shinybroker
def fetch_close_for_a_ticker(ticker):
    df = sb.fetch_historical_data(
        contract=sb.Contract({
            'symbol': ticker,
            'secType': "STK",
            'exchange': "SMART",
            'currency': "USD"
        }),
        barSizeSetting='1 day',
        durationStr='1 Y',
        whatToShow='ADJUSTED_LAST'
    )['hst_dta'][['timestamp', 'close']]
    df = df.rename(columns={'close': ticker})
    return df


# Function to fetch historical data for multiple tickers
def fetch_historical_data(tickers):
    df = fetch_close_for_a_ticker(tickers[0])
    for tk in tickers[1:]:
        df = pd.merge(df, fetch_close_for_a_ticker(tk), on='timestamp')
        time.sleep(0.1)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df.set_index('timestamp')


# Function to fetch the latest prices for multiple tickers
def fetch_latest_prices(tickers):
    prices = {}
    for tk in tickers:
        df = fetch_close_for_a_ticker(tk)
        prices[tk] = df[tk].iloc[-1]
    return prices


# Function to fetch fundamental data like PE ratio and market cap using yfinance
def fetch_fundamentals_yf(ticker):
    """Fetch fundamental data for a given ticker using yfinance."""
    stock = yf.Ticker(ticker)
    info = stock.info
    
    fundamentals = {
        'pe_ratio': info.get('trailingPE', None),
        'market_cap': info.get('marketCap', None),  # Market Cap as Size factor
    }
    
    return fundamentals


# Function to optimize the portfolio using momentum, size (market cap), and value (PE ratio)
def optimize_portfolio(historical_data, fundamentals):
    # 1. Momentum Factor: 6-month price change
    momentum = historical_data.pct_change(126).iloc[-1]

    # Scale momentum scores between 0 and 1
    min_mom = momentum.min()
    max_mom = momentum.max()
    scaled_momentum = (momentum - min_mom) / (max_mom - min_mom)

    # 2. Size Factor: Market Cap (larger market cap = higher score)
    market_caps = {ticker: fundamentals[ticker].get('market_cap', None) for ticker in fundamentals}
    
    # Remove tickers with None as market cap
    market_caps = {ticker: cap for ticker, cap in market_caps.items() if cap is not None}
    
    # Check if there are any valid market cap values to compute scaling
    if len(market_caps) > 0:
        min_size = min(market_caps.values())
        max_size = max(market_caps.values())
        scaled_size = {ticker: (market_caps[ticker] - min_size) / (max_size - min_size) for ticker in market_caps}
    else:
        scaled_size = {}

    # 3. Value Factor: PE ratio (lower PE = better value)
    pe_ratios = {ticker: fundamentals[ticker].get('pe_ratio', None) for ticker in fundamentals}
    
    # Remove tickers with None as PE ratio
    pe_ratios = {ticker: pe for ticker, pe in pe_ratios.items() if pe is not None}

    # Check if there are any valid PE ratios to compute scaling
    if len(pe_ratios) > 0:
        min_pe = min(pe_ratios.values())
        max_pe = max(pe_ratios.values())
        scaled_pe = {ticker: (min_pe - pe_ratios[ticker]) / (min_pe - max_pe) for ticker in pe_ratios}
    else:
        scaled_pe = {}

    # Combine all factors into a combined expected return score
    combined_returns = {}
    for ticker in momentum.index:
        combined_returns[ticker] = (
            0.4 * scaled_momentum.get(ticker, 0) +  # 40% momentum
            0.3 * scaled_size.get(ticker, 0) +      # 30% size (market cap)
            0.3 * scaled_pe.get(ticker, 0)         # 30% value (PE ratio)
        )

    # Convert combined_returns dictionary to a Pandas Series
    mu = pd.Series(combined_returns)

    # Use sample covariance matrix for risk estimation
    S = risk_models.sample_cov(historical_data)

    # Optimize the portfolio using the Efficient Frontier with the combined expected returns and covariance matrix
    ef = EfficientFrontier(mu, S)
    weights = ef.max_sharpe()  # Maximize Sharpe ratio for portfolio
    return ef.clean_weights()




# Function to compute target allocations based on portfolio weights and prices
def compute_target_allocations(weights, capital, prices):
    allocations = {}
    for ticker, weight in weights.items():
        if weight > 0:
            dollar_amount = capital * weight
            allocations[ticker] = int(dollar_amount / prices[ticker])
    return allocations
