import yfinance as yf
import pandas as pd

DEBUG = False


def _normalize_df(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def screen_stock(ticker):
    try:
        df = yf.download(
            ticker,
            period="4mo",
            interval="1d",
            progress=False,
            threads=False,
        )

        if df is None or df.empty:
            return None

        df = _normalize_df(df)

        required = {"Open", "High", "Close", "Volume"}
        if not required.issubset(df.columns):
            return None

        if len(df) < 60:
            return None

        close = df["Close"]
        volume = df["Volume"]

        # ───────────── Indicators ─────────────
        ma20 = close.rolling(20).mean().iloc[-1]
        ma50 = close.rolling(50).mean().iloc[-1]
        vol_ma20 = volume.rolling(20).mean().iloc[-1]

        last_close = close.iloc[-1]
        prev_close = close.iloc[-2]
        volume_today = volume.iloc[-1]
        prev_volume = volume.iloc[-2]

        if any(pd.isna(x) for x in [ma20, ma50, vol_ma20]):
            return None

        value_today = last_close * volume_today

        # ───────────── RULES (FROM IMAGE) ─────────────
        rules = {
            "price_min_100": last_close >= 100,
            "value_min_5b": value_today >= 5_000_000_000,
            "volume_min_10m": volume_today >= 10_000_000,
            "price_above_ma20": last_close >= ma20,
            "ma20_above_ma50": ma20 > ma50,
            "volume_spike": volume_today > 1.5 * prev_volume,
            "price_gap_8pct": last_close > 1.08 * prev_close,
            "volume_above_ma20": volume_today > vol_ma20,
        }

        if all(rules.values()):
            return {
                "ticker": ticker,
                "close": round(last_close, 2),
                "ma20": round(ma20, 2),
                "ma50": round(ma50, 2),
                "volume_today": int(volume_today),
                "value_today": int(value_today),
                "price_change_pct": round((last_close / prev_close - 1) * 100, 2),
            }

    except Exception as e:
        if DEBUG:
            print(f"[ERROR] {ticker}: {e}")

    return None
