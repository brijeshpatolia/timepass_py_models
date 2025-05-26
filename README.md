# NIFTY ETF Dynamic Dip Investment Strategy Backtester

## 📜 Description

This Python script performs a historical backtest of a specific dynamic investment strategy for NIFTY Exchange Traded Funds (ETFs). It compares the performance of this active strategy against a simple buy-and-hold benchmark over a user-defined period. The script fetches historical market data, simulates trades, calculates key performance metrics, and visualizes the results.

## ✨ Strategy Backtested

The core investment strategy analyzed by this script is as follows:

1.  **Initial Investment:** A lump-sum amount is invested in the chosen NIFTY ETF at the beginning of the backtest period.
2.  **Trigger for Additional Investment:** An additional investment is made if the NIFTY ETF's closing price drops by **1% or more** in a single trading day compared to the previous day's close.
3.  **Dynamic Investment Amount:** The amount of the additional investment is not fixed. Instead, it's dynamically calculated based on the magnitude of the dip:
    `Investment Amount = (Absolute Percentage Dip) * Base Investment Factor`
    * For example, if the `Base Investment Factor` is set to ₹100,000:
        * A 1.5% dip triggers an investment of `1.5 * ₹100,000 = ₹150,000`.
        * A 3.0% dip triggers an investment of `3.0 * ₹100,000 = ₹300,000`.

## 🚀 Features

* Fetches historical daily price data for NIFTY ETFs using the `yfinance` library.
* Simulates the described dynamic dip-buying investment strategy.
* Simulates a passive buy-and-hold benchmark strategy for comparison.
* Calculates and displays key performance metrics, including:
    * Final Portfolio Value
    * Total Amount Invested
    * Net Profit
    * Total Return on Invested Capital (%)
    * Approximate Annualized Return (CAGR-like)
* Generates a plot comparing the portfolio values of the active strategy and the benchmark over the backtest period.
* Allows easy customization of parameters such as initial capital, base investment factor, ETF ticker, and backtesting date range.

## ⚙️ How it Works

1.  **Data Retrieval:** The script downloads historical daily Open, High, Low, Close (OHLC) and Volume data for the specified NIFTY ETF ticker within the given date range. It uses Adjusted Close prices to account for dividends and splits.
2.  **Daily Change Calculation:** It calculates the daily percentage change in the ETF's price.
3.  **User's Strategy Simulation:**
    * An initial lump sum is invested on the first day.
    * On subsequent days, if the ETF price drops by 1% or more, an additional investment is simulated. The amount invested is proportional to the percentage drop multiplied by the defined `BASE_INVESTMENT_FACTOR_PER_PERCENT_DIP`.
    * The script tracks total units purchased, total capital invested, and the daily portfolio value.
4.  **Benchmark Strategy Simulation:**
    * An initial lump sum (identical to the user's strategy) is invested on the first day.
    * This investment is held throughout the entire backtest period without any further transactions.
    * The daily portfolio value is tracked.
5.  **Performance Analysis:** After simulating both strategies for the entire period, the script computes and prints a summary of performance metrics and displays a comparative plot.

## 🛠️ Requirements

* Python 3.x
* The following Python libraries:
    * `yfinance`
    * `pandas`
    * `numpy`
    * `matplotlib`

## ▶️ How to Use

1.  **Clone or Download:**
    * Clone this repository: `git clone <your-repo-url>`
    * Or, download the Python script file (e.g., `nifty_dip_backtester.py`).

2.  **Install Dependencies:**
    Open your terminal or command prompt and run:
    ```bash
    pip install yfinance pandas numpy matplotlib
    ```

3.  **Customize Parameters (Optional):**
    Open the Python script in a text editor and modify the parameters at the beginning of the file as needed:
    ```python
    # --- Strategy Parameters ---
    INITIAL_CAPITAL = 1000000.0
    BASE_INVESTMENT_FACTOR_PER_PERCENT_DIP = 100000.0 # Key factor for dynamic investment
    MIN_DIP_TRIGGER_PCT = 1.0 # Minimum dip (as positive %) to trigger

    ETF_TICKER = "NIFTYBEES.NS"  # Example: Nippon India ETF Nifty BeES
    START_DATE = "2015-01-01"
    END_DATE = "2024-12-31"
    ```

4.  **Run the Script:**
    Execute the script from your terminal:
    ```bash
    python your_script_name.py
    ```
    (Replace `your_script_name.py` with the actual name of your Python file).

## 📊 Interpreting Results

* The script will print a **Performance Summary** in your terminal, comparing the User's Strategy (Dynamic Dip Investment) against the Benchmark (Buy and Hold).
* Key metrics include Final Portfolio Value, Total Amount Invested, Net Profit, Total Return on Invested Capital, and an Approximate Annualized Return (CAGR-like).
* A **plot** will be displayed showing the growth of portfolio values for both strategies over time. This helps visualize performance across different market conditions.
* **Important Note on CAGR:** The "Approx. Annualized Return" for the User's Strategy is a simplified calculation. Due to the irregular nature and timing of the additional investments, a more precise measure of compounded annual growth rate is the **XIRR (Extended Internal Rate of Return)**. The script generates a `strategy_investments_log` list (containing dates and cash flows) which can be used with spreadsheet software (like Excel or Google Sheets using the `XIRR` function) or financial libraries in Python to calculate the XIRR.

## 🖼️ Example Output
--- Performance Summary ---
Period: 2015-01-02 to 2024-12-30 (9.99 years)

User's Strategy (Dynamic Dip Investment):
  Final Portfolio Value: ₹280,611,721.70
  Total Amount Invested: ₹50,851,610.31
  Net Profit: ₹229,760,111.39
  Total Return on Invested Capital: 451.82%
  Approx. Annualized Return (CAGR-like): 18.64% (Note: XIRR is more precise for irregular investments)

Benchmark (Buy and Hold):
  Final Portfolio Value: ₹3,120,735.71
  Total Amount Invested: ₹1,000,000.00
  Net Profit: ₹2,120,735.71
  Total Return: 212.07%
  CAGR: 12.06%
