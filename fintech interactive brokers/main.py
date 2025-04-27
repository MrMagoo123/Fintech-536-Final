from data_fetcher import fetch_historical_data, optimize_portfolio, fetch_latest_prices
from trader import rebalance_portfolio, get_account_value

TICKERS = ["AAPL", "TSLA", "MSTR", "GME", "AMZN", "USO", "SHY", "IVV", "QQQ", "VOO", "IBKR", "MSFT", "NVDA", "SPY", "META"]


def main():
    # print(yf.__version__)

    print("🔍 Fetching historical data...")
    historical_data = fetch_historical_data(TICKERS)

    print("🧠 Optimizing portfolio...")
    weights = optimize_portfolio(historical_data)

    print("💰 Fetching account value...")
    capital = get_account_value()
    if capital == 0.0:
        print("⚠️ Could not fetch NetLiquidation. Using fallback capital of $10,000.")
        capital = 10000.0
    print(f"✅ Capital available for allocation: ${capital:.2f}")

    print("💹 Fetching latest prices...")
    latest_prices = fetch_latest_prices(TICKERS)

    print("📊 Calculating target allocations...")
    allocations = {
        symbol: weights.get(symbol, 0.0)
        for symbol in TICKERS
        if symbol in latest_prices and latest_prices[symbol] > 0
    }

    estimated_cost = sum((capital * weight) for symbol, weight in allocations.items())
    cash_remaining = capital - estimated_cost
    print(f"💸 Estimated cash remaining after allocation: ${cash_remaining:.2f}")


    print("🔁 Rebalancing portfolio...")
    rebalance_portfolio(allocations, latest_prices)


if __name__ == "__main__":
    main()
