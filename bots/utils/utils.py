from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from decimal import *
import os
import time
import asyncio
from aiogram.types import Message, FSInputFile
import base64
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram import types
from aiogram.fsm.context import FSMContext
from typing import Optional
from functools import wraps
from typing import Optional, List, Dict

async def safe_edit_message(message: types.Message, text: str, reply_markup: InlineKeyboardMarkup):
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            print("Attempted to edit message without changes.")
        else:
            print(f"Failed to edit message: {e}")

async def delete_message(message, state):
    await message.delete()
    state_data = await state.get_data()
    chat_id = state_data.get('chat_id')
    message_id = state_data.get('message_id')
    await message.bot.delete_message(chat_id, message_id)

def handle_telegram_exception(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if isinstance(args[0], CallbackQuery):
                await args[0].message.answer("Произошла ошибка при обработке вашего запроса.")
            elif isinstance(args[0], Message):
                await args[0].answer("Произошла ошибка при обработке вашего сообщения.")
    return wrapper

def format_asset_summary(info: Dict) -> str:
    name = info.get('info', {}).get('name', 'Нет данных')
    ticker = info.get('info', {}).get('ticker', 'Нет тикера')
    current_price = info.get('current_price', 'Нет данных')
    high = info.get('high', 'Нет данных')
    low = info.get('low', 'Нет данных')
    currency = info.get('info', {}).get('currency', 'Нет данных')
    volume = info.get('volume', 0)

    turnover_ratio = 10
    try:
        calculated_market_cap = float(volume) * turnover_ratio
    except (ValueError, TypeError):
        calculated_market_cap = "Не удалось рассчитать"

    if high and low:
        try:
            change_percent = (float(high) - float(low)) / float(low) * 100
        except ZeroDivisionError:
            change_percent = "Ошибка деления на ноль"
    else:
        change_percent = "Данные отсутствуют"

    summary = (
        f"📈 {name} ({ticker})\n\n"
        f"🔍 Текущая цена: {current_price} {currency}\n"
        f"📊 Минимум за день: {low} {currency}\n"
        f"📊 Максимум за день: {high} {currency}\n"
        f"📊 Изменение за день: {change_percent}%\n"
        f"🔄 Объем торгов за день: {volume} {currency}\n"
    )
    
    return summary


def format_crypto_summary(info: Dict) -> str:
    name = info.get('info', {}).get('name', 'Нет данных')
    ticker = info.get('info', {}).get('symbol', 'Нет тикера')
    current_price = info.get('current_price', 'Нет данных')
    high = info.get('High', 'Нет данных')
    low = info.get('Low', 'Нет данных')
    currency = info.get('info', {}).get('currency', 'Нет данных')
    volume = info.get('Volume', 'Нет данных')
    circulating_supply = info.get('info', {}).get('circulatingSupply', 'Нет данных')
    market_cap = info.get('info', {}).get('marketCap', 'Не указано')

    if high and low:
        try:
            change_percent = (float(high) - float(low)) / float(low) * 100
        except ZeroDivisionError:
            change_percent = "Ошибка деления на ноль"
    else:
        change_percent = "Данные отсутствуют"

    summary = (
        f"📈 {name} ({ticker})\n\n"
        f"🔍 Текущая цена: {current_price} {currency}\n"
        f"📊 Минимум за день: {low} {currency}\n"
        f"📊 Максимум за день: {high} {currency}\n"
        f"📊 Изменение за день: {change_percent}%\n"
        f"💼 Рыночная капитализация: {market_cap} USD\n"
        f"🔄 Объем торгов: {volume} USD\n"
        f"💰 В обращении: {circulating_supply} токенов\n"
    )
    
    return summary


def format_currency_summary(info: Dict) -> str:
    name = info.get('info', {}).get('longName', 'Нет данных')
    ticker = info.get('info', {}).get('symbol', 'Нет тикера')
    current_price = info.get('current_price', 'Нет данных')
    high = info.get('info', {}).get('regularMarketDayHigh', 'Нет данных')
    low = info.get('info', {}).get('regularMarketDayLow', 'Нет данных')
    currency = info.get('info', {}).get('currency', 'Нет данных')
    year_low = info.get('info', {}).get('fiftyTwoWeekLow', 'Нет данных')
    year_high = info.get('info', {}).get('fiftyTwoWeekHigh', 'Нет данных')
    average_50 = info.get('info', {}).get('fiftyDayAverage', 'Нет данных')
    average_200 = info.get('info', {}).get('twoHundredDayAverage', 'Нет данных')

    if high and low:
        try:
            change_percent = (float(high) - float(low)) / float(low) * 100
        except ZeroDivisionError:
            change_percent = "Ошибка деления на ноль"
    else:
        change_percent = "Данные отсутствуют"

    summary = (
        f"📈 {name} ({ticker})\n\n"
        f"🔍 Текущая цена (закрытие): {current_price} {currency}\n"
        f"📊 Минимум за день: {low} {currency}\n"
        f"📊 Максимум за день: {high} {currency}\n"
        f"📊 Изменение за день: {change_percent}%\n"
        f"📆 Годовой диапазон: {year_low} - {year_high} {currency}\n"
        f"📈 Средняя цена (50 дней): {average_50} {currency}\n"
        f"📈 Средняя цена (200 дней): {average_200} {currency}\n"
    )
    
    return summary