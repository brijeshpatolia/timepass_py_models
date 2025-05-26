import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# --- Strategy Parameters ---
INITIAL_CAPITAL = 1000000.0
# The fixed additional investment amount is no longer used directly,
# instead, we use a base factor for dynamic investment.
BASE_INVESTMENT_FACTOR_PER_PERCENT_DIP = 100000.0
MIN_DIP_TRIGGER_PCT = 1.0 # Minimum dip (as a positive percentage, e.g., 1.0 for 1%) to trigger investment

ETF_TICKER = "NIFTYBEES.NS"  # Example: Nippon India ETF Nifty BeES
START_DATE = "2015-01-01"
END_DATE = "2024-12-31" # Using data up to end of last full year

# --- Download Historical Data ---
print(f"Downloading historical data for {ETF_TICKER} from {START_DATE} to {END_DATE}...")
try:
    data = yf.download(ETF_TICKER, start=START_DATE, end=END_DATE, progress=False) # auto_adjust is True by default
    if data.empty:
        print(f"No data found for {ETF_TICKER}. Please check the ticker or date range.")
        exit()
except Exception as e:
    print(f"Error downloading data: {e}")
    exit()

print("Data downloaded successfully.")

if 'Close' not in data.columns:
    print(f"Critical Error: 'Close' column not found in the downloaded data for {ETF_TICKER}.")
    print("Available columns are:", data.columns)
    exit()

# Robustly select the 'Close' price Series
close_price_data = data['Close']
if isinstance(close_price_data, pd.DataFrame):
    print("Note: data['Close'] resolved to a DataFrame. Using its first column as the definitive close price series.")
    if close_price_data.shape[1] > 0:
        actual_close_prices = close_price_data.iloc[:, 0]
    else:
        print(f"Critical Error: data['Close'] for {ETF_TICKER} resolved to an empty DataFrame.")
        exit()
elif isinstance(close_price_data, pd.Series):
    actual_close_prices = close_price_data
else:
    print(f"Critical Error: data['Close'] for {ETF_TICKER} is not a DataFrame or Series. Type: {type(close_price_data)}")
    exit()

data['Actual_Close'] = actual_close_prices
data['Prev_Close'] = data['Actual_Close'].shift(1)
# Calculate daily change as a fraction (e.g., -0.02 for a 2% drop)
data['Daily_Change_Fraction'] = (data['Actual_Close'] - data['Prev_Close']) / data['Prev_Close']
data = data.dropna()
if data.empty:
    print("Error: No data left after processing and dropna(). Check date range or data source.")
    exit()

# --- Backtesting User's Strategy ---
strategy_units = 0
strategy_total_invested = 0
strategy_portfolio_value_history = []
strategy_investments_log = []

# Initial Investment
first_day_price = data['Actual_Close'].iloc[0]
strategy_units = INITIAL_CAPITAL / first_day_price
strategy_total_invested = INITIAL_CAPITAL
strategy_investments_log.append({'date': data.index[0], 'amount': -INITIAL_CAPITAL})
print(f"\n--- User's Strategy (Dynamic Dip Investment) ---")
print(f"Base investment factor per percent dip: ₹{BASE_INVESTMENT_FACTOR_PER_PERCENT_DIP:,.2f}")
print(f"Minimum dip to trigger: {MIN_DIP_TRIGGER_PCT}%")
print(f"Initial Investment on {data.index[0].date()}: ₹{INITIAL_CAPITAL:,.2f} at ₹{first_day_price:,.2f}, Units: {strategy_units:,.2f}")

for i in range(len(data)):
    current_date = data.index[i]
    current_price = data['Actual_Close'].iloc[i]
    daily_change_fraction = data['Daily_Change_Fraction'].iloc[i] # e.g., -0.02 for a 2% drop

    # Convert fractional change to absolute percentage dip
    # daily_change_fraction will be negative for a dip
    absolute_dip_pct = abs(daily_change_fraction) * 100

    # Trigger condition: dip must be >= MIN_DIP_TRIGGER_PCT
    if daily_change_fraction <= -(MIN_DIP_TRIGGER_PCT / 100.0):
        # Dynamic investment amount based on dip magnitude
        current_additional_investment = absolute_dip_pct * BASE_INVESTMENT_FACTOR_PER_PERCENT_DIP

        units_bought_on_dip = current_additional_investment / current_price
        strategy_units += units_bought_on_dip
        strategy_total_invested += current_additional_investment
        strategy_investments_log.append({'date': current_date, 'amount': -current_additional_investment})
        print(f"Trigger on {current_date.date()}: Price ₹{current_price:,.2f} (Dip: {absolute_dip_pct:,.2f}%) -> Dynamic Investment: ₹{current_additional_investment:,.2f}, New Units: {units_bought_on_dip:,.2f}")

    current_portfolio_value = strategy_units * current_price
    strategy_portfolio_value_history.append(current_portfolio_value)

