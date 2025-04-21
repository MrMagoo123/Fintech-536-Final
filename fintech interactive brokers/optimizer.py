# Optimize portfolio using PyPortfolioOpt

from pypfopt import expected_returns, risk_models
from pypfopt.efficient_frontier import EfficientFrontier

def optimize_portfolio(historical_data):
    mu = expected_returns.mean_historical_return(historical_data)
    S = risk_models.sample_cov(historical_data)
    ef = EfficientFrontier(mu, S)
    weights = ef.max_sharpe()
    ef.portfolio_performance(verbose=True)
    return weights
