import yfinance as yf
import pandas as pd

DEBUG = True


def format_volume(n: float) -> str:
    n = int(n)
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def _normalize_df(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def screen_stock(ticker):
    try:
        df = yf.download(
            ticker,
            period="3mo",
            interval="1d",
            progress=False,
            threads=False,
        )

        if df is None or df.empty:
            return None

        df = _normalize_df(df)

        if not {"Close", "Volume"}.issubset(df.columns):
            return None

        if len(df) < 25:
            if DEBUG:
                print(f"[DEBUG] {ticker}: insufficient data ({len(df)} rows)")
            return None

        close = df["Close"]
        volume = df["Volume"]

        # ─────────────────────────────
        # Indicators
        # ─────────────────────────────
        avg_volume = volume.rolling(20).mean().iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]

        last_close = close.iloc[-1]
        close_5d_ago = close.iloc[-6]

        if pd.isna(avg_volume) or pd.isna(ma20):
            return None

        # ─────────────────────────────
        # RULES
        # ─────────────────────────────
        rules = {
            "liquidity": avg_volume > 100_000_000,
            "trend": last_close > ma20,
            "price_filter": last_close > 50,
            "momentum": last_close > close_5d_ago,
        }

        if DEBUG:
            print(
                f"[DEBUG] {ticker} | "
                f"Vol={format_volume(avg_volume)} | "
                f"Close={last_close:.2f} | "
                f"MA20={ma20:.2f} | "
                f"Rules={rules}"
            )

        if all(rules.values()):
            return {
                "ticker": ticker,
                "avg_volume": int(avg_volume),
                "avg_volume_fmt": format_volume(avg_volume),
                "last_close": round(last_close, 2),
                "ma20": round(ma20, 2),
                "momentum_5d": round(last_close - close_5d_ago, 2),
                # "reason": "High Volume + Uptrend + Momentum",
            }

    except Exception as e:
        if DEBUG:
            print(f"[ERROR] {ticker}: {e}")

    return None
