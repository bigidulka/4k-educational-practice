import requests
import json
from datetime import datetime
import os

def ensure_directory(path: str):
    """Ensure that the directory exists."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

def save_json(data, filename: str):
    """Save data to a JSON file."""
    ensure_directory(filename)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    # Base URL of the FastAPI application
    base_url = 'http://localhost:8000'  # Change this if your API is hosted elsewhere

    # 1. Call the root endpoint
    try:
        response = requests.get(f'{base_url}/')
        response.raise_for_status()
        save_json(response.json(), 'test\\files/root.json')
        print("Saved response from '/' to 'test\\files/root.json'")
    except requests.RequestException as e:
        save_json({'error': str(e)}, 'test\\files/root.json')
        print(f"Error saving root endpoint: {e}")

    # 2. Call the /stocks endpoint without country filter
    try:
        response = requests.get(f'{base_url}/stocks')
        response.raise_for_status()
        save_json(response.json(), 'test\\files/stocks_all.json')
        print("Saved response from '/stocks' to 'test\\files/stocks_all.json'")
    except requests.RequestException as e:
        save_json({'error': str(e)}, 'test\\files/stocks_all.json')
        print(f"Error saving /stocks endpoint (all): {e}")

    # 3. Call the /stocks endpoint with a country filter (e.g., "United States")
    try:
        params = {'country': 'United States'}
        response = requests.get(f'{base_url}/stocks', params=params)
        response.raise_for_status()
        save_json(response.json(), 'test\\files/stocks_filtered_united_states.json')
        print("Saved response from '/stocks' with country filter to 'test\\files/stocks_filtered_united_states.json'")
    except requests.RequestException as e:
        save_json({'error': str(e)}, 'test\\files/stocks_filtered_united_states.json')
        print(f"Error saving /stocks endpoint (filtered): {e}")

    # 4. Call the /cryptocurrencies endpoint
    try:
        response = requests.get(f'{base_url}/cryptocurrencies')
        response.raise_for_status()
        save_json(response.json(), 'test\\files/cryptocurrencies.json')
        print("Saved response from '/cryptocurrencies' to 'test\\files/cryptocurrencies.json'")
    except requests.RequestException as e:
        save_json({'error': str(e)}, 'test\\files/cryptocurrencies.json')
        print(f"Error saving /cryptocurrencies endpoint: {e}")

    # 5. Call the /currency_crosses endpoint
    try:
        response = requests.get(f'{base_url}/currency_crosses')
        response.raise_for_status()
        save_json(response.json(), 'test\\files/currency_crosses.json')
        print("Saved response from '/currency_crosses' to 'test\\files/currency_crosses.json'")
    except requests.RequestException as e:
        save_json({'error': str(e)}, 'test\\files/currency_crosses.json')
        print(f"Error saving /currency_crosses endpoint: {e}")

    # 6. Call the /historical/{market}/{symbol} endpoint
    try:
        market = 'stock'      # Example market
        symbol = 'AAPL'       # Example symbol
        params = {
            'from_date': '2023-01-01',
            'to_date': '2023-12-31',
            'utc_offset': 0,
            'interval': '1d'
        }
        response = requests.get(f'{base_url}/historical/{market}/{symbol}', params=params)
        response.raise_for_status()
        save_json(response.json(), f'test\\files/historical_{market}_{symbol}.json')
        print(f"Saved response from '/historical/{market}/{symbol}' to 'test\\files/historical_{market}_{symbol}.json'")
    except requests.RequestException as e:
        save_json({'error': str(e)}, f'test\\files/historical_{market}_{symbol}.json')
        print(f"Error saving /historical/{market}/{symbol} endpoint: {e}")

    # 7. Call the /current/{market}/{symbol} endpoint
    try:
        market = 'stock'      # Example market
        symbol = 'AAPL'       # Example symbol
        params = {'interval': '1d'}
        response = requests.get(f'{base_url}/current/{market}/{symbol}', params=params)
        response.raise_for_status()
        save_json(response.json(), f'test\\files/current_{market}_{symbol}.json')
        print(f"Saved response from '/current/{market}/{symbol}' to 'test\\files/current_{market}_{symbol}.json'")
    except requests.RequestException as e:
        save_json({'error': str(e)}, f'test\\files/current_{market}_{symbol}.json')
        print(f"Error saving /current/{market}/{symbol} endpoint: {e}")

    # 8. Call the /tb_historical/{symbol} endpoint
    try:
        symbol = 'AAPL'       # Example symbol
        params = {
            'from_date': '2023-01-01',
            'to_date': '2023-12-31',
            'utc_offset': 0,
            'interval': '1d'
        }
        response = requests.get(f'{base_url}/tb_historical/{symbol}', params=params)
        response.raise_for_status()
        save_json(response.json(), f'test\\files/tb_historical_{symbol}.json')
        print(f"Saved response from '/tb_historical/{symbol}' to 'test\\files/tb_historical_{symbol}.json'")
    except requests.RequestException as e:
        save_json({'error': str(e)}, f'test\\files/tb_historical_{symbol}.json')
        print(f"Error saving /tb_historical/{symbol} endpoint: {e}")

    # 9. Call the /tb_current/{symbol} endpoint
    try:
        symbol = 'AAPL'       # Example symbol
        params = {'interval': '1d'}
        response = requests.get(f'{base_url}/tb_current/{symbol}', params=params)
        response.raise_for_status()
        save_json(response.json(), f'test\\files/tb_current_{symbol}.json')
        print(f"Saved response from '/tb_current/{symbol}' to 'test\\files/tb_current_{symbol}.json'")
    except requests.RequestException as e:
        save_json({'error': str(e)}, f'test\\files/tb_current_{symbol}.json')
        print(f"Error saving /tb_current/{symbol} endpoint: {e}")

    # 10. Call the /tb_tickers endpoint
    try:
        response = requests.get(f'{base_url}/tb_tickers')
        response.raise_for_status()
        save_json(response.json(), 'test\\files/tb_tickers.json')
        print("Saved response from '/tb_tickers' to 'test\\files/tb_tickers.json'")
    except requests.RequestException as e:
        save_json({'error': str(e)}, 'test\\files/tb_tickers.json')
        print(f"Error saving /tb_tickers endpoint: {e}")

    # 11. Call the /recommendations/{symbol} endpoint
    try:
        symbol = 'AAPL'       # Example symbol
        params = {
            'support_level': 150.0,    # Example support level
            'resistance_level': 200.0  # Example resistance level
        }
        response = requests.get(f'{base_url}/recommendations/{symbol}', params=params)
        response.raise_for_status()
        save_json(response.json(), f'test\\files/recommendations_{symbol}.json')
        print(f"Saved response from '/recommendations/{symbol}' to 'test\\files/recommendations_{symbol}.json'")
    except requests.RequestException as e:
        save_json({'error': str(e)}, f'test\\files/recommendations_{symbol}.json')
        print(f"Error saving /recommendations/{symbol} endpoint: {e}")

if __name__ == '__main__':
    main()
