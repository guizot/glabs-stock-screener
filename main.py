from get_idx_tickers import get_idx_tickers
from screener import screen_stock
import pandas as pd

IDX_TICKERS = get_idx_tickers()

print(f"Scanning {len(IDX_TICKERS)} IDX stocks...")

results = []

for ticker in IDX_TICKERS:
    res = screen_stock(ticker)
    if res:
        results.append(res)
        print(f"✓ {ticker} passed")

df = pd.DataFrame(results)

if not df.empty:
    df = df.sort_values("avg_volume", ascending=False)
    df.to_csv("results.csv", index=False)
    print("\nTop Results:")
    print(df.head(5))
else:
    print("No stocks passed the filter.")
