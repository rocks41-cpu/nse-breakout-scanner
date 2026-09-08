import pandas as pd
import yfinance as yf
import os

# -----------------------------
# CONFIGURATION
# -----------------------------
MIN_MCAP = 10_000_00_00_00   # 10,000 crore
MIN_VOLUME = 100_000

MODES = {
    "Aggressive": {"lookback": 10, "vol_mult": 1.2},
    "Balanced": {"lookback": 20, "vol_mult": 1.5},
    "Conservative": {"lookback": 50, "vol_mult": 2.0},
}

SECTORS_ALLOWED = [
    "Financial Services", "IT", "Energy", "FMCG", "Pharma",
    "Auto", "Metals", "Infra", "Chemicals"
]

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def get_market_cap_and_sector(symbol):
    try:
        info = yf.Ticker(symbol + ".NS").info
        return info.get("marketCap", 0), info.get("sector", "Unknown")
    except Exception:
        return 0, "Unknown"

def detect_breakout(df, mode):
    cfg = MODES[mode]

    highs = df["High"].rolling(cfg["lookback"]).max().shift(1)
    lows = df["Low"].rolling(cfg["lookback"]).min().shift(1)
    vol_sma = df["Volume"].rolling(20).mean()

    latest = df.iloc[-1]
    prev_high = highs.iloc[-1]
    prev_low = lows.iloc[-1]
    avg_vol = vol_sma.iloc[-1]

    bullish = bool(latest["Close"] > prev_high and latest["Volume"] > cfg["vol_mult"] * avg_vol)
    bearish = bool(latest["Close"] < prev_low and latest["Volume"] > cfg["vol_mult"] * avg_vol)

    return bullish, bearish

# -----------------------------
# MAIN SCANNER
# -----------------------------
symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "LT", "SBIN"]

results = []

for symbol in symbols:
    df = yf.download(symbol + ".NS", period="300d", interval="1d")
    if df.empty:
        continue

    # Liquidity filters
    mcap, sector = get_market_cap_and_sector(symbol)
    latest_volume = df["Volume"].iloc[-1]

    if mcap < MIN_MCAP or latest_volume < MIN_VOLUME or sector not in SECTORS_ALLOWED:
        continue

    # Weekly timeframe
    weekly = df.resample("W").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum"
    })

    for mode in MODES.keys():
        daily_bull, daily_bear = detect_breakout(df, mode)
        weekly_bull, weekly_bear = detect_breakout(weekly, mode)

        # Multi-timeframe confirmation
        if daily_bull and weekly_bull:
            results.append({
                "Symbol": symbol,
                "Mode": mode,
                "Type": "Bullish",
                "Close": df["Close"].iloc[-1],
                "Volume": latest_volume,
                "Sector": sector,
                "Market Cap (Cr)": round(mcap / 1e7, 2)
            })

        if daily_bear and weekly_bear:
            results.append({
                "Symbol": symbol,
                "Mode": mode,
                "Type": "Bearish",
                "Close": df["Close"].iloc[-1],
                "Volume": latest_volume,
                "Sector": sector,
                "Market Cap (Cr)": round(mcap / 1e7, 2)
            })

# -----------------------------
# SAVE TO EXCEL
# -----------------------------
os.makedirs("data", exist_ok=True)
df_out = pd.DataFrame(results)
df_out.to_excel("data/breakouts.xlsx", index=False)
print("✅ Breakout scan completed successfully.")
