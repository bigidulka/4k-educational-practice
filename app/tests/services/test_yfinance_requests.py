# File path: tests/services/test_yfinance_requests.py

import pytest
import json
from src.services.yfinance_requests import get_current_data, get_historical_data
import pandas as pd

# Путь для сохранения тестовых данных
TEST_OUTPUTS_PATH = 'tests/test_outputs/'

def save_test_data(filename, data):
    """Сохраняет данные в формате JSON."""
    with open(f'{TEST_OUTPUTS_PATH}{filename}', 'w', encoding='utf-8') as f:
        json.dump(data, f, default=str, ensure_ascii=False, indent=4)

@pytest.mark.asyncio
async def test_get_current_data_stock():
    data = await get_current_data('stock', 'AAPL')
    assert isinstance(data, dict), f"Expected dict, got {type(data)}"
    assert len(data) > 0, "Data should not be empty"
    save_test_data('current_data_stock.json', data)

@pytest.mark.asyncio
async def test_get_current_data_crypto():
    data = await get_current_data('crypto', 'BTC')
    assert isinstance(data, dict), f"Expected dict, got {type(data)}"
    assert len(data) > 0, "Data should not be empty"
    save_test_data('current_data_crypto.json', data)

@pytest.mark.asyncio
async def test_get_current_data_currency():
    data = await get_current_data('currency', 'EURUSD')
    assert isinstance(data, dict), f"Expected dict, got {type(data)}"
    assert len(data) > 0, "Data should not be empty"
    save_test_data('current_data_currency.json', data)

# @pytest.mark.asyncio
# async def test_get_current_data_index():
#     data = await get_current_data('index', '^GSPC')
#     assert isinstance(data, dict), f"Expected dict, got {type(data)}"
#     assert len(data) > 0, "Data should not be empty"
#     save_test_data('current_data_index.json', data)

@pytest.mark.asyncio
async def test_get_historical_data_stock():
    data = await get_historical_data('stock', 'AAPL', '2010-01-01', '2020-01-01')
    assert isinstance(data, pd.DataFrame), f"Expected DataFrame, got {type(data)}"
    assert not data.empty, "Data should not be empty"
    save_test_data('historical_data_stock.json', data.to_dict(orient='records'))

@pytest.mark.asyncio
async def test_get_historical_data_crypto():
    data = await get_historical_data('crypto', 'BTC', '2014-01-01', '2019-01-01')
    assert isinstance(data, pd.DataFrame), f"Expected DataFrame, got {type(data)}"
    assert not data.empty, "Data should not be empty"
    save_test_data('historical_data_crypto.json', data.to_dict(orient='records'))

@pytest.mark.asyncio
async def test_get_historical_data_currency():
    data = await get_historical_data('currency', 'EURUSD', '2010-01-01', '2020-01-01')
    assert isinstance(data, pd.DataFrame), f"Expected DataFrame, got {type(data)}"
    assert not data.empty, "Data should not be empty"
    save_test_data('historical_data_currency.json', data.to_dict(orient='records'))

# @pytest.mark.asyncio
# async def test_get_historical_data_index():
#     data = await get_historical_data('index', '^GSPC', '2010-01-01', '2020-01-01')
#     assert isinstance(data, pd.DataFrame), f"Expected DataFrame, got {type(data)}"
#     assert not data.empty, "Data should not be empty"
#     save_test_data('historical_data_index.json', data.to_dict(orient='records'))
