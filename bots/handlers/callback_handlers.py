import sys
from aiogram import Router, types, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from other.fetch_endpoints import *
from utils.middlewares import UserTrackingMiddleware 
from keyboards.inline import *
from utils.utils import *
from utils.states import *
from data.database import *
from aiogram import Bot


router = Router()
router.callback_query.outer_middleware(UserTrackingMiddleware())

@router.callback_query(BaseCallbackData.filter(F.data == 'info_assets'))
async def handle_info_assets_menu(call: CallbackQuery, callback_data: BaseCallbackData):
    text, keyboard = info_assets_keyboard()
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data == 'favorite_assets'))
async def handle_favorite_assets_menu(call: CallbackQuery, callback_data: BaseCallbackData):
    text, keyboard = favorite_assets_keyboard()
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data == 'bot_settings'))
async def handle_bot_settings(call: CallbackQuery, callback_data: BaseCallbackData):
    text, keyboard = bot_settings_keyboard()
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data == 'help_commands'))
async def handle_help_commands(call: CallbackQuery, callback_data: BaseCallbackData):
    text, keyboard = help_commands_keyboard()
    await call.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data == 'select_timezone'))
async def handle_select_timezone(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext):
    user_id = call.from_user.id
    settings = await get_user_settings(user_id)
    current_timezone = settings.get('timezone', 'UTC')
    text, keyboard = timezone_selection_keyboard(current_timezone)
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data.startswith('set_timezone_')))
async def handle_set_timezone(call: CallbackQuery, callback_data: BaseCallbackData):
    tz = callback_data.data.replace('set_timezone_', '')
    user_id = call.from_user.id
    await update_specific_user_settings(user_id, {'timezone': tz})
    settings = await get_user_settings(user_id)
    current_timezone = settings.get('timezone', 'UTC')
    text, keyboard = timezone_selection_keyboard(current_timezone)
    await call.message.edit_text("Ваш часовой пояс установлен на {}.".format(tz), reply_markup=keyboard)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data == 'select_base_currency'))
async def handle_select_base_currency(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext):
    user_id = call.from_user.id
    settings = await get_user_settings(user_id)
    current_currency = settings.get('base_currency', 'USD')
    text, keyboard = base_currency_selection_keyboard(current_currency)
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data.startswith('set_base_currency_')))
async def handle_set_base_currency(call: CallbackQuery, callback_data: BaseCallbackData):
    currency = callback_data.data.replace('set_base_currency_', '')
    user_id = call.from_user.id
    await update_specific_user_settings(user_id, {'base_currency': currency})
    settings = await get_user_settings(user_id)
    current_currency = settings.get('base_currency', 'USD')
    text, keyboard = base_currency_selection_keyboard(current_currency)
    await call.message.edit_text(f"Ваша базовая валюта установлена на {currency}.", reply_markup=keyboard)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data == 'select_notification_frequency'))
async def handle_select_notification_frequency(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext):
    user_id = call.from_user.id
    settings = await get_user_settings(user_id)
    current_frequency = settings.get('notification_frequency', '10min')
    text, keyboard = notification_frequency_selection_keyboard(current_frequency)
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data.startswith('set_notification_frequency_')))
async def handle_set_notification_frequency(call: CallbackQuery, callback_data: BaseCallbackData):
    frequency = callback_data.data.replace('set_notification_frequency_', '')
    user_id = call.from_user.id
    await update_specific_user_settings(user_id, {'notification_frequency': frequency})
    settings = await get_user_settings(user_id)
    current_frequency = settings.get('notification_frequency', '10min')
    text, keyboard = notification_frequency_selection_keyboard(current_frequency)
    frequency_labels = {
        '1min': 'Каждую 1 минут',
        '5min': 'Каждую 5 минут',
        '10min': 'Каждые 10 минут',
        '30min': 'Каждые 30 минут',
        '1h': 'Каждый 1 час',
        '6h': 'Каждые 6 часов',
        '12h': 'Каждые 12 часов',
        '24h': 'Каждый 1 день',
    }
    label = frequency_labels.get(frequency, frequency)
    await call.message.edit_text("Частота уведомлений установлена на {}.".format(label), reply_markup=keyboard)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data == 'info_stocks'))
