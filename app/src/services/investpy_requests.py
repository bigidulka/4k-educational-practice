# File path: src/services/investpy_requests.py
import investpy
import asyncio
import functools
import logging
from typing import Optional, Any
import pandas as pd


async def run_in_executor(func: Any, *args: Any, **kwargs: Any) -> Any:
    """
    Асинхронно выполняет функцию с использованием цикла событий и исполнителя.

    Параметры:
        func (Callable): Функция для выполнения.
        *args: Аргументы для функции.
        **kwargs: Именованные аргументы для функции.

    Returns:
        Any: Результат выполнения функции.
    """
    loop = asyncio.get_event_loop()
    partial_func = functools.partial(func, *args, **kwargs)
    return await loop.run_in_executor(None, partial_func)


async def get_stocks() -> Optional[pd.DataFrame]:
    """
    Получает список акций с помощью investpy.

    Returns:
        Optional[pd.DataFrame]: Данные акций или None в случае ошибки.
    """
    try:
        stocks = await run_in_executor(investpy.stocks.get_stocks)
        return stocks
    except Exception as e:
        logging.error(f"Ошибка в get_stocks: {e}")
        return None


async def get_funds() -> Optional[pd.DataFrame]:
    """
    Получает список фондов с помощью investpy.

    Returns:
        Optional[pd.DataFrame]: Данные фондов или None в случае ошибки.
    """
    try:
        funds = await run_in_executor(investpy.funds.get_funds)
        return funds
    except Exception as e:
        logging.error(f"Ошибка в get_funds: {e}")
        return None


async def get_etfs() -> Optional[pd.DataFrame]:
    """
    Получает список ETF с помощью investpy.

    Returns:
        Optional[pd.DataFrame]: Данные ETF или None в случае ошибки.
    """
    try:
        etfs = await run_in_executor(investpy.etfs.get_etfs)
        return etfs
    except Exception as e:
        logging.error(f"Ошибка в get_etfs: {e}")
        return None


async def get_currency_crosses() -> Optional[pd.DataFrame]:
    """
    Получает список валютных пар с помощью investpy.

    Returns:
        Optional[pd.DataFrame]: Данные валютных пар или None в случае ошибки.
    """
    try:
        currencies = await run_in_executor(investpy.currency_crosses.get_currency_crosses)
        return currencies
    except Exception as e:
        logging.error(f"Ошибка в get_currency_crosses: {e}")
        return None


async def get_indices() -> Optional[pd.DataFrame]:
    """
    Получает список индексов с помощью investpy.

    Returns:
        Optional[pd.DataFrame]: Данные индексов или None в случае ошибки.
    """
    try:
        indices = await run_in_executor(investpy.indices.get_indices)
        return indices
    except Exception as e:
        logging.error(f"Ошибка в get_indices: {e}")
        return None


async def get_bonds() -> Optional[pd.DataFrame]:
    """
    Получает список облигаций с помощью investpy.

    Returns:
        Optional[pd.DataFrame]: Данные облигаций или None в случае ошибки.
    """
    try:
        bonds = await run_in_executor(investpy.bonds.get_bonds)
        return bonds
    except Exception as e:
        logging.error(f"Ошибка в get_bonds: {e}")
        return None


async def get_commodities() -> Optional[pd.DataFrame]:
    """
    Получает список сырьевых товаров с помощью investpy.

    Returns:
        Optional[pd.DataFrame]: Данные сырьевых товаров или None в случае ошибки.
    """
    try:
        commodities = await run_in_executor(investpy.commodities.get_commodities)
        return commodities
    except Exception as e:
        logging.error(f"Ошибка в get_commodities: {e}")
        return None


async def get_certificates() -> Optional[pd.DataFrame]:
    """
    Получает список сертификатов с помощью investpy.

    Returns:
        Optional[pd.DataFrame]: Данные сертификатов или None в случае ошибки.
    """
    try:
        certificates = await run_in_executor(investpy.certificates.get_certificates)
        return certificates
    except Exception as e:
        logging.error(f"Ошибка в get_certificates: {e}")
        return None


async def get_cryptocurrencies() -> Optional[pd.DataFrame]:
    """
    Получает список криптовалют с помощью investpy.

    Returns:
        Optional[pd.DataFrame]: Данные криптовалют или None в случае ошибки.
    """
    try:
        cryptocurrencies = await run_in_executor(investpy.crypto.get_cryptos)
        return cryptocurrencies
    except Exception as e:
        logging.error(f"Ошибка в get_cryptocurrencies: {e}")
        return None