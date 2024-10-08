# File path: app/endpoints/routes.py

from fastapi import APIRouter, HTTPException, Query
from services import investpy_requests as investpy_services
from services import yfinance_requests as yfinance_services

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Добро пожаловать в финансовый API"}


# Эндпоинты для получения списков котировок с помощью investpy
@router.get("/stocks")
async def get_stocks(country: str = None, limit: int = Query(None, ge=1)):
    try:
        stocks = await investpy_services.get_stocks()
        if country:
            stocks = stocks[stocks['country'].str.lower() == country.lower()]
        data = stocks.to_dict(orient="records")
        if limit:
            data = data[:limit]
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/funds")
async def get_funds(limit: int = Query(None, ge=1)):
    try:
        funds = await investpy_services.get_funds()
        data = funds.to_dict(orient="records")
        if limit:
            data = data[:limit]
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/etfs")
async def get_etfs(limit: int = Query(None, ge=1)):
    try:
        etfs = await investpy_services.get_etfs()
        data = etfs.to_dict(orient="records")
        if limit:
            data = data[:limit]
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/currencies")
async def get_currency_crosses(limit: int = Query(None, ge=1)):
    try:
        currencies = await investpy_services.get_currency_crosses()
        data = currencies.to_dict(orient="records")
        if limit:
            data = data[:limit]
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indices")
async def get_indices(limit: int = Query(None, ge=1)):
    try:
        indices = await investpy_services.get_indices()
        data = indices.to_dict(orient="records")
        if limit:
            data = data[:limit]
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bonds")
async def get_bonds(limit: int = Query(None, ge=1)):
    try:
        bonds = await investpy_services.get_bonds()
        data = bonds.to_dict(orient="records")
        if limit:
            data = data[:limit]
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/commodities")
async def get_commodities(limit: int = Query(None, ge=1)):
    try:
        commodities = await investpy_services.get_commodities()
        data = commodities.to_dict(orient="records")
        if limit:
            data = data[:limit]
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/certificates")
async def get_certificates(limit: int = Query(None, ge=1)):
    try:
        certificates = await investpy_services.get_certificates()
        data = certificates.to_dict(orient="records")
        if limit:
            data = data[:limit]
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cryptocurrencies")
async def get_cryptocurrencies(limit: int = Query(None, ge=1)):
    try:
        cryptocurrencies = await investpy_services.get_cryptocurrencies()
        data = cryptocurrencies.to_dict(orient="records")
        if limit:
            data = data[:limit]
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Эндпоинты для получения исторических данных с помощью investpy
@router.get("/historical/{market}/{symbol}")
async def get_historical_data(
    market: str,
    symbol: str,
    from_date: str = '01/01/2020',
    to_date: str = '01/01/2023',
    country: str = None
):
    try:
        historical_data = await investpy_services.get_historical_data(market, symbol, from_date, to_date, country)
        if historical_data is None or historical_data.empty:
            raise HTTPException(status_code=404, detail=f"{market.capitalize()} '{symbol}' не найден или данные недоступны")
        return historical_data.reset_index().to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Эндпоинты для получения текущих данных с помощью yfinance
@router.get("/current/{market}/{symbol}")
async def get_current_data(market: str, symbol: str):
    try:
        current_data = await yfinance_services.get_current_data(market, symbol)
        if current_data is None:
            raise HTTPException(status_code=404, detail=f"{market.capitalize()} '{symbol}' не найден")
        return current_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