async def handle_info_stocks(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext):
    stocks = await call_tb_tickers()
    if not stocks or "error" in stocks:
        await call.message.answer("Не удалось получить список акций.")
        await call.answer()
        return
    page = 1
    per_page = 5
    text, keyboard = stocks_list_keyboard(stocks, page, per_page)
    await state.update_data(stocks=stocks, current_page=page, per_page=per_page)
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data == 'favorite_stocks'))
async def handle_favorite_stocks(call: CallbackQuery, callback_data: BaseCallbackData):
    user_id = call.from_user.id
    settings = await get_user_settings(user_id)
    favorite_assets = settings.get('favorites_assets', [])
    favorite_stocks = [asset for asset in favorite_assets if asset.get('asset_type') == 'stock']
    if not favorite_stocks:
        await call.message.answer("У вас нет избранных акций.")
        await call.answer()
        return
    builder = InlineKeyboardBuilder()
    for asset in favorite_stocks:
        ticker = asset.get('ticker')
        builder.row(
            InlineKeyboardButton(
                text=ticker, 
                callback_data=BaseCallbackData(data=f"stock_{ticker}").pack()
            )
        )
    builder.row(
        InlineKeyboardButton(
            text='↩ Назад',
            callback_data=BaseCallbackData(data='favorite_assets').pack()
        )
    )
    keyboard = builder.as_markup()
    await call.message.edit_text("Ваши избранные акции:", reply_markup=keyboard)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data == 'favorite_currencies'))
async def handle_favorite_currencies(call: CallbackQuery, callback_data: BaseCallbackData):
    user_id = call.from_user.id
    settings = await get_user_settings(user_id)
    favorite_assets = settings.get('favorites_assets', [])
    favorite_currencies = [asset for asset in favorite_assets if asset.get('asset_type') == 'currency']
    if not favorite_currencies:
        await call.message.answer("У вас нет избранных валют.")
        await call.answer()
        return
    builder = InlineKeyboardBuilder()
    for asset in favorite_currencies:
        ticker = asset.get('ticker')
        builder.row(
            InlineKeyboardButton(
                text=ticker, 
                callback_data=BaseCallbackData(data=f"currency_{ticker}").pack()
            )
        )
    builder.row(
        InlineKeyboardButton(
            text='↩ Назад',
            callback_data=BaseCallbackData(data='favorite_assets').pack()
        )
    )
    keyboard = builder.as_markup()
    await call.message.edit_text("Ваши избранные валюты:", reply_markup=keyboard)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data == 'favorite_crypto'))
async def handle_favorite_crypto(call: CallbackQuery, callback_data: BaseCallbackData):
    user_id = call.from_user.id
    settings = await get_user_settings(user_id)
    favorite_assets = settings.get('favorites_assets', [])
    favorite_crypto = [asset for asset in favorite_assets if asset.get('asset_type') == 'crypto']
    if not favorite_crypto:
        await call.message.answer("У вас нет избранных криптовалют.")
        await call.answer()
        return
    builder = InlineKeyboardBuilder()
    for asset in favorite_crypto:
        ticker = asset.get('ticker')
        builder.row(
            InlineKeyboardButton(
                text=ticker, 
                callback_data=BaseCallbackData(data=f"crypto_{ticker}").pack()
            )
        )
    builder.row(
        InlineKeyboardButton(
            text='↩ Назад',
            callback_data=BaseCallbackData(data='favorite_assets').pack()
        )
    )
    keyboard = builder.as_markup()
    await call.message.edit_text("Ваши избранные криптовалюты:", reply_markup=keyboard)
    await call.answer()

@router.callback_query(Pagination.filter(F.data == 'stocks'))
async def handle_stocks_pagination(call: CallbackQuery, callback_data: Pagination, state: FSMContext):
    user_data = await state.get_data()
    stocks = user_data.get('stocks')
    per_page = user_data.get('per_page', 5)
    if not stocks:
        stocks = await call_tb_tickers()
        if not stocks or "error" in stocks:
            await call.message.answer("Не удалось получить список акций.")
            await call.answer()
            return
        await state.update_data(stocks=stocks)
    page = callback_data.page
    text, keyboard = stocks_list_keyboard(stocks, page, per_page)
    await state.update_data(current_page=page)
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data == 'search_stocks'))
async def handle_search_stocks(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext):
    text, keyboard = search_prompt_keyboard()
    await call.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(SearchStocks.waiting_for_search_query)
    await call.answer()

