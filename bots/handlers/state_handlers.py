from aiogram import Router, types, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
from aiogram import Bot
import os
from config import TIMEFRAME_SETTINGS
from other.fetch_endpoints import *
from utils.middlewares import UserTrackingMiddleware 
from keyboards.inline import *
from utils.utils import *
from utils.states import *
from other.graph_image import *
from data.database import *


router = Router()
router.callback_query.outer_middleware(UserTrackingMiddleware())

@router.message(SearchStocks.waiting_for_search_query, F.text)
async def process_search_query(message: Message, state: FSMContext):
    query = message.text.strip()
    if not query:
        await message.reply("Пожалуйста, введите корректный запрос для поиска.")
        return
    
    stocks = await call_tb_tickers()
    if not stocks or "error" in stocks:
        await message.reply("Не удалось получить список акций.")
        await state.clear()
        return
    
    filtered_stocks = [
        stock for stock in stocks
        if query.lower() in stock.get('name', '').lower() or query.upper() == stock.get('ticker', '').upper()
    ]
    
    if not filtered_stocks:
        await message.reply("Акции не найдены по вашему запросу.")
        await state.clear()
        return
    
    builder = InlineKeyboardBuilder()
    for stock in filtered_stocks:
        builder.add(
            InlineKeyboardButton(
                text=stock.get('name', 'Без названия'),
                callback_data=BaseCallbackData(data=f"stock_{stock.get('ticker')}").pack()
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text='↩ Назад',
            callback_data=BaseCallbackData(data='info_stocks').pack()
        )
    )
    
    keyboard = builder.as_markup()
    await message.reply("Результаты поиска:", reply_markup=keyboard)
    await state.clear()
    
@router.callback_query(TimeframeCallbackData.filter())
async def handle_timeframe_selection(call: CallbackQuery, callback_data: TimeframeCallbackData, state: FSMContext):
    timeframe = callback_data.timeframe
    user_data = await state.get_data()
    ticker = user_data.get('chart_ticker')

    if not ticker:
        await call.message.answer("Произошла ошибка: тикер не найден.")
        await call.answer()
        await state.clear()
        return

    settings = TIMEFRAME_SETTINGS.get(timeframe)
    if not settings:
        await call.message.answer("Неверный таймфрейм.")
        await call.answer()
        return

    interval = settings['interval']
    period_days = settings['period_days']
    user_id = call.from_user.id
    user_settings = await get_user_settings(user_id)
    timezone_str = user_settings.get('timezone', '0')
    try:
        utc_offset = int(timezone_str)
    except ValueError:
        utc_offset = 0

    today_utc = datetime.utcnow()
    today_user = today_utc + timedelta(hours=utc_offset)
    today_user_date = today_user.date()
    from_date = today_user_date - timedelta(days=period_days)
    to_date = today_user_date.strftime('%Y-%m-%d')
    from_date_str = from_date.strftime('%Y-%m-%d')

    if ticker.startswith("stock_"):
        symbol = ticker.replace("stock_", "")
        historical_data = await call_tb_historical_data(
            symbol=symbol,
            from_date=from_date_str,
            to_date=to_date,
            utc_offset=utc_offset,
            interval=interval
        )
    elif ticker.startswith("crypto_"):
        symbol = ticker.replace("crypto_", "")
        historical_data = await call_historical_data(
            market="crypto",
            symbol=symbol,
            from_date=from_date_str,
            to_date=to_date,
            utc_offset=utc_offset,
            interval=interval
        )
    elif ticker.startswith("currency_"):
        symbol = ticker.replace("currency_", "")
        historical_data = await call_historical_data(
            market="currency",
            symbol=symbol,
            from_date=from_date_str,
            to_date=to_date,
            utc_offset=utc_offset,
            interval=interval
        )
    else:
        await call.message.answer("Неверный формат тикера.")
        await call.answer()
        return

    if not historical_data or "error" in historical_data:
        await call.message.answer("Не удалось получить исторические данные.")
        await call.answer()
        return

    try:
        create_candlestick_chart_from_data(
            historical_data=historical_data,
            symbol=ticker,
            output_dir="bots/charts",
            title=f"{ticker} Candlestick Chart ({timeframe})"
        )
        file_path = f"bots/charts/{ticker}_candlestick.png"

        if os.path.exists(file_path):
            await call.message.answer_photo(photo=FSInputFile(file_path), caption=f"График для {ticker} ({timeframe}).")
        else:
            await call.message.answer("Не удалось создать график.")
    except Exception as e:
        logger.error(f"Ошибка при создании графика: {e}")
        await call.message.answer(f"Ошибка при создании графика: {e}")
    finally:
        await call.answer()
        await state.clear()
        
