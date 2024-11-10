import yfinance as yf
import time

# Список тикеров для 100 активов
tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "JPM", "V", "JNJ",
    "WMT", "PG", "MA", "DIS", "HD", "PYPL", "NFLX", "PEP", "KO", "MRK",
    "NKE", "T", "BA", "XOM", "INTC", "IBM", "ORCL", "CVX", "PFE", "CSCO",
    "ABT", "VZ", "CMCSA", "ADBE", "QCOM", "MCD", "BMY", "LLY", "ABBV", "MDT",
    "TMO", "HON", "UNH", "ACN", "DHR", "TXN", "PM", "AMGN", "SBUX", "CAT",
    "LMT", "AXP", "LOW", "BKNG", "UPS", "SPGI", "GS", "MMM", "SCHW", "INTU",
    "ISRG", "GE", "MO", "BLK", "ADP", "DUK", "NOW", "VRTX", "CI", "DE",
    "ANTM", "ZTS", "COST", "SYK", "CHTR", "USB", "CL", "ICE", "MDLZ", "CVS",
    "PLD", "ECL", "NEE", "ATVI", "FDX", "SO", "ITW", "D", "STZ", "APD",
    "TGT", "AON", "NSC", "WM", "REGN", "ADI", "MET", "AIG", "CME", "ROP"
]

# Загружаем данные для всех тикеров
stocks = yf.Tickers(tickers)

# Словарь для хранения рыночной капитализации каждого тикера
market_caps = {}

# Проходим по каждому тикеру и получаем рыночную капитализацию
for ticker in tickers:
    market_cap = stocks.tickers[ticker].info
    market_caps[ticker] = market_cap
    print(f"Рыночная капитализация компании {ticker}: {market_cap}")

# Вывод результата
print("\nРыночные капитализации всех 100 активов:")
for ticker, cap in market_caps.items():
    print(f"{ticker}: {cap}")
