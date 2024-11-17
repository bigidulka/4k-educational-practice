import pandas as pd
import mplfinance as mpf
import os
import logging
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prepare_dataframe(historical_data: List[Dict[str, any]], symbol: str) -> pd.DataFrame:
    logger.info("Preparing DataFrame from historical data.")
    df = pd.DataFrame(historical_data)
    logger.info(f"Columns in raw data: {df.columns.tolist()}")

    if "Date" in df.columns:
        date_column = "Date"
    elif "time" in df.columns:
        date_column = "time"
    elif "Datetime" in df.columns:
        date_column = "Datetime"
    else:
        logger.error("No recognizable date column found.")
        raise ValueError("No recognizable date column found.")

    suffix = None
    for col in df.columns:
        if col.startswith('Open_'):
            suffix = col[len('Open_'):]
            break

    if suffix:
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing = [f"{col}_{suffix}" for col in required_cols if f"{col}_{suffix}" not in df.columns]
        if missing:
            logger.error(f"Missing required columns with suffix '{suffix}': {missing}")
            raise ValueError(f"Missing required columns with suffix '{suffix}': {missing}")
        column_mapping = {
            date_column: 'Date',
            f'Open_{suffix}': 'Open',
            f'High_{suffix}': 'High',
            f'Low_{suffix}': 'Low',
            f'Close_{suffix}': 'Close',
            f'Volume_{suffix}': 'Volume'
        }
        df.rename(columns=column_mapping, inplace=True)
    else:
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            logger.error(f"Missing required columns: {missing}")
            raise ValueError(f"Missing required columns: {missing}")
        column_mapping = {
            date_column: 'Date',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        }
        df.rename(columns=column_mapping, inplace=True)

    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)

    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Missing required columns after renaming: {missing_columns}")
        raise ValueError(f"Missing required columns after renaming: {missing_columns}")

    logger.info("DataFrame prepared successfully.")
    return df

def generate_candlestick_chart(
    df: pd.DataFrame,
    symbol: str,
    output_dir: str = 'data/results/charts',
    title: Optional[str] = None,
    save_as: Optional[str] = None
):
    logger.info(f"Generating candlestick chart for {symbol}.")

    if not title:
        title = f"{symbol} Candlestick Chart with Volume"

    if not save_as:
        save_as = f"{symbol}_candlestick.png"

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, save_as)

    mc = mpf.make_marketcolors(
        up='g',
        down='r',
        edge='i',
        wick='i',
        volume='in',
    )
    s = mpf.make_mpf_style(marketcolors=mc, gridstyle='-', gridaxis='both')

    try:
        mpf.plot(
            df,
            type='candle',
            style=s,
            title=title,
            volume=True,
            mav=(20, 50),
            savefig=filepath
        )
        logger.info(f"Candlestick chart saved as {filepath}.")
    except Exception as e:
        logger.error(f"Failed to generate candlestick chart: {e}")
        raise e

def create_candlestick_chart_from_data(
    historical_data: List[Dict[str, any]],
    symbol: str,
    output_dir: str = 'charts',
    title: Optional[str] = None
):
    try:
        df = prepare_dataframe(historical_data, symbol)
        generate_candlestick_chart(df, symbol, output_dir, title)
    except Exception as e:
        logger.error(f"Error creating candlestick chart: {e}")