import pandas as pd

# TICKER_FILE = "data/idx_tickers_min.csv"
TICKER_FILE = "data/idx_tickers.csv"

def get_idx_tickers():
    df = pd.read_csv(TICKER_FILE)

    # Find ticker column dynamically
    ticker_col = next(
        (c for c in df.columns if "Kode" in c or "Saham" in c or "Ticker" in c),
        None
    )

    if ticker_col is None:
        raise RuntimeError("Ticker column not found in CSV")

    tickers = (
        df[ticker_col]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    # Convert to Yahoo Finance format
    return [f"{t}.JK" for t in tickers]
