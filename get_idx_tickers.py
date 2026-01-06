import pandas as pd
import os

def get_available_sectors():
    """Get list of available sector files"""
    data_dir = "data"
    sectors = []
    
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.endswith('.csv'):
                sector_name = file.replace('.csv', '')
                sectors.append(sector_name)
    
    return sorted(sectors)

def get_idx_tickers(sector="All"):
    """Get tickers from specified sector file"""
    ticker_file = f"data/{sector}.csv"
    
    if not os.path.exists(ticker_file):
        raise FileNotFoundError(f"Sector file not found: {ticker_file}")
    
    df = pd.read_csv(ticker_file)

    # Find ticker column dynamically
    ticker_col = next(
        (c for c in df.columns if "Kode" in c or "Saham" in c or "Ticker" in c),
        None
    )

    if ticker_col is None:
        raise RuntimeError("Ticker column not found in Excel file")

    tickers = (
        df[ticker_col]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    # Convert to Yahoo Finance format
    return [f"{t}.JK" for t in tickers]
