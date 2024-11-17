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
    current_price = f"{info.get('current_price', 'Нет данных'):.2f}" if isinstance(info.get('current_price'), (int, float)) else info.get('current_price')
    high = f"{info.get('high', 'Нет данных'):.2f}" if isinstance(info.get('high'), (int, float)) else info.get('high')
    low = f"{info.get('low', 'Нет данных'):.2f}" if isinstance(info.get('low'), (int, float)) else info.get('low')
    currency = info.get('info', {}).get('currency', 'Нет данных')
    market_cap = f"{info.get('info', {}).get('marketCap', 'Не указано'):.2f}" if isinstance(info.get('info', {}).get('marketCap'), (int, float)) else info.get('info', {}).get('marketCap')

    if high and low:
        try:
            change_percent = f"{(float(high) - float(low)) / float(low) * 100:.2f}"
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
        f"💼 Рыночная капитализация: {market_cap} млрд\n"
    )
    
    return summary


def format_crypto_summary(info: Dict) -> str:
    name = info.get('info', {}).get('name', 'Нет данных')
    ticker = info.get('info', {}).get('symbol', 'Нет тикера')
    current_price = f"{info.get('current_price', 'Нет данных'):.2f}" if isinstance(info.get('current_price'), (int, float)) else info.get('current_price')
    high = f"{info.get('High', 'Нет данных'):.2f}" if isinstance(info.get('High'), (int, float)) else info.get('High')
    low = f"{info.get('Low', 'Нет данных'):.2f}" if isinstance(info.get('Low'), (int, float)) else info.get('Low')
    currency = info.get('info', {}).get('currency', 'Нет данных')
    volume = f"{info.get('Volume', 'Нет данных'):.2f}" if isinstance(info.get('Volume'), (int, float)) else info.get('Volume')
    circulating_supply = f"{info.get('info', {}).get('circulatingSupply', 'Нет данных'):.2f}" if isinstance(info.get('info', {}).get('circulatingSupply'), (int, float)) else info.get('info', {}).get('circulatingSupply')
    market_cap = f"{info.get('info', {}).get('marketCap', 'Не указано'):.2f}" if isinstance(info.get('info', {}).get('marketCap'), (int, float)) else info.get('info', {}).get('marketCap')

    if high and low:
        try:
            change_percent = f"{(float(high) - float(low)) / float(low) * 100:.2f}"
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
    current_price = f"{info.get('current_price', 'Нет данных'):.2f}" if isinstance(info.get('current_price'), (int, float)) else info.get('current_price')
    high = f"{info.get('info', {}).get('regularMarketDayHigh', 'Нет данных'):.2f}" if isinstance(info.get('info', {}).get('regularMarketDayHigh'), (int, float)) else info.get('info', {}).get('regularMarketDayHigh')
    low = f"{info.get('info', {}).get('regularMarketDayLow', 'Нет данных'):.2f}" if isinstance(info.get('info', {}).get('regularMarketDayLow'), (int, float)) else info.get('info', {}).get('regularMarketDayLow')
    currency = info.get('info', {}).get('currency', 'Нет данных')
    year_low = f"{info.get('info', {}).get('fiftyTwoWeekLow', 'Нет данных'):.2f}" if isinstance(info.get('info', {}).get('fiftyTwoWeekLow'), (int, float)) else info.get('info', {}).get('fiftyTwoWeekLow')
    year_high = f"{info.get('info', {}).get('fiftyTwoWeekHigh', 'Нет данных'):.2f}" if isinstance(info.get('info', {}).get('fiftyTwoWeekHigh'), (int, float)) else info.get('info', {}).get('fiftyTwoWeekHigh')
    average_50 = f"{info.get('info', {}).get('fiftyDayAverage', 'Нет данных'):.2f}" if isinstance(info.get('info', {}).get('fiftyDayAverage'), (int, float)) else info.get('info', {}).get('fiftyDayAverage')
    average_200 = f"{info.get('info', {}).get('twoHundredDayAverage', 'Нет данных'):.2f}" if isinstance(info.get('info', {}).get('twoHundredDayAverage'), (int, float)) else info.get('info', {}).get('twoHundredDayAverage')

    if high and low:
        try:
            change_percent = f"{(float(high) - float(low)) / float(low) * 100:.2f}"
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