# File path: src/services/yfinance_requests.py
import yfinance as yf
import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, List, Dict, Any
import pandas as pd


# Асинхронная функция для получения исторических данных по тикеру
async def fetch_data(ticker_symbol: str, interval: str = "1d") -> pd.DataFrame:
    """
    Асинхронно получает последние данные для указанного тикера.

    Параметры:
        ticker_symbol (str): Символ тикера, например, "AAPL" для Apple.
        interval (str): Интервал данных (например, "1m", "5m", "1d").

    Returns:
        pd.DataFrame: Последние данные по тикеру за указанный интервал.
    """
    ticker = yf.Ticker(ticker_symbol)
    data = await asyncio.to_thread(ticker.history, interval=interval)
    return data

# Асинхронная функция для получения информации о тикере
async def fetch_info(ticker_symbol: str) -> Dict[str, Any]:
    """
    Асинхронно получает информацию о тикере.

    Параметры:
        ticker_symbol (str): Символ тикера, например, "AAPL" для Apple.

    Returns:
        dict: Информация о тикере.
    """
    ticker = yf.Ticker(ticker_symbol)
    info = await asyncio.to_thread(lambda: ticker.info)
    return info

# Основная функция для получения текущих данных и информации о тикере
async def get_current_data(market: str, symbol: str, interval: str = "1d") -> Optional[Dict[str, Any]]:
    """
    Получает текущие данные и информацию о тикере для указанного рынка и символа.

    Параметры:
        market (str): Тип рынка (например, "stock", "crypto").
        symbol (str): Символ тикера на указанном рынке.
        interval (str): Интервал данных (например, "1m", "5m", "1d").

    Returns:
        dict или None: Последняя запись данных по тикеру и информация о тикере или None, если данные отсутствуют.
    """
    try:
        ticker_symbol = map_market_to_symbol(market.lower(), symbol)
        logging.info(f"Используемый тикер: {ticker_symbol}")

        if ticker_symbol:
            # Получаем исторические данные и информацию о тикере параллельно
            data, info = await asyncio.gather(fetch_data(ticker_symbol, interval=interval), fetch_info(ticker_symbol))

            if not data.empty:
                # Преобразуем индекс в UTC для унификации
                if data.index.tz is None:
                    data.index = data.index.tz_localize('UTC')
                else:
                    data.index = data.index.tz_convert('UTC')

                # Получаем последние данные и добавляем информацию о тикере
                latest_data = data.tail(1).to_dict(orient="records")[0]
                latest_data.update({"info": info})

                return latest_data
            else:
                logging.warning(f"Нет данных для тикера: {ticker_symbol}")
                return None
        else:
            logging.warning(f"Неподдерживаемый рынок или символ: {market}, {symbol}")
            return None

    except Exception as e:
        logging.error(f"Ошибка в get_current_data: {e}")
        return None


async def get_historical_data(
    market: str,
    symbol: str,
    from_date: str,
    to_date: str,
    client_timezone: str,
    interval: str = "1d"
) -> Optional[List[Dict[str, Any]]]:
    try:
        ticker_symbol = map_market_to_symbol(market.lower(), symbol)
        logging.info(f"Используемый тикер: {ticker_symbol}")

        if ticker_symbol:
            historical_data = await fetch_historical_data(ticker_symbol, from_date, to_date, interval)
            if historical_data is not None and not historical_data.empty:
                try:
                    if historical_data.index.tz is None:
                        historical_data.index = historical_data.index.tz_localize('UTC').tz_convert(client_timezone)
                    else:
                        historical_data.index = historical_data.index.tz_convert(client_timezone)
                except Exception as tz_error:
                    logging.error(f"Ошибка при конвертации часового пояса: {tz_error}")
                    raise ValueError(f"Некорректный часовой пояс: {client_timezone}")

                # Flatten the MultiIndex columns
                historical_data.columns = [
                    '_'.join(filter(None, map(str, col))).strip()
                    if isinstance(col, tuple) else col
                    for col in historical_data.columns.values
                ]

                return historical_data.reset_index().to_dict(orient='records')
            else:
                logging.warning(f"Нет данных для тикера: {ticker_symbol}")
                return None
        else:
            logging.warning(f"Неподдерживаемый рынок или символ: {market}, {symbol}")
            return None

    except ValueError as ve:
        logging.error(f"Ошибка в get_historical_data: {ve}")
        raise ve
    except Exception as e:
        logging.error(f"Ошибка в get_historical_data: {e}")
        return None

async def fetch_historical_data(
    symbol: str,
    from_date: str,
    to_date: str,
    interval: str = "1d"
) -> Optional[pd.DataFrame]:
    """
    Асинхронно получает исторические данные для указанного тикера.

    Параметры:
        symbol (str): Символ тикера.
        from_date (str): Начальная дата в формате "YYYY-MM-DD".
        to_date (str): Конечная дата в формате "YYYY-MM-DD".
        interval (str): Интервал данных (например, "1m", "5m", "1d").

    Returns:
        pd.DataFrame или None: Исторические данные или None, если данные отсутствуют.
    """
    try:
        historical_data = await asyncio.to_thread(
            yf.download,
            symbol,
            start=from_date,
            end=to_date,
            interval=interval,
            progress=False
        )
        return historical_data if not historical_data.empty else None
    except Exception as e:
        logging.error(f"Ошибка при получении исторических данных для {symbol}: {e}")
        return None


def map_market_to_symbol(market: str, symbol: str) -> Optional[str]:
    """
    Преобразует тип рынка и символ в формат тикера, понятный yfinance.

    Поддерживаемые рынки:
        - Акции ("stock")
        - Криптовалюты ("crypto")
        - Валютные пары ("currency")
        - Индексы ("index")
        - Сырьевые товары ("commodity")

    Параметры:
        market (str): Тип рынка.
        symbol (str): Символ тикера.

    Returns:
        str или None: Форматированный тикер или None, если рынок не поддерживается.
    """
    market_map = {
        "stock": symbol,  # Прямое использование символа для акций
        "crypto": f"{symbol}-USD",  # Криптовалюты
        "currency": f"{symbol}=X",  # Валютные пары
        # "index": f"^{symbol}",  # Индексы, например, '^GSPC' для S&P 500
        # "commodity": symbol,  # Сырьевые товары, если символ доступен в yfinance
    }

    return market_map.get(market, None)