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
        return info.get("marketCap", 0), info.get("sector", "Unknown
