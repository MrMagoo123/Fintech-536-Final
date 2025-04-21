import csv
import time
from ib_client import start_ib_client, stock_contract, market_order

def get_current_positions():
    app = start_ib_client()
    app.reqPositions()
    time.sleep(2)
    positions = app.positions.copy()
    app.disconnect()
    return positions

def rebalance_portfolio(target_allocations, current_positions):
    app = start_ib_client()

    for ticker, target_qty in target_allocations.items():
        current_qty = current_positions.get(ticker, 0)
        diff = target_qty - current_qty
        if diff != 0:
            action = "BUY" if diff > 0 else "SELL"
            qty = abs(diff)
            contract = stock_contract(ticker)
            order = market_order(action, qty)

            print(f"Placing {action} order for {qty} shares of {ticker}")
            app.placeOrder(app.next_order_id, contract, order)
            app.next_order_id += 1

    time.sleep(5)
    write_fills_to_csv(app.fills)
    app.disconnect()

def write_fills_to_csv(fills, filename="fills_log.csv"):
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['symbol', 'exec_id', 'shares', 'price', 'time'])
        if file.tell() == 0:
            writer.writeheader()
        for fill in fills:
            writer.writerow(fill)
