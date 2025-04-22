from data_fetcher import fetch_historical_data, optimize_portfolio, fetch_latest_prices
from trader import rebalance_portfolio, get_account_value
from optimizer import get_target_allocations

# from positionsTest import read_positions

from ibapi.client import EClient
from ibapi.wrapper import EWrapper


TICKERS = ["AAPL", "TSLA", "MSTR", "GME", "AMZN", "USO", "SHY", "IVV"]

def main(): #this does everything
    print("Fetching historical data...")
    hist_data = fetch_historical_data(TICKERS)

    print("Optimizing portfolio...")
    weights = optimize_portfolio(hist_data)

    capital = get_account_value() 
    if capital == 0.0:
        print("⚠️ Warning: Could not fetch NetLiquidation value. Using fallback capital = $10,000.")
        capital = 10000.0
    print(f"Computing allocations for capital: ${capital:.2f}")

    latest_prices = fetch_latest_prices(TICKERS)
    allocations = {tk: weights[tk] for tk in TICKERS}

    print("Rebalancing portfolio...")
    rebalance_portfolio(allocations, latest_prices)



if __name__ == "__main__":
    main()