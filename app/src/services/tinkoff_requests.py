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

TOKEN = "t.mW7xlCY9XgIU6DztPR-kA3RNKqqiT-ALUHoctPusUmsPsufYS-EuPXdEUaBH6glIjxvJTU1ZgytuclR8_s9qVQ"

INTERVAL_MAPPING = {
    "1m": CandleInterval.CANDLE_INTERVAL_1_MIN,
    "5m": CandleInterval.CANDLE_INTERVAL_5_MIN,
    "15m": CandleInterval.CANDLE_INTERVAL_15_MIN,
    "1h": CandleInterval.CANDLE_INTERVAL_HOUR,
    "1d": CandleInterval.CANDLE_INTERVAL_DAY,
    "1w": CandleInterval.CANDLE_INTERVAL_WEEK,
    "1M": CandleInterval.CANDLE_INTERVAL_MONTH,
}

MARKET_MAPPING = {
    "stock": "share",
    "etf": "etf",
    "bond": "bond",
    "currency": "currency",
    "future": "future",
}

def quotation_to_float(quotation: Quotation) -> float:
    '''
    Преобразует объект Quotation в float.
    '''
    logging.debug(f"Преобразование объекта Quotation: {quotation} в float")
    return quotation.units + quotation.nano / 1e9

async def get_all_tickers() -> List[Dict[str, str]]:
    '''
    Получает список всех доступных тикеров акций на Tinkoff.
    
    Returns:
        List[Dict[str, str]]: Список словарей с тикерами акций и их FIGI.
    '''
    logging.info("Получаем список всех тикеров акций.")
    async with AsyncClient(TOKEN) as client:
        response = await client.instruments.shares()
        tickers = [
            {"ticker": instrument.ticker, "figi": instrument.figi, "name": instrument.name}
            for instrument in response.instruments
        ]
    logging.info(f"Получено {len(tickers)} тикеров.")
    return tickers

async def fetch_data(figi: str, interval: CandleInterval, from_: datetime, to: datetime) -> pd.DataFrame:
    '''
    Получает исторические данные по FIGI за указанный интервал времени.

    Параметры:
        figi (str): FIGI инструмента.
        interval (CandleInterval): Интервал времени для получения данных.
        from_ (datetime): Начало периода.
        to (datetime): Конец периода.

    Returns:
        pd.DataFrame: Данные по инструменту в виде DataFrame.
    '''
    logging.info(f"Получаем данные для FIGI: {figi}, с {from_} по {to}, интервал {interval}")
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
            logging.info(f"Получено {len(candles)} свечей.")
        except AioRequestError as e:
            logging.error(f"Ошибка при получении данных по FIGI {figi}: {e}")
            return pd.DataFrame()

    data = []
    for candle in candles:
        logging.debug(f"Обрабатываем свечу: {candle}")
        data.append({
            "time": candle.time,
            "open": quotation_to_float(candle.open),
            "high": quotation_to_float(candle.high),
            "low": quotation_to_float(candle.low),
            "close": quotation_to_float(candle.close),
            "volume": candle.volume,
        })
    if data:
        df = pd.DataFrame(data)
        df.set_index("time", inplace=True)
        logging.info(f"Данные для FIGI {figi} успешно загружены.")
        return df
    else:
        logging.warning(f"Нет данных для FIGI {figi}.")
        return pd.DataFrame()

async def fetch_info(figi: str) -> Dict[str, Any]:
    '''
    Получает информацию об инструменте по FIGI.

    Параметры:
        figi (str): FIGI инструмента.

    Returns:
        dict: Информация об инструменте.
    '''
    logging.info(f"Получаем информацию для инструмента с FIGI: {figi}")
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
            logging.info(f"Информация по FIGI {figi}: {info}")
            return info
        except AioRequestError as e:
            logging.error(f"Ошибка при получении информации по FIGI {figi}: {e}")
            return {}

async def get_current_data(market: str, symbol: str, interval: str = "1d") -> Optional[Dict[str, Any]]:
    '''
    Получает текущие данные и информацию об инструменте по символу и рынку.
    
    Параметры:
        market (str): Рынок (например, "stock", "etf").
        symbol (str): Символ инструмента.
        interval (str): Интервал данных (по умолчанию "1d").
    
    Returns:
        dict: Текущие данные и информация об инструменте.
    '''
    logging.info(f"Запрос текущих данных для {market} {symbol} с интервалом {interval}")
    try:
        figi = await map_market_to_figi(market.lower(), symbol)
        logging.info(f"Используемый FIGI: {figi}")

        if figi:
            interval_tinkoff = INTERVAL_MAPPING.get(interval, CandleInterval.CANDLE_INTERVAL_DAY)
            to_date = now()
            from_date = to_date - timedelta(days=7)  # Получаем данные за последнюю неделю

            data = await fetch_data(figi, interval_tinkoff, from_date, to_date)
            if not data.empty:
                latest_candle = data.iloc[-1]
                info = await fetch_info(figi)
                result = {
                    'open': latest_candle['open'],
                    'high': latest_candle['high'],
                    'low': latest_candle['low'],
                    'close': latest_candle['close'],
                    'volume': latest_candle['volume'],
                    'info': info
                }
                logging.info(f"Данные для {symbol} получены успешно.")
                return result
            else:
                logging.warning(f"Нет данных для FIGI: {figi}")
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
    '''
    Получает исторические данные по символу и рынку за указанный период.

    Параметры:
        market (str): Рынок (например, "stock", "etf").
        symbol (str): Символ инструмента.
        from_date (str): Дата начала периода.
        to_date (str): Дата конца периода.
        client_timezone (str): Часовой пояс клиента.
        interval (str): Интервал данных (по умолчанию "1d").

    Returns:
        list: Список исторических данных.
    '''
    logging.info(f"Запрос исторических данных для {market} {symbol} с {from_date} по {to_date}, интервал {interval}")
    try:
        figi = await map_market_to_figi(market.lower(), symbol)
        logging.info(f"Используемый FIGI: {figi}")

        if figi:
            from_datetime = datetime.strptime(from_date, "%Y-%m-%d")
            to_datetime = datetime.strptime(to_date, "%Y-%m-%d")
            interval_tinkoff = INTERVAL_MAPPING.get(interval, CandleInterval.CANDLE_INTERVAL_DAY)
            data = await fetch_data(figi, interval_tinkoff, from_datetime, to_datetime)
            if not data.empty:
                try:
                    if data.index.tzinfo is None or data.index.tz is None:
                        data.index = data.index.tz_localize('UTC').tz_convert(client_timezone)
                    else:
                        data.index = data.index.tz_convert(client_timezone)
                    logging.info(f"Исторические данные для {figi} успешно загружены.")
                except Exception as tz_error:
                    logging.error(f"Ошибка при конвертации часового пояса: {tz_error}")
                    raise ValueError(f"Некорректный часовой пояс: {client_timezone}")

                return data.reset_index().to_dict(orient='records')
            else:
                logging.warning(f"Нет данных для FIGI: {figi}")
                return None
        else:
            logging.warning(f"Неподдерживаемый рынок или символ: {market}, {symbol}")
            return None

    except Exception as e:
        logging.error(f"Ошибка в get_historical_data: {e}")
        return None