@router.callback_query(CurrencySelectionCallbackData.filter(F.step == 'select'))
async def handle_currency_selection(call: CallbackQuery, callback_data: CurrencySelectionCallbackData, state: FSMContext):
    selected_currency = callback_data.currency
    user_data = await state.get_data()
    selected = user_data.get('selected_currencies', [])
    if selected_currency in selected:
        selected.remove(selected_currency)
    elif len(selected) < 2:
        selected.append(selected_currency)
    await state.update_data(selected_currencies=selected)
    user_id = call.from_user.id
    settings = await get_user_settings(user_id)
    base_currency = settings.get('base_currency', 'USD')
    currencies = CURRENCY_TICKERS
    text, keyboard = select_currencies_keyboard(currencies, selected, base_currency)
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data == 'info_currencies'))
async def handle_info_currencies(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext):
    currencies = CURRENCY_TICKERS
    user_id = call.from_user.id
    settings = await get_user_settings(user_id)
    base_currency = settings.get('base_currency', 'USD')
    text, keyboard = select_currencies_keyboard(currencies, selected=[], base_currency=base_currency)
    await call.message.edit_text(text, reply_markup=keyboard)
    await state.update_data(selected_currencies=[])
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data == 'info_crypto'))
async def handle_info_crypto(call: CallbackQuery, callback_data: BaseCallbackData):
    cryptos = await call_cryptocurrencies()
    if not cryptos or "error" in cryptos:
        await call.message.answer("Не удалось получить список криптовалют.")
        await call.answer()
        return
    text, keyboard = crypto_list_keyboard(cryptos)
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data.startswith("stock_")))
async def handle_stock_detail(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext):
    ticker = callback_data.data.split("_", 1)[1]
    await handle_asset_detail(call, 'stock', ticker, state)

@router.callback_query(BaseCallbackData.filter(F.data.startswith("crypto_")))
async def handle_crypto_detail(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext):
    ticker = callback_data.data.split("_", 1)[1]
    await handle_asset_detail(call, 'crypto', ticker, state)

@router.callback_query(BaseCallbackData.filter(F.data.startswith("currency_")))
async def handle_currency_detail(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext):
    ticker = callback_data.data.replace("currency_", "").replace("_", "")
    await handle_asset_detail(call, 'currency', ticker, state)

async def handle_asset_detail(call: CallbackQuery, asset_type: str, ticker: str, state: FSMContext):
    user_id = call.from_user.id

    if asset_type == 'stock':
        daily_data = await call_tb_current_data(ticker, interval='1d')
        if not daily_data or "error" in daily_data:
            await call.message.answer("Не удалось загрузить данные по акции.")
            await call.answer()
            return
    else:
        daily_data = await call_current_data(asset_type, ticker, interval='1d')
        if not daily_data or "error" in daily_data:
            await call.message.answer(f"Не удалось загрузить данные по {asset_type}.")
            await call.answer()
            return

    if asset_type == 'stock':
        current_price_data = await call_tb_current_data(ticker, interval='5m')
        if not current_price_data or "error" in current_price_data:
            await call.message.answer("Не удалось получить текущую цену по акции.")
            await call.answer()
            return
        current_price = current_price_data.get('close')
    else:
        current_price_data = await call_current_data(asset_type, ticker, interval='5m')
        if not current_price_data or "error" in current_price_data:
            await call.message.answer(f"Не удалось получить текущую цену по {asset_type}.")
            await call.answer()
            return
        current_price = current_price_data.get('Close')

    asset_info = daily_data.copy()
    asset_info['current_price'] = current_price

    if asset_type == 'stock':
        formatted_message = format_asset_summary(asset_info)
    elif asset_type == 'crypto':
        formatted_message = format_crypto_summary(asset_info)
    elif asset_type == 'currency':
        formatted_message = format_currency_summary(asset_info)
    else:
        await call.message.answer("Неизвестный тип актива.")
        await call.answer()
        return

    await state.update_data(current_price=current_price)

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
    await safe_edit_message(call.message, full_message, keyboard)
    await state.update_data(asset_detail_message_id=call.message.message_id)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data.startswith("show_chart_")))
async def handle_show_chart(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext):
    ticker = callback_data.data.replace("show_chart_", "")
    await state.update_data(chart_ticker=ticker)
    await state.set_state(ChartTimeframe.waiting_for_timeframe_selection)
    text, keyboard = timeframe_selection_keyboard()
    await call.message.answer(text, reply_markup=keyboard)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data.startswith("subscribe_")))
