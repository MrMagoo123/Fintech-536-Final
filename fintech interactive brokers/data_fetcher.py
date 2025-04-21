import pandas as pd
import time
import shinybroker as sb
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import expected_returns, risk_models

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

def fetch_historical_data(tickers):
    df = fetch_close_for_a_ticker(tickers[0])
    for tk in tickers[1:]:
        df = pd.merge(df, fetch_close_for_a_ticker(tk), on='timestamp')
        time.sleep(0.1)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df.set_index('timestamp')

def fetch_latest_prices(tickers):
    prices = {}
    for tk in tickers:
        df = fetch_close_for_a_ticker(tk)
        prices[tk] = df[tk].iloc[-1]
    return prices

def optimize_portfolio(historical_data):
    mu = expected_returns.mean_historical_return(historical_data)
    S = risk_models.sample_cov(historical_data)
    ef = EfficientFrontier(mu, S)
    weights = ef.max_sharpe()
    return ef.clean_weights()

def compute_target_allocations(weights, capital, prices):
    allocations = {}
    for ticker, weight in weights.items():
        if weight > 0:
            dollar_amount = capital * weight
            allocations[ticker] = int(dollar_amount / prices[ticker])
    return allocations
