# File path: app/services/investpy_requests.py

import investpy
import asyncio
import functools
import logging


async def run_in_executor(func, *args, **kwargs):
    """
    Асинхронное выполнение функции с использованием Loop и Executor.
    """
    loop = asyncio.get_event_loop()
    partial_func = functools.partial(func, *args, **kwargs)
    return await loop.run_in_executor(None, partial_func)


async def get_investpy_data(data_type: str):
    """
    Получение данных из investpy по указанному типу данных.
    Доступные типы данных: stocks, funds, etfs, currencies, indices, bonds, commodities, certificates, cryptocurrencies.
    """
    try:
        data_fetchers = {
            "stocks": investpy.stocks.get_stocks,
            "cryptocurrencies": investpy.crypto.get_cryptos,
            "funds": investpy.funds.get_funds,
            "etfs": investpy.etfs.get_etfs,
            "currencies": investpy.currency_crosses.get_currency_crosses,
            "indices": investpy.indices.get_indices,
            "bonds": investpy.bonds.get_bonds,
            "commodities": investpy.commodities.get_commodities,
            "certificates": investpy.certificates.get_certificates,
        }

        if data_type not in data_fetchers:
            raise ValueError(f"Неподдерживаемый тип данных: {data_type}")

        data = await run_in_executor(data_fetchers[data_type])
        return data
    except Exception as e:
        logging.error(f"Ошибка в get_investpy_data для {data_type}: {e}")
        return None