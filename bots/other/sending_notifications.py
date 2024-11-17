import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
from data.database import get_all_users, get_user_settings, update_specific_user_settings
from other.fetch_endpoints import call_current_data, call_tb_current_data
import logging
from config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def update_alert_info(user_id: int, asset_type: str, ticker: str, alert_info: Dict):
    settings = await get_user_settings(user_id)
    
    settings['notification_price_level'][asset_type][ticker] = alert_info
    
    await update_specific_user_settings(user_id, {'notification_price_level': settings['notification_price_level']})

async def send_notification_price_change(bot):
    while True:
        users = await get_all_users()
        for user in users:
            user_id = user['id']
            settings = await get_user_settings(user_id)
            frequency_str = settings.get('notification_frequency', '10min')
            frequency = FREQUENCY_MAPPING.get(frequency_str, 600)
            last_sent = settings.get('last_price_change_notification', {})
            now = datetime.utcnow()

            if user_id in last_sent:
                last_time = datetime.fromisoformat(last_sent[user_id])
                if (now - last_time).total_seconds() < frequency:
                    continue

            notification_price_change = settings.get('notification_price_change', {})
            if notification_price_change:
                await fetch_and_notify_price_change(bot, user_id, notification_price_change)
                last_sent[user_id] = now.isoformat()
                await update_specific_user_settings(user_id, {'last_price_change_notification': last_sent})

        await asyncio.sleep(60)

async def fetch_and_notify_price_change(bot, user_id: int, notification_price_change: Dict):
    for asset_type, tickers in notification_price_change.items():
        for ticker in tickers:
            if asset_type == 'stock':
                data = await call_tb_current_data(ticker, interval='5m')
            else:
                data = await call_current_data(asset_type, ticker, interval='5m')
            if data and "error" not in data:
                message_text = f"📈 Обновление цены для {ticker}:\n\nТекущая цена: {data.get('close') or data.get('Close')}"
                await bot.send_message(chat_id=user_id, text=message_text, parse_mode='HTML')
                await asyncio.sleep(1)
            else:
                logger.error(f"Failed to fetch data for {ticker}")

async def send_notification_price_level(bot):
    while True:
        users = await get_all_users()
        for user in users:
            user_id = user['id']
            settings = await get_user_settings(user_id)
            notification_price_level = settings.get('notification_price_level', {})
            if notification_price_level:
                await check_and_notify_price_levels(bot, user_id, notification_price_level)
        await asyncio.sleep(60)

async def check_and_notify_price_levels(bot, user_id: int, notification_price_level: Dict):
    for asset_type, tickers_info in notification_price_level.items():
        for ticker, alert_info in tickers_info.items():
            if asset_type == 'stock':
                data = await call_tb_current_data(ticker, interval='5m')
            else:
                data = await call_current_data(asset_type, ticker, interval='5m')
            if data and "error" not in data:
                current_price = data.get('close') or data.get('Close')
                previous_price = alert_info.get('current_price')
                alert_type = alert_info.get('type')
                alert_value = alert_info.get('value')

                if alert_type == 'value' and (
                    (previous_price < alert_value <= current_price) or 
                    (previous_price > alert_value >= current_price)
                ):
                    message_text = (f"⚠ {ticker} достиг ценового уровня: {alert_value}\n"
                                    f"Текущая цена: {current_price}")
                    await bot.send_message(chat_id=user_id, text=message_text, parse_mode='HTML')
                    alert_info['current_price'] = current_price
                    await update_alert_info(user_id, asset_type, ticker, alert_info)

                elif alert_type == 'percent':
                    percent_change = ((current_price - previous_price) / previous_price) * 100
                    if abs(percent_change) >= alert_value:
                        message_text = (f"⚠ {ticker} изменился на {percent_change:.2f}%\n"
                                        f"Текущая цена: {current_price}")
                        await bot.send_message(chat_id=user_id, text=message_text, parse_mode='HTML')
                        alert_info['current_price'] = current_price
                        await update_alert_info(user_id, asset_type, ticker, alert_info)
            else:
                logger.error(f"Failed to fetch data for {ticker}")

async def start(bot):
    await asyncio.gather(
        send_notification_price_change(bot),
        send_notification_price_level(bot)
    )
