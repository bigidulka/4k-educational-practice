# File path: tests/services/test_investpy_requests.py
import pytest
import asyncio
import json
from unittest.mock import patch, MagicMock
from src.services.investpy_requests import get_investpy_data
import pandas as pd

# Путь для сохранения тестовых данных
TEST_OUTPUTS_PATH = 'tests/test_outputs/'

def save_test_data(filename, data):
    """Сохраняет данные в формате JSON."""
    with open(f'{TEST_OUTPUTS_PATH}{filename}', 'w', encoding='utf-8') as f:
        json.dump(data, f, default=str, ensure_ascii=False, indent=4)

@pytest.mark.asyncio
async def test_get_stocks():
    data = await get_investpy_data("stocks")
    assert isinstance(data, pd.DataFrame), f"Expected DataFrame, got {type(data)}"
    assert not data.empty, "Data should not be empty"
    save_test_data('stocks.json', data.to_dict())

@pytest.mark.asyncio
async def test_get_funds():
    data = await get_investpy_data("funds")
    assert isinstance(data, pd.DataFrame), f"Expected DataFrame, got {type(data)}"
    assert not data.empty, "Data should not be empty"
    save_test_data('funds.json', data.to_dict())

@pytest.mark.asyncio
async def test_get_etfs():
    data = await get_investpy_data("etfs")
    assert isinstance(data, pd.DataFrame), f"Expected DataFrame, got {type(data)}"
    assert not data.empty, "Data should not be empty"
    save_test_data('etfs.json', data.to_dict())

@pytest.mark.asyncio
async def test_get_currency_crosses():
    data = await get_investpy_data("currencies")
    assert isinstance(data, pd.DataFrame), f"Expected DataFrame, got {type(data)}"
    assert not data.empty, "Data should not be empty"
    save_test_data('currency_crosses.json', data.to_dict())

@pytest.mark.asyncio
async def test_get_indices():
    data = await get_investpy_data("indices")
    assert isinstance(data, pd.DataFrame), f"Expected DataFrame, got {type(data)}"
    assert not data.empty, "Data should not be empty"
    save_test_data('indices.json', data.to_dict())

@pytest.mark.asyncio
async def test_get_bonds():
    data = await get_investpy_data("bonds")
    assert isinstance(data, pd.DataFrame), f"Expected DataFrame, got {type(data)}"
    assert not data.empty, "Data should not be empty"
    save_test_data('bonds.json', data.to_dict())

@pytest.mark.asyncio
async def test_get_commodities():
    data = await get_investpy_data("commodities")
    assert isinstance(data, pd.DataFrame), f"Expected DataFrame, got {type(data)}"
    assert not data.empty, "Data should not be empty"
    save_test_data('commodities.json', data.to_dict())

@pytest.mark.asyncio
async def test_get_certificates():
    data = await get_investpy_data("certificates")
    assert isinstance(data, pd.DataFrame), f"Expected DataFrame, got {type(data)}"
    assert not data.empty, "Data should not be empty"
    save_test_data('certificates.json', data.to_dict())

@pytest.mark.asyncio
async def test_get_cryptocurrencies():
    data = await get_investpy_data("cryptocurrencies")
    assert isinstance(data, pd.DataFrame), f"Expected DataFrame, got {type(data)}"
    assert not data.empty, "Data should not be empty"
    save_test_data('cryptocurrencies.json', data.to_dict())