if not strategy_portfolio_value_history:
    print("Error: Strategy portfolio value history is empty. Something went wrong during simulation.")
    exit()

final_portfolio_value_strategy = strategy_portfolio_value_history[-1]
strategy_investments_log.append({'date': data.index[-1], 'amount': final_portfolio_value_strategy})

# --- Backtesting Benchmark (Buy and Hold) ---
benchmark_units = INITIAL_CAPITAL / first_day_price
benchmark_portfolio_value_history = benchmark_units * data['Actual_Close']
final_portfolio_value_benchmark = benchmark_portfolio_value_history.iloc[-1]
print(f"\n--- Benchmark Strategy (Buy and Hold) ---")
print(f"Initial Investment on {data.index[0].date()}: ₹{INITIAL_CAPITAL:,.2f} at ₹{first_day_price:,.2f}, Units: {benchmark_units:,.2f}")

# --- Performance Calculation ---
num_years = (data.index[-1] - data.index[0]).days / 365.25

# User's Strategy Performance
total_return_strategy_pct = (final_portfolio_value_strategy - strategy_total_invested) / strategy_total_invested * 100 if strategy_total_invested > 0 else 0
cagr_strategy_approx = 0
if strategy_total_invested > 0 and num_years > 0 :
    if final_portfolio_value_strategy > 0 :
        cagr_strategy_approx = ((final_portfolio_value_strategy / strategy_total_invested)**(1 / num_years) - 1) * 100
    elif final_portfolio_value_strategy == 0 and strategy_total_invested > 0: # Handles total loss of invested capital
        cagr_strategy_approx = -100.0
    # Note: A more complex formula or iterative method (like XIRR) is needed if final_portfolio_value_strategy is negative

# Benchmark Strategy Performance
total_return_benchmark_pct = (final_portfolio_value_benchmark - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100 if INITIAL_CAPITAL > 0 else 0
cagr_benchmark = 0
if INITIAL_CAPITAL > 0 and num_years > 0:
    if final_portfolio_value_benchmark > 0:
        cagr_benchmark = ((final_portfolio_value_benchmark / INITIAL_CAPITAL)**(1 / num_years) - 1) * 100
    elif final_portfolio_value_benchmark == 0: # Handles total loss of benchmark capital
        cagr_benchmark = -100.0

print("\n--- Performance Summary ---")
print(f"Period: {data.index[0].date()} to {data.index[-1].date()} ({num_years:.2f} years)")

print(f"\nUser's Strategy (Dynamic Dip Investment):")
print(f"  Final Portfolio Value: ₹{final_portfolio_value_strategy:,.2f}")
print(f"  Total Amount Invested: ₹{strategy_total_invested:,.2f}")
print(f"  Net Profit: ₹{(final_portfolio_value_strategy - strategy_total_invested):,.2f}")
print(f"  Total Return on Invested Capital: {total_return_strategy_pct:.2f}%")
print(f"  Approx. Annualized Return (CAGR-like): {cagr_strategy_approx:.2f}% (Note: XIRR is more precise for irregular investments)")

print(f"\nBenchmark (Buy and Hold):")
print(f"  Final Portfolio Value: ₹{final_portfolio_value_benchmark:,.2f}")
print(f"  Total Amount Invested: ₹{INITIAL_CAPITAL:,.2f}")
print(f"  Net Profit: ₹{(final_portfolio_value_benchmark - INITIAL_CAPITAL):,.2f}")
print(f"  Total Return: {total_return_benchmark_pct:.2f}%")
print(f"  CAGR: {cagr_benchmark:.2f}%")

# --- Plotting Results (Optional) ---
plt.figure(figsize=(14, 7))
plt.plot(data.index, strategy_portfolio_value_history, label="User's Strategy Portfolio Value (Dynamic Dip)")
plt.plot(data.index, benchmark_portfolio_value_history, label="Benchmark (Buy & Hold) Portfolio Value")
plt.title(f"Strategy vs. Benchmark Performance ({ETF_TICKER})")
plt.xlabel("Date")
plt.ylabel("Portfolio Value (₹)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

print("\n--- Important Notes ---")
print("1. Past performance is not indicative of future results.")
print("2. This backtest does not include transaction costs, taxes, or ETF tracking error.")
print(f"3. 'Close' prices from yfinance (with auto_adjust=True by default) are used, which typically account for dividends and splits.")
print("4. The 'Approx. Annualized Return' for the user's strategy is a simplified calculation. For strategies with irregular cash flows, XIRR (Extended Internal Rate of Return) provides a more accurate measure of CAGR.")
print("5. This dynamic strategy can lead to very large investments during sharp market drops. Ensure this aligns with your capital availability and risk tolerance.")