async def handle_subscribe(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext):
    ticker_full = callback_data.data.replace("subscribe_", "")
    asset_type, ticker = ticker_full.split("_", 1)
    user_id = call.from_user.id
    settings = await get_user_settings(user_id)
    notification_price_change = settings.get('notification_price_change', {})
    if asset_type not in notification_price_change:
        notification_price_change[asset_type] = []
    if ticker not in notification_price_change[asset_type]:
        notification_price_change[asset_type].append(ticker)
        await update_specific_user_settings(user_id, {'notification_price_change': notification_price_change})
        await call.message.answer(f"Вы подписались на изменения цены {ticker}.")
    else:
        await call.message.answer(f"Вы уже подписаны на изменения цены {ticker}.")
    await handle_asset_detail(call, asset_type, ticker, state)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data.startswith("set_alert_")))
async def handle_set_alert(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext):
    ticker_full = callback_data.data.replace("set_alert_", "")
    asset_type, ticker = ticker_full.split("_", 1)
    user_id = call.from_user.id
    await state.update_data(
        alert_asset_type=asset_type,
        alert_ticker=ticker,
        asset_detail_message_id=call.message.message_id
    )
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='По цене', callback_data='alert_type_value'),
        InlineKeyboardButton(text='По проценту', callback_data='alert_type_percent')
    )
    keyboard = builder.as_markup()
    await call.message.answer(f"Выберите тип ценового уровня для {ticker}:", reply_markup=keyboard)
    await state.set_state(SetAlert.waiting_for_alert_type)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data.startswith("add_favorite_")))
async def handle_add_favorite(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext):
    ticker_full = callback_data.data.replace("add_favorite_", "")
    asset_type, ticker = ticker_full.split("_", 1)
    user_id = call.from_user.id
    new_item = {'asset_type': asset_type, 'ticker': ticker}
    list_path = ['favorites_assets']
    success = await add_item_to_user_list_setting(user_id, list_path, new_item)
    if success:
        await call.message.answer(f"{ticker} добавлен в избранное.")
    else:
        await call.message.answer(f"{ticker} уже есть в избранном.")
    await handle_asset_detail(call, asset_type, ticker, state)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data.startswith("remove_favorite_")))
async def handle_remove_favorite(call: CallbackQuery, callback_data: BaseCallbackData):
    ticker_full = callback_data.data.replace("remove_favorite_", "")
    asset_type, ticker = ticker_full.split("_", 1)
    user_id = call.from_user.id
    list_path = ['favorites_assets']
    item_to_remove = {'asset_type': asset_type, 'ticker': ticker}
    success = await remove_item_from_user_list_setting(user_id, list_path, item_to_remove)
    if success:
        await call.message.answer(f"{ticker} удален из избранного.")
    else:
        await call.message.answer(f"{ticker} не был в избранном.")
    await refresh_asset_detail(call, asset_type, ticker)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data.startswith("unsubscribe_")))
async def handle_unsubscribe(call: CallbackQuery, callback_data: BaseCallbackData):
    ticker_full = callback_data.data.replace("unsubscribe_", "")
    asset_type, ticker = ticker_full.split("_", 1)
    user_id = call.from_user.id
    settings = await get_user_settings(user_id)
    notification_price_change = settings.get('notification_price_change', {})
    if ticker in notification_price_change.get(asset_type, []):
        notification_price_change[asset_type].remove(ticker)
        await update_specific_user_settings(user_id, {'notification_price_change': notification_price_change})
        await call.message.answer(f"Вы отписались от изменений цены {ticker}.")
    else:
        await call.message.answer(f"Вы не были подписаны на изменения цены {ticker}.")
    await refresh_asset_detail(call, asset_type, ticker)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data.startswith("remove_alert_")))
async def handle_remove_alert(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext):
    ticker_full = callback_data.data.replace("remove_alert_", "")
    asset_type, ticker = ticker_full.split("_", 1)
    user_id = call.from_user.id
    settings = await get_user_settings(user_id)
    notification_price_level = settings.get('notification_price_level', {})
    if ticker in notification_price_level.get(asset_type, {}):
        del notification_price_level[asset_type][ticker]
        if not notification_price_level[asset_type]:
            del notification_price_level[asset_type]
        if not notification_price_level:
            notification_price_level = {}
        await update_specific_user_settings(user_id, {'notification_price_level': notification_price_level})
        await call.message.answer(f"Ценовой уровень для {ticker} удален.")
    else:
        await call.message.answer(f"У вас не был установлен ценовой уровень для {ticker}.")
    await handle_asset_detail(call, asset_type, ticker, state)
    await call.answer()

