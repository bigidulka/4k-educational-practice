# File path: src/endpoints/routes.py
from fastapi import APIRouter, HTTPException, Query
from src.services import investpy_requests as investpy_services
from src.services import yfinance_requests as yfinance_services
from src.services import tinkoff_requests as tinkoff_requests 
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from enum import Enum

router = APIRouter()


@router.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """
    Корневой эндпоинт, возвращающий приветственное сообщение.

    Returns:
        dict: Словарь с приветственным сообщением.
    """
    return {"message": "Добро пожаловать в Финансовое API"}


@router.get("/stocks", response_model=List[Dict])
async def get_stocks(
    country: Optional[str] = None
) -> List[Dict]:
    """
    Получает список акций, с возможной фильтрацией по стране.

    Параметры:
        country (Optional[str]): Страна для фильтрации акций.

    Returns:
        List[dict]: Список словарей с информацией об акциях.

    Raises:
        HTTPException: Если не удалось получить данные об акциях.
    """
    try:
        stocks = await investpy_services.get_stocks()
        if stocks is None:
            raise HTTPException(status_code=500, detail="Не удалось получить данные об акциях")
        if country:
            stocks = stocks[stocks['country'].str.lower() == country.lower()]
        return stocks.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cryptocurrencies", response_model=List[Dict])
async def get_cryptocurrencies() -> List[Dict]:
    """
    Получает список криптовалют.

    Returns:
        List[dict]: Список словарей с информацией о криптовалютах.

    Raises:
        HTTPException: Если не удалось получить данные о криптовалютах.
    """
    try:
        cryptocurrencies = await investpy_services.get_cryptocurrencies()
        if cryptocurrencies is None:
            raise HTTPException(status_code=500, detail="Не удалось получить данные о криптовалютах")
        return cryptocurrencies.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/currency_crosses", response_model=List[Dict[str, str]])
async def get_currency_crosses() -> List[Dict[str, str]]:
    """
    Получает список валютных пар.

    Returns:
        List[Dict[str, str]]: Список словарей с информацией о валютных парах.

    Raises:
        HTTPException: Если не удалось получить данные о валютных парах.
    """
    try:
        currency_crosses = await investpy_services.get_currency_crosses()
        if currency_crosses is None:
            raise HTTPException(status_code=500, detail="Не удалось получить данные о валютных парах")
        
        return currency_crosses.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical/{market}/{symbol}", response_model=List[Dict])
async def get_historical_data(
    market: str,
    symbol: str,
    from_date: str = Query('2020-01-01', regex=r'^\d{4}-\d{2}-\d{2}$', description="Начальная дата в формате YYYY-MM-DD"),
    to_date: str = Query('2023-01-01', regex=r'^\d{4}-\d{2}-\d{2}$', description="Конечная дата в формате YYYY-MM-DD"),
    utc_offset: int = Query(0, ge=-12, le=14, description="Смещение UTC в часах (например, 3 для UTC+3)"),
    interval: str = Query('1d', regex=r'^(1m|5m|15m|30m|60m|90m|1h|1d|5d|1wk|1mo|3mo)$', description="Интервал данных (например, '1d')")
) -> List[Dict]:
    """
    Получает исторические данные для указанного рынка и символа в заданном диапазоне дат и часовом поясе.

    Параметры:
        market (str): Тип рынка (например, "stock", "crypto").
        symbol (str): Тикер символа.
        from_date (str): Начальная дата в формате "YYYY-MM-DD".
        to_date (str): Конечная дата в формате "YYYY-MM-DD".
        utc_offset (int): Смещение UTC в часах (например, 3 для UTC+3, -5 для UTC-5).
        interval (str): Интервал данных (например, "1m", "5m", "1d").

    Returns:
        List[dict]: Список исторических записей данных.

    Raises:
        HTTPException: Если данные не найдены, даты некорректны или произошла другая ошибка.
    """
    try:
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')

        if utc_offset == 0:
            utc_timezone = "UTC"
        elif utc_offset > 0:
            utc_timezone = f"Etc/GMT-{utc_offset}"
        else:
            utc_timezone = f"Etc/GMT+{abs(utc_offset)}"

        historical_data = await yfinance_services.get_historical_data(
            market,
            symbol,
            from_date_obj.strftime('%Y-%m-%d'),
            to_date_obj.strftime('%Y-%m-%d'),
            utc_timezone,
            interval
        )
        if historical_data is None or not historical_data:
            raise HTTPException(
                status_code=404,
                detail=f"{market.capitalize()} '{symbol}' не найден или данные недоступны"
            )
        return historical_data
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current/{market}/{symbol}", response_model=Dict)
async def get_current_data(
    market: str,
    symbol: str,
    interval: str = Query('1d', regex=r'^(1m|5m|15m|30m|60m|90m|1h|1d|5d|1wk|1mo|3mo)$', description="Интервал данных (например, '1d')")
) -> Dict:
    """
    Получает текущие данные для указанного рынка и символа.

    Параметры:
        market (str): Тип рынка (например, "stock", "crypto").
        symbol (str): Тикер символа.
        interval (str): Интервал данных (например, "1m", "5m", "1d").

    Returns:
        dict: Последняя запись данных для указанного тикера.

    Raises:
        HTTPException: Если данные не найдены или произошла другая ошибка.
    """
    try:
        current_data = await yfinance_services.get_current_data(market, symbol, interval)
        if current_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"{market.capitalize()} '{symbol}' не найден"
            )
        return current_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tb_historical/{symbol}", response_model=List[Dict])
