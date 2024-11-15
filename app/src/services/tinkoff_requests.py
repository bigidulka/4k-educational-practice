# File path: src/services/tinkoff_requests.py

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from tinkoff.invest import (
    AsyncClient,
    CandleInterval,
    InstrumentIdType,
    Quotation,
    HistoricCandle,
)
from tinkoff.invest.utils import now
from tinkoff.invest.exceptions import AioRequestError
import pandas as pd
import os
from fastapi import APIRouter, HTTPException
from statistics import median
from typing import Optional, List, Dict, Any

# Получение токена из переменных окружения или установка вручную
TOKEN = "t.mW7xlCY9XgIU6DztPR-kA3RNKqqiT-ALUHoctPusUmsPsufYS-EuPXdEUaBH6glIjxvJTU1ZgytuclR8_s9qVQ"

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Сопоставление интервалов
INTERVAL_MAPPING = {
    "1m": CandleInterval.CANDLE_INTERVAL_1_MIN,
    "5m": CandleInterval.CANDLE_INTERVAL_5_MIN,
    "15m": CandleInterval.CANDLE_INTERVAL_15_MIN,
    "1h": CandleInterval.CANDLE_INTERVAL_HOUR,
    "1d": CandleInterval.CANDLE_INTERVAL_DAY,
    "1w": CandleInterval.CANDLE_INTERVAL_WEEK,
    "1M": CandleInterval.CANDLE_INTERVAL_MONTH,
}

# Сопоставление рынков
MARKET_MAPPING = {
    "stock": "share",
    "etf": "etf",
    "bond": "bond",
    "currency": "currency",
    "future": "future",
}

# Функция для преобразования Quotation в float
def quotation_to_float(quotation: Quotation) -> float:
    return quotation.units + quotation.nano / 1e9

async def get_all_tickers() -> List[Dict[str, str]]:
    """
    Получает список всех доступных тикеров акций на Tinkoff.

    Returns:
        List[Dict[str, str]]: Список словарей с тикерами акций и их FIGI.
    """
    async with AsyncClient(TOKEN) as client:
        response = await client.instruments.shares()
        tickers = [
            {"ticker": instrument.ticker, "figi": instrument.figi, "name": instrument.name}
            for instrument in response.instruments
        ]
    return tickers

# Асинхронная функция для получения исторических данных
async def fetch_data(figi: str, interval: CandleInterval, from_: datetime, to: datetime) -> pd.DataFrame:
    async with AsyncClient(TOKEN) as client:
        candles = []
        try:
            async for candle in client.get_all_candles(
                figi=figi,
                from_=from_,
                to=to,
                interval=interval,
            ):
                candles.append(candle)
        except AioRequestError as e:
            logger.error(f"Ошибка при получении данных по FIGI {figi}: {e}")
            return pd.DataFrame()

    # Преобразование свечей в DataFrame
    data = []
    for candle in candles:
        data.append({
            "time": candle.time,
            "open": quotation_to_float(candle.open),
            "high": quotation_to_float(candle.high),
            "low": quotation_to_float(candle.low),
            "close": quotation_to_float(candle.close),
            "volume": candle.volume,
        })
    df = pd.DataFrame(data)
    df.set_index("time", inplace=True)
    return df

# Асинхронная функция для получения информации об инструменте
async def fetch_info(figi: str) -> Dict[str, Any]:
    async with AsyncClient(TOKEN) as client:
        try:
            response = await client.instruments.get_instrument_by(
                id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                id=figi,
            )
            instrument = response.instrument
            info = {
                "figi": instrument.figi,
                "ticker": instrument.ticker,
                "class_code": instrument.class_code,
                "isin": instrument.isin,
                "lot": instrument.lot,
                "currency": instrument.currency,
                "name": instrument.name,
                "type": instrument.instrument_type,
            }
            return info
        except AioRequestError as e:
            logger.error(f"Ошибка при получении информации по FIGI {figi}: {e}")
            return {}

# Асинхронная функция для получения текущих данных и информации об инструменте
async def get_current_data(market: str, symbol: str, interval: str = "1d") -> Optional[Dict[str, Any]]:
    try:
        figi = await map_market_to_figi(market.lower(), symbol)
        logger.info(f"Используемый FIGI: {figi}")

        if figi:
            # Получаем данные за последний день
            to_date = now()
            from_date = to_date - timedelta(days=1)
            interval_tinkoff = INTERVAL_MAPPING.get(interval, CandleInterval.CANDLE_INTERVAL_DAY)

            # Получаем данные и информацию об инструменте параллельно
            data_task = fetch_data(figi, interval_tinkoff, from_date, to_date)
            info_task = fetch_info(figi)
            data, info = await asyncio.gather(data_task, info_task)

            if not data.empty:
                latest_data = data.tail(1).to_dict(orient="records")[0]
                latest_data.update({"info": info})
                return latest_data
            else:
                logger.warning(f"Нет данных для FIGI: {figi}")
                return None
        else:
            logger.warning(f"Неподдерживаемый рынок или символ: {market}, {symbol}")
            return None

    except Exception as e:
        logger.error(f"Ошибка в get_current_data: {e}")
        return None