@router.callback_query(F.data.startswith('alert_type_'), SetAlert.waiting_for_alert_type)
async def process_alert_type_selection(call: CallbackQuery, state: FSMContext):
    alert_type = call.data.replace('alert_type_', '')
    await state.update_data(alert_type=alert_type)
    await call.message.answer("Введите значение для оповещения:")
    await state.set_state(SetAlert.waiting_for_price_input)
    await call.answer()

@router.message(SetAlert.waiting_for_price_input, F.text)
async def process_price_input(message: Message, state: FSMContext):
    user_data = await state.get_data()
    asset_type = user_data.get('alert_asset_type')
    ticker = user_data.get('alert_ticker')
    alert_type = user_data.get('alert_type')
    current_price = user_data.get('current_price')
    user_id = message.from_user.id

    value_input = message.text.strip().replace(',', '.')
    try:
        value = float(value_input)
    except ValueError:
        await message.reply("Пожалуйста, введите корректное число.")
        return

    settings = await get_user_settings(user_id)
    notification_price_level = settings.get('notification_price_level', {})

    if asset_type not in notification_price_level:
        notification_price_level[asset_type] = {}

    notification_price_level[asset_type][ticker] = {
        'type': alert_type,
        'value': value,
        'current_price': current_price
    }

    await update_specific_user_settings(user_id, {'notification_price_level': notification_price_level})

    await message.reply(f"Уведомление для {ticker} установлено: {('цена' if alert_type == 'value' else 'процент')} {value}.")

    asset_detail_message_id = user_data.get('asset_detail_message_id')
    if not asset_detail_message_id:
        await message.reply("Не удалось обновить детали актива.")
        await state.clear()
        return

    await refresh_asset_detail_message(
        user_id=user_id,
        asset_type=asset_type,
        ticker=ticker,
        asset_detail_message_id=asset_detail_message_id,
        bot=message.bot
    )

    await state.clear()

async def refresh_asset_detail_message(user_id: int, asset_type: str, ticker: str, asset_detail_message_id: int, bot: Bot):
    if asset_type == 'stock':
        daily_data = await call_tb_current_data(ticker, interval='1d')
        if not daily_data or "error" in daily_data:
            await bot.send_message(chat_id=user_id, text="Не удалось загрузить обновленные данные по акции.")
            return
    else:
        daily_data = await call_current_data(asset_type, ticker, interval='1d')
        if not daily_data or "error" in daily_data:
            await bot.send_message(chat_id=user_id, text=f"Не удалось загрузить обновленные данные по {asset_type}.")
            return

    if asset_type == 'stock':
        current_price_data = await call_tb_current_data(ticker, interval='5m')
        if not current_price_data or "error" in current_price_data:
            await bot.send_message(chat_id=user_id, text="Не удалось получить текущую цену по акции.")
            return
        current_price = current_price_data.get('close')
    else:
        current_price_data = await call_current_data(asset_type, ticker, interval='5m')
        if not current_price_data or "error" in current_price_data:
            await bot.send_message(chat_id=user_id, text=f"Не удалось получить текущую цену по {asset_type}.")
            return
        current_price = current_price_data.get('Close')

    asset_info = daily_data.copy()
    asset_info['current_price'] = current_price

    # Форматируем сообщение
    if asset_type == 'stock':
        formatted_message = format_asset_summary(asset_info)
    elif asset_type == 'crypto':
        formatted_message = format_crypto_summary(asset_info)
    elif asset_type == 'currency':
        formatted_message = format_currency_summary(asset_info)
    else:
        await bot.send_message(chat_id=user_id, text="Неизвестный тип актива.")
        return

    settings = await get_user_settings(user_id)
    favorites_assets = settings.get('favorites_assets', [])
    notification_price_change = settings.get('notification_price_change', {})
    notification_price_level = settings.get('notification_price_level', {})

    is_favorite = any(
        asset for asset in favorites_assets 
        if asset.get('asset_type') == asset_type and asset.get('ticker') == ticker
    )
    is_subscribed = ticker in notification_price_change.get(asset_type, [])
    alert_info = notification_price_level.get(asset_type, {}).get(ticker)
    has_alert = bool(alert_info)

    status_lines = [
        "⭐ Этот актив в вашем избранном." if is_favorite else "Этот актив не в вашем избранном.",
        "🔔 Вы подписаны на изменения цены этого актива." if is_subscribed else "Вы не подписаны на изменения цены этого актива.",
        f"⚠ У вас установлен ценовой уровень: {'цена' if alert_info.get('type') == 'value' else 'процент'} {alert_info.get('value')}." if alert_info else "У вас не установлен ценовой уровень для этого актива."
    ]

    full_message = f"{formatted_message}\n\n" + "\n".join(status_lines)

    keyboard = asset_detail_keyboard(f"{asset_type}_{ticker}", is_favorite, is_subscribed, has_alert)

    try:
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=asset_detail_message_id,
            text=full_message,
            reply_markup=keyboard
        )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logging.info("Attempted to edit message without changes.")
        else:
            logging.error(f"Failed to edit message: {e}")