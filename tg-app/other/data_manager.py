import json
import asyncio
import aiohttp
from datetime import datetime
import re

from utils import *
from data import *

# File path: src/client.py
import httpx
import asyncio
from typing import List, Dict, Optional

API_BASE_URL = "http://localhost:8000"  # Замените на реальный URL, если он отличается

# Хранимые данные для автообновления
stocks_data = []
cryptocurrencies_data = []
currency_crosses_data = []

# Функции для запроса данных с сервера

async def fetch_stocks(country: Optional[str] = None) -> List[Dict]:
    """
    Запрашивает список акций с возможной фильтрацией по стране.
    """
    params = {'country': country} if country else {}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/stocks", params=params)
        response.raise_for_status()
        return response.json()


async def fetch_cryptocurrencies() -> List[Dict]:
    """
    Запрашивает список криптовалют.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/cryptocurrencies")
        response.raise_for_status()
        return response.json()


async def fetch_currency_crosses() -> List[Dict[str, str]]:
    """
    Запрашивает список валютных пар.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/currency_crosses")
        response.raise_for_status()
        return response.json()


# Функции для автообновления данных

async def update_stocks_data():
    """
    Обновляет данные по акциям и сохраняет в глобальной переменной.
    """
    global stocks_data
    stocks_data = await fetch_stocks()
    print("Stocks data updated")


async def update_cryptocurrencies_data():
    """
    Обновляет данные по криптовалютам и сохраняет в глобальной переменной.
    """
    global cryptocurrencies_data
    cryptocurrencies_data = await fetch_cryptocurrencies()
    print("Cryptocurrencies data updated")


async def update_currency_crosses_data():
    """
    Обновляет данные по валютным парам и сохраняет в глобальной переменной.
    """
    global currency_crosses_data
    currency_crosses_data = await fetch_currency_crosses()
    print("Currency crosses data updated")


async def auto_update_data(interval: int = 100):
    """
    Периодически обновляет данные с заданным интервалом в секундах.
    """
    while True:
        await update_stocks_data()
        await update_cryptocurrencies_data()
        await update_currency_crosses_data()
        await asyncio.sleep(interval)
