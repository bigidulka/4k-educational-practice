from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from typing import Optional, List, Dict, Tuple
from config import *

class Navigation(CallbackData, prefix='nav'):
    data: str
    previous: str
    callback_func: str = "None"
        
class BaseCallbackData(CallbackData, prefix='base'):
    data: str
        
class Pagination(CallbackData, prefix='page'):
    data: str
    page: int
        
class Sort(CallbackData, prefix='sort'):
    data: str
    type: str
    current_sort_order: str

class FilterCallbackData(CallbackData, prefix='filter'):
    action: str
    additional: Optional[str] = None

class SearchCallbackData(CallbackData, prefix='search'):
    query: str

class CurrencySelectionCallbackData(CallbackData, prefix='currency'):
    step: str
    currency: str

class SearchStateCallbackData(CallbackData, prefix='search_state'):
    action: str
    
class TimeframeCallbackData(CallbackData, prefix='timeframe'):
    timeframe: str

def timeframe_selection_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='За 1 день',
            callback_data=TimeframeCallbackData(timeframe='1d').pack()
        ),
        InlineKeyboardButton(
            text='За 1 неделю',
            callback_data=TimeframeCallbackData(timeframe='1w').pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text='За 1 месяц',
            callback_data=TimeframeCallbackData(timeframe='1mo').pack()
        ),
        InlineKeyboardButton(
            text='За 1 год',
            callback_data=TimeframeCallbackData(timeframe='1y').pack()
        )
    )
    keyboard = builder.as_markup()
    return "Выберите таймфрейм для графика:", keyboard

def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='Информация об активах', 
            callback_data=BaseCallbackData(data='info_assets').pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text='Избранные активы', 
            callback_data=BaseCallbackData(data='favorite_assets').pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text='Настройки бота', 
            callback_data=BaseCallbackData(data='bot_settings').pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text='Справка по командам и помощь', 
            callback_data=BaseCallbackData(data='help_commands').pack()
        )
    )
    keyboard = builder.as_markup()
    return "Главное меню:", keyboard

def info_assets_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='Акции', callback_data=BaseCallbackData(data='info_stocks').pack()),
        InlineKeyboardButton(text='Валюты', callback_data=BaseCallbackData(data='info_currencies').pack()),
        InlineKeyboardButton(text='Криптовалюты', callback_data=BaseCallbackData(data='info_crypto').pack())
    )
    builder.row(
        InlineKeyboardButton(
            text='↩ Назад',
            callback_data=Navigation(data='back', previous='main_menu_keyboard').pack()
        )
    )
    keyboard = builder.as_markup()
    return "Информация об активах:", keyboard

def favorite_assets_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='Акции', callback_data=BaseCallbackData(data='favorite_stocks').pack()),
        InlineKeyboardButton(text='Валюты', callback_data=BaseCallbackData(data='favorite_currencies').pack()),
        InlineKeyboardButton(text='Криптовалюты', callback_data=BaseCallbackData(data='favorite_crypto').pack())
    )
    builder.row(
        InlineKeyboardButton(
            text='↩ Назад',
            callback_data=Navigation(data='back', previous='main_menu_keyboard').pack()
        )
    )
    keyboard = builder.as_markup()
    return "Избранные активы:", keyboard

def bot_settings_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='Выбрать часовой пояс', callback_data=BaseCallbackData(data='select_timezone').pack())
    )
    builder.row(
        InlineKeyboardButton(text='Базовая валюта', callback_data=BaseCallbackData(data='select_base_currency').pack())
    )
    builder.row(
        InlineKeyboardButton(text='Частота уведомлений', callback_data=BaseCallbackData(data='select_notification_frequency').pack())
    )
    builder.row(
        InlineKeyboardButton(
            text='↩ Назад',
            callback_data=Navigation(data='back', previous='main_menu_keyboard').pack()
        )
    )
    keyboard = builder.as_markup()
    return "Настройки бота:", keyboard

