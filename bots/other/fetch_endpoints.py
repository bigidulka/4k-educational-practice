import httpx
import re
from typing import Optional, Dict
from urllib.parse import urlencode
from config import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_response(response: httpx.Response) -> Dict:
    try:
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as http_err:
        logger.error(f"HTTP error occurred: {http_err} - {response.text}")
        return {"error": str(http_err), "details": response.text}
    except Exception as err:
        logger.error(f"Unexpected error: {err}")
        return {"error": str(err)}

async def fetch(method: str, url: str, params: Optional[Dict] = None) -> Dict:
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            logger.info(f"Calling endpoint: {method} {url} with params: {params}")
            response = await client.request(method, url, params=params)
            return handle_response(response)
    except Exception as e:
        logger.error(f"Error during {method} request to {url} with params {params}: {e}")
        return {"error": str(e)}

async def call_cryptocurrencies():
    endpoint = '/cryptocurrencies'
    url = f"{BASE_URL}{endpoint}"
    data = await fetch('GET', url)

    if "error" not in data:
        filtered_data = [crypto for crypto in data if crypto.get("symbol") in CRYPTO_TICKERS]
        logger.info(f"Filtered cryptocurrencies count: {len(filtered_data)}")
        data = filtered_data
    else:
        logger.error("Error in fetching cryptocurrencies data; skipping filtering.")

    return data

async def call_currency_crosses():
    endpoint = '/currency_crosses'
    url = f"{BASE_URL}{endpoint}"
    data = await fetch('GET', url)

    if "error" not in data:
        filtered_data = [
            cross for cross in data
            if cross.get("base") in CURRENCY_TICKERS and cross.get("second") in CURRENCY_TICKERS
        ]
        logger.info(f"Filtered currency crosses count: {len(filtered_data)}")
        data = filtered_data
    else:
        logger.error("Error in fetching currency crosses data; skipping filtering.")

    return data

async def call_historical_data(
    market: str,
    symbol: str,
    from_date: str,
    to_date: str,
    utc_offset: int = 0,
    interval: str = '1d'
):
    endpoint = f'/historical/{market}/{symbol}'
    query_params = urlencode({
        'from_date': from_date,
        'to_date': to_date,
        'utc_offset': utc_offset,
        'interval': interval
    })
    
    url = f"{BASE_URL}{endpoint}?{query_params}"
    data = await fetch('GET', url)
    return data

async def call_current_data(
    market: str,
    symbol: str,
    interval: str = '1d'
):
    endpoint = f'/current/{market}/{symbol}'
    url = f"{BASE_URL}{endpoint}"
    params = {'interval': interval}
    data = await fetch('GET', url, params)
    return data

async def call_tb_historical_data(
    symbol: str,
    from_date: str,
    to_date: str,
    utc_offset: int = 0,
    interval: str = '1d'
):
    endpoint = f'/tb_historical/{symbol}'
    url = f"{BASE_URL}{endpoint}"
    params = {
        'from_date': from_date,
        'to_date': to_date,
        'utc_offset': utc_offset,
        'interval': interval
    }
    data = await fetch('GET', url, params)
    return data

async def call_tb_current_data(
    symbol: str,
    interval: str = '1d'
):
    endpoint = f'/tb_current/{symbol}'
    url = f"{BASE_URL}{endpoint}"
    params = {'interval': interval}
    data = await fetch('GET', url, params)
    return data

def is_russian(name: str) -> bool:
    return bool(re.search('[\u0400-\u04FF]', name))

async def call_tb_tickers():
    endpoint = '/tb_tickers'
    url = f"{BASE_URL}{endpoint}"
    data = await fetch('GET', url)
    
    if not data or "error" in data:
        return data
    
    sorted_data = sorted(data, key=lambda x: not is_russian(x.get('name', '')))
    
    return sorted_data

async def call_recommendations(symbol: str):
    endpoint = f'/recommendations/{symbol}'
    url = f"{BASE_URL}{endpoint}"
    data = await fetch('GET', url)
    return data