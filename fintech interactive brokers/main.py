from data_fetcher import fetch_historical_data, optimize_portfolio, fetch_latest_prices, compute_target_allocations
from trader import get_current_positions, rebalance_portfolio

TICKERS = ["AAPL", "TSLA", "MSTR", "GME", "AMZN", "USO", "SHY", "IVV"]

def main():
    print("Fetching historical data...")
    hist_data = fetch_historical_data(TICKERS)

    print("Optimizing portfolio...")
    weights = optimize_portfolio(hist_data)

    print("Fetching latest prices...")
    prices = fetch_latest_prices(TICKERS)

    print("Fetching current positions...")
    current_positions = get_current_positions()

    capital = 10000  # Manually set or make dynamic later
    print(f"Computing allocations for capital: ${capital}")
    allocations = compute_target_allocations(weights, capital, prices)

    print("Rebalancing portfolio...")
    rebalance_portfolio(allocations, current_positions)

if __name__ == "__main__":
    main()