# Асинхронная функция для получения исторических данных
async def get_historical_data(
    market: str,
    symbol: str,
    from_date: str,
    to_date: str,
    client_timezone: str,
    interval: str = "1d"
) -> Optional[List[Dict[str, Any]]]:
    try:
        figi = await map_market_to_figi(market.lower(), symbol)
        logger.info(f"Используемый FIGI: {figi}")

        if figi:
            from_datetime = datetime.strptime(from_date, "%Y-%m-%d")
            to_datetime = datetime.strptime(to_date, "%Y-%m-%d")
            interval_tinkoff = INTERVAL_MAPPING.get(interval, CandleInterval.CANDLE_INTERVAL_DAY)
            data = await fetch_data(figi, interval_tinkoff, from_datetime, to_datetime)
            if not data.empty:
                try:
                    # Проверяем, содержит ли индекс информацию о часовом поясе
                    if data.index.tzinfo is None or data.index.tz is None:
                        # Если нет, локализуем в UTC и конвертируем
                        data.index = data.index.tz_localize('UTC').tz_convert(client_timezone)
                    else:
                        # Если уже содержит, просто конвертируем
                        data.index = data.index.tz_convert(client_timezone)
                except Exception as tz_error:
                    logger.error(f"Ошибка при конвертации часового пояса: {tz_error}")
                    raise ValueError(f"Некорректный часовой пояс: {client_timezone}")

                # Преобразуем данные в список словарей
                return data.reset_index().to_dict(orient='records')
            else:
                logger.warning(f"Нет данных для FIGI: {figi}")
                return None
        else:
            logger.warning(f"Неподдерживаемый рынок или символ: {market}, {symbol}")
            return None

    except Exception as e:
        logger.error(f"Ошибка в get_historical_data: {e}")
        return None

# Функция для сопоставления рынка и символа с FIGI
async def map_market_to_figi(market: str, symbol: str) -> Optional[str]:
    async with AsyncClient(TOKEN) as client:
        try:
            instrument_type = MARKET_MAPPING.get(market)
            if not instrument_type:
                logger.warning(f"Неподдерживаемый тип рынка: {market}")
                return None

            instruments_service = client.instruments
            search_method = getattr(instruments_service, f"{instrument_type}s")
            instruments_response = await search_method()
            for instrument in instruments_response.instruments:
                if instrument.ticker == symbol:
                    return instrument.figi
            logger.warning(f"Инструмент с символом {symbol} не найден на рынке {market}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при поиске FIGI для {symbol}: {e}")
            return None

async def generate_recommendation_based_on_history(
    symbol: str, historical_data: List[Dict[str, Any]]
) -> Dict[str, str]:
    """
    Генерирует рекомендацию на основе исторических данных акции.
    
    Параметры:
        symbol (str): Тикер символа.
        historical_data (List[Dict[str, Any]]): Список исторических записей данных.
    
    Returns:
        dict: Сгенерированная рекомендация и пояснение.
    """
    try:
        # Преобразуем исторические данные в DataFrame для удобства обработки
        df = pd.DataFrame(historical_data)
        
        # Проверяем, достаточно ли данных для анализа
        if df.empty or len(df) < 2:
            return {
                "symbol": symbol,
                "recommendation": "Удержание",
                "message": "Недостаточно исторических данных для генерации рекомендации."
            }
        
        # Рассчитываем уровни поддержки и сопротивления
        support_level, resistance_level = calculate_support_resistance(df)
        
        # Получаем текущую цену закрытия
        current_price = df['close'].iloc[-1]
        
        # Генерируем рекомендацию на основе текущей цены и уровней
        if support_level and current_price <= support_level:
            recommendation = "Покупка"
            message = f"Текущая цена ({current_price}) близка к уровню поддержки ({support_level}). Рекомендуется покупка."
        elif resistance_level and current_price >= resistance_level:
            recommendation = "Продажа"
            message = f"Текущая цена ({current_price}) достигла уровня сопротивления ({resistance_level}). Рекомендуется продажа."
        else:
            recommendation = "Удержание"
            message = "Текущая цена не близка ни к уровню поддержки, ни к уровню сопротивления. Рекомендуется удержание."
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "support_level": support_level,
            "resistance_level": resistance_level,
            "recommendation": recommendation,
            "message": message
        }
    
    except Exception as e:
        logger.error(f"Ошибка в generate_recommendation_based_on_history: {e}")
        return {
            "symbol": symbol,
            "recommendation": "Удержание",
            "message": "Произошла ошибка при генерации рекомендации."
        }

def calculate_support_resistance(df: pd.DataFrame):
    """
    Рассчитывает уровни поддержки и сопротивления на основе исторических данных.
    
    Параметры:
        df (pd.DataFrame): DataFrame с историческими данными.
    
    Returns:
        Tuple[Optional[float], Optional[float]]: Уровень поддержки и уровень сопротивления.
    """
    try:
        # Используем медиану максимальных и минимальных цен за период
        support_level = median(df['low'])
        resistance_level = median(df['high'])
        
        return support_level, resistance_level
    except Exception as e:
        logger.error(f"Ошибка в calculate_support_resistance: {e}")
        return None, None