async def get_tinkoff_historical_data(
    symbol: str,
    from_date: str = Query('2020-01-01', regex=r'^\d{4}-\d{2}-\d{2}$', description="Начальная дата в формате YYYY-MM-DD"),
    to_date: str = Query('2023-01-01', regex=r'^\d{4}-\d{2}-\d{2}$', description="Конечная дата в формате YYYY-MM-DD"),
    utc_offset: int = Query(0, ge=-12, le=14, description="Смещение UTC в часах (например, 3 для UTC+3)"),
    interval: str = Query('1d', regex=r'^(1m|5m|15m|1h|1d|1w|1M)$', description="Интервал данных (например, '1d')")
) -> List[Dict]:
    """
    Получает исторические данные для указанного символа акции в заданном диапазоне дат и часовом поясе.

    Параметры:
        symbol (str): Тикер символа.
        from_date (str): Начальная дата в формате "YYYY-MM-DD".
        to_date (str): Конечная дата в формате "YYYY-MM-DD".
        utc_offset (int): Смещение UTC в часах.
        interval (str): Интервал данных (например, '1d').

    Returns:
        List[dict]: Список исторических записей данных.
    """
    try:
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
        timezone = f"Etc/GMT-{utc_offset}" if utc_offset > 0 else f"Etc/GMT+{abs(utc_offset)}"

        historical_data = await tinkoff_requests.get_historical_data(
            market="stock",
            symbol=symbol,
            from_date=from_date_obj.strftime('%Y-%m-%d'),
            to_date=to_date_obj.strftime('%Y-%m-%d'),
            client_timezone=timezone,
            interval=interval
        )
        if not historical_data:
            raise HTTPException(
                status_code=404,
                detail=f"Акция '{symbol}' не найдена или данные недоступны"
            )
        return historical_data
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tb_current/{symbol}", response_model=Dict)
async def get_tinkoff_current_data(
    symbol: str,
    interval: str = Query('1d', regex=r'^(1m|5m|15m|1h|1d|1w|1M)$', description="Интервал данных (например, '1d')")
) -> Dict:
    """
    Получает текущие данные для указанного символа акции.

    Параметры:
        symbol (str): Тикер символа.
        interval (str): Интервал данных (например, '1d').

    Returns:
        dict: Последняя запись данных для указанного тикера.
    """
    try:
        current_data = await tinkoff_requests.get_current_data(market="stock", symbol=symbol, interval=interval)
        if current_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Акция '{symbol}' не найдена"
            )
        return current_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/tb_tickers", response_model=List[Dict[str, str]])
async def get_tickers() -> List[Dict[str, str]]:
    """
    Получает список всех доступных тикеров акций на Tinkoff.

    Returns:
        List[Dict[str, str]]: Список словарей с тикерами акций и их FIGI.

    Raises:
        HTTPException: В случае ошибки.
    """
    try:
        tickers = await tinkoff_requests.get_all_tickers()
        if not tickers:
            raise HTTPException(status_code=404, detail="Тикеры акций не найдены")
        return tickers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
class MarketType(str, Enum):
    stock = "stock"
    crypto = "crypto"
    currency_cross = "currency"

@router.get("/recommendations/{market}/{symbol}", response_model=Dict)
async def get_recommendations(
    market: MarketType,
    symbol: str
) -> Dict:
    """
    Возвращает рекомендации по покупке или продаже на основе исторических данных указанного актива.
    
    Параметры:
        market (str): Тип рынка (например, "stock", "crypto", "currency").
        symbol (str): Тикер символа.
    
    Returns:
        dict: Рекомендации по покупке, продаже или удержанию.
    
    Raises:
        HTTPException: Если исторические данные не найдены или произошла ошибка при генерации рекомендаций.
    """
    try:
        # Определение временного диапазона для исторических данных (последний год)
        from_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        to_date = datetime.now().strftime('%Y-%m-%d')
        timezone = "UTC"

        # Получение исторических данных в зависимости от типа рынка
        if market == MarketType.stock:
            historical_data = await tinkoff_requests.get_historical_data(
                market="stock",
                symbol=symbol,
                from_date=from_date,
                to_date=to_date,
                client_timezone=timezone,
                interval="1d"
            )
        elif market == MarketType.crypto:
            historical_data = await yfinance_services.get_historical_data(
                market=market,
                symbol=symbol,
                from_date=from_date,
                to_date=to_date,
                client_timezone=timezone,
                interval="1d"
            )
        elif market == MarketType.currency_cross:
            historical_data = await yfinance_services.get_historical_data(
                market=market,
                symbol=symbol,
                from_date=from_date,
                to_date=to_date,
                client_timezone=timezone,
                interval="1d"
            )
        else:
            raise HTTPException(status_code=400, detail="Неподдерживаемый тип рынка")

        if not historical_data:
            raise HTTPException(
                status_code=404,
                detail=f"Исторические данные для {market.value} '{symbol}' не найдены"
            )
        
        # Генерация рекомендаций на основе исторических данных
        recommendation = await tinkoff_requests.generate_recommendation_based_on_history(symbol, historical_data)

        return recommendation

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))