async def refresh_asset_detail(call: CallbackQuery, asset_type: str, ticker: str):
    user_id = call.from_user.id
    if asset_type == 'stock':
        asset_info = await call_tb_current_data(ticker)
        if not asset_info or "error" in asset_info:
            await call.message.answer("Не удалось загрузить обновленные данные по акции.")
            return
        message = format_asset_summary(asset_info)
    elif asset_type == 'crypto':
        asset_info = await call_current_data("crypto", ticker)
        if not asset_info or "error" in asset_info:
            await call.message.answer("Не удалось загрузить обновленные данные по криптовалюте.")
            return
        message = format_crypto_summary(asset_info)
    elif asset_type == 'currency':
        asset_info = await call_current_data("currency", ticker)
        if not asset_info or "error" in asset_info:
            await call.message.answer("Не удалось загрузить обновленные данные по валюте.")
            return
        message = format_currency_summary(asset_info)
    else:
        await call.message.answer("Неизвестный тип актива.")
        return

    settings = await get_user_settings(user_id)
    favorites_assets = settings.get('favorites_assets', [])
    notification_price_change = settings.get('notification_price_change', {})
    notification_price_level = settings.get('notification_price_level', {})

    is_favorite = any(asset for asset in favorites_assets if asset.get('asset_type') == asset_type and asset.get('ticker') == ticker)
    is_subscribed = ticker in notification_price_change.get(asset_type, [])
    alert_info = notification_price_level.get(asset_type, {}).get(ticker)
    has_alert = bool(alert_info)

    status_lines = []
    if is_favorite:
        status_lines.append("⭐ Этот актив в вашем избранном.")
    else:
        status_lines.append("Этот актив не в вашем избранном.")
    if is_subscribed:
        status_lines.append("🔔 Вы подписаны на изменения цены этого актива.")
    else:
        status_lines.append("Вы не подписаны на изменения цены этого актива.")
    if alert_info:
        alert_type = 'цена' if alert_info.get('type') == 'value' else 'процент'
        alert_value = alert_info.get('value')
        status_lines.append(f"⚠ У вас установлен ценовой уровень: {alert_type} {alert_value}.")
    else:
        status_lines.append("У вас не установлен ценовой уровень для этого актива.")

    full_message = message + "\n\n" + "\n".join(status_lines)
    keyboard = asset_detail_keyboard(f"{asset_type}_{ticker}", is_favorite, is_subscribed, has_alert)
    await call.message.edit_text(full_message, reply_markup=keyboard)
    
@router.callback_query(BaseCallbackData.filter(F.data.startswith("update_info_")))
async def handle_update_info(call: CallbackQuery, callback_data: BaseCallbackData, state: FSMContext):
    ticker_full = callback_data.data.replace("update_info_", "")
    if "_" in ticker_full:
        asset_type, ticker = ticker_full.split("_", 1)
    else:
        await call.message.answer("Не удалось определить тип актива для обновления.")
        await call.answer()
        return
    await handle_asset_detail(call, asset_type, ticker, state)

@router.callback_query(BaseCallbackData.filter())
@handle_telegram_exception
async def handle_remaining_callbacks(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    logger.debug('Unhandled callback data received.')
    await call.answer()

@router.callback_query(Navigation.filter())
@handle_telegram_exception
async def go_back(call: CallbackQuery, callback_data: Navigation, state: FSMContext, user_settings, **kwargs):
    if callback_data.callback_func != 'None':
        func_to_call = getattr(sys.modules[__name__], callback_data.callback_func, None)
        if callable(func_to_call):
            await func_to_call(call, state, callback_data, user_settings, **kwargs)
        else:
            logger.error(f"Function {callback_data.callback_func} not found.")
    else:
        func_to_call = getattr(sys.modules[__name__], callback_data.previous, None)
        if callable(func_to_call):
            message_text, reply_markup = func_to_call()
            await call.message.edit_text(text=message_text, reply_markup=reply_markup)
            await state.clear()
        else:
            logger.error(f"Function {callback_data.previous} not found.")
    await call.answer()