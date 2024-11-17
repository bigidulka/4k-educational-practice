API_TOKEN = '7704537041:AAGNOzRsXszQVTBYmyCdBlogGTB__jgEoEE'
DATABASE_URL = "sqlite+aiosqlite:///./data/database.db"

BASE_SETTINGS = {
    "timezone": "0",
    "base_currency": "RUB",
    "notification_frequency": "1min",
    "favorites_assets": [],
    "notification_price_change": {},
    "notification_price_level": {}
}

TIMEFRAME_SETTINGS = {
    '1d': {'interval': '5m', 'period_days': 1},
    '1w': {'interval': '15m', 'period_days': 7},
    '1mo': {'interval': '1h', 'period_days': 30},
    '1y': {'interval': '1d', 'period_days': 365},
}

FREQUENCY_MAPPING = {
    '1min': 60,
    '5min': 300,
    '10min': 600,
    '30min': 1800,
    '1h': 3600,
    '6h': 21600,
    '12h': 43200,
    '24h': 86400,
}

# BASE_URL = 'http://bigidulka2.ddns.net:8000'
BASE_URL = 'http://web:8000'

OUTPUT_DIR = 'other/data/results'

CRYPTO_TICKERS = [
    "BTC", "ETH", "USDT", "BNB", "XRP", "ADA", "SOL", "DOGE",
    "DOT", "SHIB", "LTC", "TRX", "AVAX", "LINK", "ATOM", "UNI",
    "XLM", "XMR", "XTZ", "TON"
]

CURRENCY_TICKERS = [
    "RUB", "USD", "EUR", "CNY", "GBP", "CHF", "JPY", "KZT", "BYN", "AED"
]

UTC_OFFSETS_EVEN = [
    f"{'+' if offset > 0 else ''}{offset}"
    for offset in range(-12, 15, 2) 
]
