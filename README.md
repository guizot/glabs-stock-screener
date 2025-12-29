
# IDX Beginner Stock Screener (yfinance)

This project screens **ALL Indonesia Stock Exchange (IDX)** stocks using beginner-friendly rules.

## Rules (Beginner)
1. Price > MA20
2. Average Volume (20d) > 1,000,000
3. Last Close > 500 IDR

## Output
- Prints 5–20 filtered stocks
- Saves results to `results.csv`

## Setup
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python main.py
```