async def map_market_to_figi(market: str, symbol: str) -> Optional[str]:
    '''
    Сопоставляет рынок и символ с FIGI.

    Параметры:
        market (str): Рынок.
        symbol (str): Символ инструмента.

    Returns:
        str: FIGI инструмента.
    '''
    logging.info(f"Поиск FIGI для {market} {symbol}")
    async with AsyncClient(TOKEN) as client:
        try:
            instrument_type = MARKET_MAPPING.get(market)
            if not instrument_type:
                logging.warning(f"Неподдерживаемый тип рынка: {market}")
                return None

            instruments_service = client.instruments
            search_method = getattr(instruments_service, f"{instrument_type}s")
            instruments_response = await search_method()
            for instrument in instruments_response.instruments:
                if instrument.ticker == symbol:
                    logging.info(f"Найден FIGI: {instrument.figi} для {symbol}")
                    return instrument.figi
            logging.warning(f"Инструмент с символом {symbol} не найден на рынке {market}")
            return None
        except Exception as e:
            logging.error(f"Ошибка при поиске FIGI для {symbol}: {e}")
            return None

def calculate_support_resistance(df: pd.DataFrame):
    '''
    Рассчитывает уровни поддержки и сопротивления на основе исторических данных.

    Параметры:
        df (pd.DataFrame): DataFrame с историческими данными.

    Returns:
        Tuple[Optional[float], Optional[float]]: Уровень поддержки и уровень сопротивления.
    '''
    logging.debug("Расчет уровней поддержки и сопротивления.")
    try:
        support_level = median(df['low'])
        resistance_level = median(df['high'])
        
        logging.debug(f"Уровень поддержки: {support_level}, уровень сопротивления: {resistance_level}")
        return support_level, resistance_level
    except Exception as e:
        logging.error(f"Ошибка в calculate_support_resistance: {e}")
        return None, None

async def generate_recommendation_based_on_history(
    symbol: str, historical_data: List[Dict[str, Any]]
) -> Dict[str, str]:
    '''
    Генерирует рекомендацию на основе исторических данных акции.

    Параметры:
        symbol (str): Тикер символа.
        historical_data (List[Dict[str, Any]]): Список исторических записей данных.

    Returns:
        dict: Сгенерированная рекомендация и пояснение.
    '''
    logging.info(f"Генерация рекомендации для {symbol} на основе исторических данных.")
    try:
        df = pd.DataFrame(historical_data)
        
        if df.empty or len(df) < 2:
            logging.warning("Недостаточно данных для генерации рекомендации.")
            return {
                "symbol": symbol,
                "recommendation": "Удержание",
                "message": "Недостаточно исторических данных для генерации рекомендации."
            }
        
        support_level, resistance_level = calculate_support_resistance(df)
        
        current_price = df['close'].iloc[-1]
        
        if support_level and current_price <= support_level:
            recommendation = "Покупка"
            message = f"Текущая цена ({current_price}) близка к уровню поддержки ({support_level}). Рекомендуется покупка."
        elif resistance_level and current_price >= resistance_level:
            recommendation = "Продажа"
            message = f"Текущая цена ({current_price}) достигла уровня сопротивления ({resistance_level}). Рекомендуется продажа."
        else:
            recommendation = "Удержание"
            message = "Текущая цена не близка ни к уровню поддержки, ни к уровню сопротивления. Рекомендуется удержание."
        
        logging.info(f"Рекомендация для {symbol}: {recommendation}")
        return {
            "symbol": symbol,
            "current_price": current_price,
            "support_level": support_level,
            "resistance_level": resistance_level,
            "recommendation": recommendation,
            "message": message
        }
    
    except Exception as e:
        logging.error(f"Ошибка в generate_recommendation_based_on_history: {e}")
        return {
            "symbol": symbol,
            "recommendation": "Удержание",
            "message": "Произошла ошибка при генерации рекомендации."
        }