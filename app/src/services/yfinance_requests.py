# File path: app/services/yfinance_requests.py

import yfinance as yf
import asyncio
import logging


async def fetch_data(ticker_symbol: str, period: str = "1d"):
    """Асинхронное получение данных с использованием yfinance."""
    ticker = yf.Ticker(ticker_symbol)
    data = await asyncio.to_thread(ticker.history, period=period)
    return data


async def get_current_data(market: str, symbol: str):
    """
    Получение текущих данных для различных типов рынков: акции, криптовалюты, валютные пары, индексы, сырьевые товары.
    """
    try:
        # Определение соответствующего тикера для каждой категории рынка
        ticker_symbol = map_market_to_symbol(market.lower(), symbol)

        if ticker_symbol:
            data = await fetch_data(ticker_symbol)
            return data.tail(1).to_dict(orient="records")[0] if not data.empty else None
        else:
            logging.warning(f"Неподдерживаемый рынок или символ: {market}, {symbol}")
            return None

    except Exception as e:
        logging.error(f"Ошибка в get_current_data: {e}")
        return None


async def get_historical_data(market: str, symbol: str, from_date: str, to_date: str):
    """
    Получение исторических данных для всех поддерживаемых рынков: акции, криптовалюты, валютные пары, индексы, сырьевые товары.
    """
    try:
        # Определение соответствующего тикера для каждой категории рынка
        ticker_symbol = map_market_to_symbol(market.lower(), symbol)

        if ticker_symbol:
            historical_data = await fetch_historical_data(ticker_symbol, from_date, to_date)
            return historical_data if historical_data is not None else None
        else:
            logging.warning(f"Неподдерживаемый рынок или символ: {market}, {symbol}")
            return None

    except Exception as e:
        logging.error(f"Ошибка в get_historical_data: {e}")
        return None


async def fetch_historical_data(symbol: str, from_date: str, to_date: str):
    """
    Асинхронное получение исторических данных с использованием yfinance.
    """
    try:
        historical_data = await asyncio.to_thread(yf.download, symbol, start=from_date, end=to_date)
        return historical_data if not historical_data.empty else None
    except Exception as e:
        logging.error(f"Ошибка при получении исторических данных для {symbol}: {e}")
        return None


def map_market_to_symbol(market: str, symbol: str) -> str:
    """
    Маппинг категорий рынка на формат тикера, который понимает yfinance.
    """
    market_map = {
        "stock": symbol,  # Прямое использование символа для акций
        "crypto": f"{symbol}-USD",  # Криптовалюты
        "currency": f"{symbol}=X",  # Валютные пары
        "index": f"^{symbol}",  # Индексы, например, '^GSPC' для S&P 500
        "commodity": symbol,  # Сырьевые товары, если символ доступен в yfinance
        # Добавление дополнительных типов по мере необходимости
    }

    return market_map.get(market, None)