def timezone_selection_keyboard(current_timezone: str) -> Tuple[str, InlineKeyboardMarkup]:
    builder = InlineKeyboardBuilder()
    for i in range(0, len(UTC_OFFSETS_EVEN), 2):
        buttons = []
        for j in range(2):
            if i + j < len(UTC_OFFSETS_EVEN):
                tz = UTC_OFFSETS_EVEN[i + j]
                text = f"✅ {tz}" if tz == current_timezone else tz
                callback_data = BaseCallbackData(data=f'set_timezone_{tz}').pack()
                buttons.append(InlineKeyboardButton(text=text, callback_data=callback_data))
        builder.row(*buttons)

    builder.row(
        InlineKeyboardButton(
            text='↩ Назад',
            callback_data=Navigation(data='back', previous='bot_settings_keyboard').pack()
        )
    )

    keyboard = builder.as_markup()
    return "Выберите ваш часовой пояс:", keyboard

def base_currency_selection_keyboard(current_currency: str):
    builder = InlineKeyboardBuilder()
    for currency in CURRENCY_TICKERS:
        text = f"✅ {currency}" if currency == current_currency else currency
        builder.row(
            InlineKeyboardButton(
                text=text,
                callback_data=BaseCallbackData(data=f'set_base_currency_{currency}').pack()
            )
        )

    builder.row(
        InlineKeyboardButton(
            text='↩ Назад',
            callback_data=Navigation(data='back', previous='bot_settings_keyboard').pack()
        )
    )

    keyboard = builder.as_markup()
    return "Выберите вашу базовую валюту:", keyboard

def notification_frequency_selection_keyboard(current_frequency: str):
    frequencies = ['1min', '5min', '10min', '30min', '1h', '6h', '12h', '24h']
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

    builder = InlineKeyboardBuilder()
    for freq in frequencies:
        label = frequency_labels.get(freq, freq)
        text = f"✅ {label}" if freq == current_frequency else label
        builder.row(
            InlineKeyboardButton(
                text=text,
                callback_data=BaseCallbackData(data=f'set_notification_frequency_{freq}').pack()
            )
        )

    builder.row(
        InlineKeyboardButton(
            text='↩ Назад',
            callback_data=Navigation(data='back', previous='bot_settings_keyboard').pack()
        )
    )

    keyboard = builder.as_markup()
    return "Выберите частоту уведомлений:", keyboard


def help_commands_keyboard():
    help_text = (
        "🤖 Этот бот предоставляет следующие возможности:\n"
        "• /start — Инициализация взаимодействия, вывод главного меню.\n"
        "• Просмотр информации об активах: акции, валюты, криптовалюты.\n"
        "• Управление избранными активами.\n"
        "• Настройка часового пояса, базовой валюты и уведомлений.\n"
        "• Оповещения об изменениях цен и установленных уровнях.\n"
        "• Исторические данные и графики для активов.\n"
        "• Быстрый поиск акций, валют и криптовалют.\n"
        "• Пагинация для удобного просмотра длинных списков.\n"
    )
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='↩ Назад',
            callback_data=Navigation(data='back', previous='main_menu_keyboard').pack()
        )
    )
    keyboard = builder.as_markup()
    return help_text, keyboard

def stocks_list_keyboard(stocks: List[Dict], page: int, per_page: int = 5):
    builder = InlineKeyboardBuilder()
    start = (page - 1) * per_page
    end = start + per_page
    current_stocks = stocks[start:end]
    
    for stock in current_stocks:
        ticker = stock.get('ticker')
        name = stock.get('name')
        
        if ticker and name:
            builder.row(
                InlineKeyboardButton(
                    text=name, 
                    callback_data=BaseCallbackData(data=f"stock_{ticker}").pack()
                )
            )
    
    navigation_buttons = []
    total_pages = (len(stocks) + per_page - 1) // per_page
    if page > 1:
        navigation_buttons.append(
            InlineKeyboardButton(
                text='⬅️',
                callback_data=Pagination(data='stocks', page=page-1).pack()
            )
        )
    if page < total_pages:
        navigation_buttons.append(
            InlineKeyboardButton(
                text='➡️',
                callback_data=Pagination(data='stocks', page=page+1).pack()
            )
        )
    
    if navigation_buttons:
        builder.row(*navigation_buttons)
    
    builder.row(
        InlineKeyboardButton(
            text='🔍 Поиск', 
            callback_data=BaseCallbackData(data='search_stocks').pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text='↩ Назад',
            callback_data=Navigation(data='back', previous='info_assets_keyboard').pack()
        )
    )
    
    keyboard = builder.as_markup()
    return f"Акции (страница {page}):", keyboard

