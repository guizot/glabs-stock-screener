import yfinance as yf
import pandas as pd

DEBUG = False


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

        required_cols = {"Open", "High", "Close", "Volume"}
        if not required_cols.issubset(df.columns):
            return None

        if len(df) < 25:
            if DEBUG:
                print(f"[DEBUG] {ticker}: insufficient data ({len(df)} rows)")
            return None

        close = df["Close"]
        volume = df["Volume"]
        high = df["High"]

        # ─────────────────────────────
        # INDICATORS (NO LOOK-AHEAD)
        # ─────────────────────────────
        ma5 = close.rolling(5).mean().iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        avg_volume_5d = volume.rolling(5).mean().iloc[-2]

        last_close = close.iloc[-1]
        prev_close = close.iloc[-2]
        volume_today = volume.iloc[-1]
        high_today = high.iloc[-1]

        if any(pd.isna(x) for x in [ma5, ma20, avg_volume_5d]):
            return None

        value_today = last_close * volume_today
        daily_change = (last_close / prev_close - 1) * 100

        # ─────────────────────────────
        # RULES — STAGE 1 + STAGE 2
        # ─────────────────────────────
        rules = {
            # Likuiditas & uang masuk
            "volume_today_10m": volume_today > 10_000_000,
            "value_today_10b": value_today > 10_000_000_000,

            # Trend
            "close_above_ma5": last_close > ma5,
            "ma5_above_ma20": ma5 > ma20,

            # Momentum
            "volume_momentum": volume_today > avg_volume_5d,
            "daily_change_min_1pct": daily_change > 1.0,

            # Strength (anti fake breakout)
            "close_near_high": last_close > high_today * 0.97,
        }

        if DEBUG:
            print(
                f"[DEBUG] {ticker} | "
                f"Close={last_close:.2f} | "
                f"MA5={ma5:.2f} | "
                f"MA20={ma20:.2f} | "
                f"VolToday={format_volume(volume_today)} | "
                f"AvgVol5D={format_volume(avg_volume_5d)} | "
                f"Value={format_volume(value_today)} | "
                f"Change={daily_change:.2f}% | "
                f"Rules={rules}"
            )

        if all(rules.values()):
            return {
                "ticker": ticker,
                "close": round(last_close, 2),
                "ma5": round(ma5, 2),
                "ma20": round(ma20, 2),
                "volume_today": int(volume_today),
                "volume_today_fmt": format_volume(volume_today),
                "avg_volume_5d": int(avg_volume_5d),
                "avg_volume_5d_fmt": format_volume(avg_volume_5d),
                "value_today": int(value_today),
                "value_today_fmt": format_volume(value_today),
                "daily_change_pct": round(daily_change, 2),
            }

    except Exception as e:
        if DEBUG:
            print(f"[ERROR] {ticker}: {e}")

    return None