def search_prompt_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='↩ Назад',
            callback_data=BaseCallbackData(data='info_stocks').pack()
        )
    )
    keyboard = builder.as_markup()
    return "Введите название или тикер акции в сообщении.", keyboard

def crypto_list_keyboard(cryptos: List[Dict]):
    builder = InlineKeyboardBuilder()

    for i in range(0, len(cryptos), 2):
        buttons = []
        for j in range(2):
            if i + j < len(cryptos):
                crypto = cryptos[i + j]
                text = crypto['name']
                callback_data = BaseCallbackData(data=f"crypto_{crypto['symbol']}").pack()
                buttons.append(InlineKeyboardButton(text=text, callback_data=callback_data))
        builder.row(*buttons)

    builder.row(
        InlineKeyboardButton(
            text='↩ Назад',
            callback_data=Navigation(data='back', previous='info_assets_keyboard').pack()
        )
    )

    keyboard = builder.as_markup()
    return "Криптовалюты:", keyboard

def select_currencies_keyboard(currencies: List[str], selected: List[str] = None, base_currency: str = None):
    builder = InlineKeyboardBuilder()
    selected = selected or []

    for i in range(0, len(currencies), 2):
        buttons = []
        for j in range(2):
            if i + j < len(currencies):
                currency = currencies[i + j]
                display_currency = f"{currency}⭐" if currency == base_currency else currency
                text = f"✅ {display_currency}" if currency in selected else display_currency
                callback_data = CurrencySelectionCallbackData(step='select', currency=currency).pack()
                buttons.append(InlineKeyboardButton(text=text, callback_data=callback_data))
        builder.row(*buttons)

    if len(selected) == 2:
        selected_currencies = "_".join(selected)
        builder.row(
            InlineKeyboardButton(
                text="✅ Получить информацию",
                callback_data=BaseCallbackData(data=f'currency_{selected_currencies}').pack()
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="↩ Назад",
            callback_data=Navigation(data='back', previous='info_assets_keyboard').pack()
        )
    )

    keyboard = builder.as_markup()
    return "Выберите две валюты:", keyboard

def asset_detail_keyboard(ticker_full: str, is_favorite: bool, is_subscribed: bool, has_alert: bool, add_update_button: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    asset_type, ticker = ticker_full.split("_", 1)

    builder.row(
        InlineKeyboardButton(text='📉 Показать график', callback_data=BaseCallbackData(data=f'show_chart_{ticker_full}').pack())
    )

    if is_subscribed:
        builder.row(
            InlineKeyboardButton(text='🔕 Отписаться от изменений цены', callback_data=BaseCallbackData(data=f'unsubscribe_{ticker_full}').pack())
        )
    else:
        builder.row(
            InlineKeyboardButton(text='🔔 Подписаться на изменения цены', callback_data=BaseCallbackData(data=f'subscribe_{ticker_full}').pack())
        )

    if has_alert:
        builder.row(
            InlineKeyboardButton(text='❌ Удалить ценовой уровень', callback_data=BaseCallbackData(data=f'remove_alert_{ticker_full}').pack())
        )
    else:
        builder.row(
            InlineKeyboardButton(text='⚠ Установить ценовой уровень', callback_data=BaseCallbackData(data=f'set_alert_{ticker_full}').pack())
        )

    if is_favorite:
        builder.row(
            InlineKeyboardButton(text='⭐ Убрать из избранного', callback_data=BaseCallbackData(data=f'remove_favorite_{ticker_full}').pack())
        )
    else:
        builder.row(
            InlineKeyboardButton(text='⭐ Добавить в избранное', callback_data=BaseCallbackData(data=f'add_favorite_{ticker_full}').pack())
        )
    
    builder.row(
        InlineKeyboardButton(
            text='🔄 Обновить информацию', 
            callback_data=BaseCallbackData(data=f'update_info_{ticker_full}').pack()
        )
    )

    return builder.as_markup()