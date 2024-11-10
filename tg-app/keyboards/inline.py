# keyboards/inline.py

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from typing import Optional, List

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

# Клавиатура для меню фильтров
def filters_menu_keyboard():
    message_text = "Вы в разделе фильтров:"
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Создать новый фильтр', callback_data=BaseCallbackData(data='create_filter').pack()))
    builder.row(InlineKeyboardButton(text='🔙 Назад', callback_data=Navigation(data='back', previous='main_menu_keyboard').pack()))
    keyboard = builder.as_markup()
    return message_text, keyboard

# Клавиатура редактора фильтров
def filter_editor_keyboard(current_filter: List[str]):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Добавить условие', callback_data=BaseCallbackData(data='add_condition').pack()))
    builder.row(InlineKeyboardButton(text='Удалить последнее', callback_data=BaseCallbackData(data='delete_last').pack()))
    builder.row(InlineKeyboardButton(text='Сохранить и выйти', callback_data=BaseCallbackData(data='save_exit').pack()))
    builder.row(InlineKeyboardButton(text='Выйти без сохранения', callback_data=BaseCallbackData(data='exit').pack()))
    keyboard = builder.as_markup()
    
    # Форматирование фильтра с условиями на отдельных строках
    if current_filter:
        filter_text = "\n".join(current_filter)
    else:
        filter_text = "Фильтр пуст."
    
    message_text = f"Редактор фильтров:\nВаш фильтр:\n{filter_text}"
    return message_text, keyboard

# Клавиатуры для выбора таймфрейма, параметра и оператора с кнопкой возврата
def timeframe_selection_keyboard():
    builder = InlineKeyboardBuilder()
    timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
    for tf in timeframes:
        builder.add(InlineKeyboardButton(text=tf, callback_data=FilterCallbackData(action='select_timeframe', additional=tf).pack()))
    builder.row(InlineKeyboardButton(text='🔙 Вернуться в редактор', callback_data=BaseCallbackData(data='return_to_editor').pack()))
    keyboard = builder.as_markup()
    return "Выберите таймфрейм:", keyboard

def parameter_selection_keyboard():
    builder = InlineKeyboardBuilder()
    parameters = ["Пивот", "Дивергенция"]
    for param in parameters:
        builder.add(InlineKeyboardButton(text=param, callback_data=FilterCallbackData(action='select_parameter', additional=param).pack()))
    builder.row(InlineKeyboardButton(text='🔙 Вернуться в редактор', callback_data=BaseCallbackData(data='return_to_editor').pack()))
    keyboard = builder.as_markup()
    return "Выберите параметр для фильтра:", keyboard

def operator_selection_keyboard():
    builder = InlineKeyboardBuilder()
    operators = [">=", "<=", "Наличие"]
    for op in operators:
        builder.add(InlineKeyboardButton(text=op, callback_data=FilterCallbackData(action='select_operator', additional=op).pack()))
    builder.row(InlineKeyboardButton(text='🔙 Вернуться в редактор', callback_data=BaseCallbackData(data='return_to_editor').pack()))
    keyboard = builder.as_markup()
    return "Выберите логическое выражение:", keyboard

# # Главное меню

def main_menu_keyboard():
    message_text = "Привет! Что вы хотите сделать?"
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Настройки', callback_data=BaseCallbackData(data='settings').pack()))
    builder.add(InlineKeyboardButton(text='ЛК', callback_data=BaseCallbackData(data='profile').pack()))
    builder.add(InlineKeyboardButton(text='Помощь', callback_data=BaseCallbackData(data='help').pack()))
    builder.row(InlineKeyboardButton(text='Список монет', callback_data=BaseCallbackData(data='tokens').pack()))
    builder.row(InlineKeyboardButton(text='Отслеживание', callback_data=BaseCallbackData(data='tracking').pack()))
    builder.row(InlineKeyboardButton(text='Фильтры', callback_data=BaseCallbackData(data='filters').pack()))
    keyboard = builder.as_markup()
    return message_text, keyboard

# Меню отслеживания (лонг и шорт лист)
def tracking_menu_keyboard():
    message_text = "Меню отслеживания:"
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Лонг лист', callback_data=BaseCallbackData(data='long_list').pack()))
    builder.add(InlineKeyboardButton(text='Шорт лист', callback_data=BaseCallbackData(data='short_list').pack()))
    builder.row(InlineKeyboardButton(text='🔙 Назад', callback_data=Navigation(data='back', previous='main_menu_keyboard').pack()))
    keyboard = builder.as_markup()
    return message_text, keyboard

# Меню лонг листа
def long_list_menu_keyboard(long_list):
    if not long_list:
        message_text = "Лонг лист пуст."
    else:
        message_text = "Ваш Лонг лист:"
    
    builder = InlineKeyboardBuilder()
    
    for token in long_list:
        builder.row(
            InlineKeyboardButton(text=token, callback_data=BaseCallbackData(data=f'token_{token}').pack()),
            InlineKeyboardButton(text="❌", callback_data=BaseCallbackData(data=f'remove_long_list_{token}').pack())
        )
    
    builder.row(InlineKeyboardButton(text='🔙 Назад', callback_data=Navigation(data='back', previous='tracking_menu_keyboard').pack()))
    keyboard = builder.as_markup()
    
    return message_text, keyboard

# Меню шорт листа
def short_list_menu_keyboard(short_list):
    if not short_list:
        message_text = "Шорт лист пуст."
    else:
        message_text = "Ваш Шорт лист:"
    
    builder = InlineKeyboardBuilder()
    
    for token in short_list:
        builder.row(
            InlineKeyboardButton(text=token, callback_data=BaseCallbackData(data=f'token_{token}').pack()),
            InlineKeyboardButton(text="❌", callback_data=BaseCallbackData(data=f'remove_short_list_{token}').pack())
        )
    
    builder.row(InlineKeyboardButton(text='🔙 Назад', callback_data=Navigation(data='back', previous='tracking_menu_keyboard').pack()))
    keyboard = builder.as_markup()
    
    return message_text, keyboard

# # Настройки 

def settings_menu_keyboard():
    message_text = "Настройки:"
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Уведомления', callback_data=BaseCallbackData(data='notifications').pack()))
    builder.row(InlineKeyboardButton(text='🔙 Назад', callback_data=Navigation(data='back', previous='main_menu_keyboard').pack()))
    keyboard = builder.as_markup()
    return message_text, keyboard

def paginated_tokens_menu_keyboard(items, page=1, per_page=5):
    total_items = len(items)
    if not items:
        message_text = "На данный момент монет нет, попробуйте позже."
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='🔄 Обновить', callback_data=BaseCallbackData(data='refresh_tokens').pack()))
        builder.row(InlineKeyboardButton(text='🔙 Назад', callback_data=Navigation(data='back', previous='main_menu_keyboard').pack()))
        return message_text, builder.as_markup()

    total_pages = (total_items - 1) // per_page + 1
    message_text = f"Выберите монету (страница {page}/{total_pages}):"
    builder = InlineKeyboardBuilder()
    start = (page - 1) * per_page
    end = start + per_page

    for item_key in items[start:min(end, total_items)]:
        display_text = item_key
        builder.row(InlineKeyboardButton(text=display_text, callback_data=BaseCallbackData(data=f'token_{item_key}').pack()))

    navigation_row = []
    if page > 1:
        navigation_row.append(InlineKeyboardButton(text="⬅️", callback_data=Pagination(data='change_token_page', page=page-1).pack()))
    navigation_row.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data=BaseCallbackData(data='noop').pack()))
    if page < total_pages:
        navigation_row.append(InlineKeyboardButton(text="➡️", callback_data=Pagination(data='change_token_page', page=page+1).pack()))
    if navigation_row:
        builder.row(*navigation_row)

    builder.row(InlineKeyboardButton(text='🔄 Обновить', callback_data=BaseCallbackData(data='refresh_tokens').pack()))
    builder.row(InlineKeyboardButton(text='🔙 Назад', callback_data=Navigation(data='back', previous='main_menu_keyboard').pack()))

    return message_text, builder.as_markup()

def help_menu_keyboard(is_admin):
    message_text = "🔹 Список доступных команд:\n\n"
    message_text += "📊 Таймфрейм (1d, 12h, 8h, 4h, 2h, 1h), Тип (long, short):\n"
    
    message_text += "✨ Основные команды:\n"
    message_text += "▫️ `/start` — Начать работу с ботом\n"
    message_text += "▫️ `/help` — Показать это меню\n\n"
    
    message_text += "📊 Команды для получения данных:\n"
    message_text += "▫️ `/get_set <таймфрейм> <тип>` — Получить токены с растяжкой\n"
    message_text += "Пример: `/get_set 1d long`\n\n"
    
    message_text += "▫️ `/get_piv <таймфрейм> <тип>` — Получить токены с пивотом\n"
    message_text += "Пример: `/get_piv 4h short`\n\n"
    
    message_text += "▫️ `/get_div <таймфрейм> <тип>` — Получить токены с дивергенцией\n"
    message_text += "Пример: `/get_div 12h long`\n\n"
    
    message_text += "🔄 Последние данные:\n"
    message_text += "▫️ `/get_last_set <таймфрейм> <тип>` — Получить последние токены с растяжкой\n"
    message_text += "Пример: `/get_last_set 1d short`\n\n"
    
    message_text += "▫️ `/get_last_piv <таймфрейм> <тип>` — Получить последние токены с пивотом\n"
    message_text += "Пример: `/get_last_piv 8h long`\n\n"
    
    message_text += "▫️ `/get_last_div <таймфрейм> <тип>` — Получить последние токены с дивергенцией\n"
    message_text += "Пример: `/get_last_div 4h short`\n\n"

    message_text += "🔍 Поиск токенов по хэштегу:\n"
    message_text += "▫️ Просто введите токен с #, например: `#BTC`, чтобы найти нужные токены.\n\n"
    
    message_text += "🧑‍🔬 Продвинутая фильтрация:\n"
    message_text += "▫️ Используйте команду `/filter` для фильтрации токенов по техническим условиям.\n"
    message_text += "▫️ Для более подробной информации введите `/filter help`.\n\n"

    if is_admin:
        message_text += "🔐 Административные команды (доступны только администраторам):\n"
        message_text += "`/grant_admin <user_id>` - Выдать права администратора пользователю\n"
        message_text += "`/revoke_admin <user_id>` - Забрать права администратора у пользователя\n"
        message_text += "`/get_username <user_id>` - Получить имя пользователя по ID\n"
        message_text += "`/get_all_users` - Получить список всех пользователей\n"
        message_text += "`/grant_subscription <user_id> <days>` - Выдать подписку пользователю на N дней\n"
        message_text += "`/revoke_subscription <user_id>` - Отменить подписку пользователя\n"
        message_text += "`/get_subscribed_users` - Получить список пользователей с подпиской и сроком ее окончания\n"
        
        message_text += "\nОбозначения:\n"
        message_text += "🧨 - Последняя растяжка (Last stretch)\n"
        message_text += "🟩 - Дивергенция для лонг-позиций (Divergence Long)\n"
        message_text += "🟥 - Дивергенция для шорт-позиций (Divergence Short)\n"
        message_text += "🔶 - Пивот для лонг/шорт позиций (Pivot Long/Short)\n"
        message_text += "⚪️ - Пустое значение (Empty)\n"

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='🔙 Назад', callback_data=Navigation(data='back', previous='main_menu_keyboard').pack()))
    keyboard = builder.as_markup()

    return message_text, keyboard

def filter_help_menu():
    message_text = "🔹 Команда `/filter` используется для фильтрации токенов на основе технических условий.\n\n"
    message_text += "📊 Формат команды:\n"
    message_text += "▫️ `/filter <направление>`\n"
    message_text += "`<таймфрейм>`: `<условия>` and `<условия>` or `<условия>`\n"
    message_text += "Где:\n"
    message_text += "▫️ `<направление>` — это тип сделки (`Long` или `Short`).\n"
    message_text += "▫️ `<таймфрейм>` — это период анализа (например: `1d`, `12h`, `8h`, `4h`, `2h`, `1h`).\n"
    message_text += "▫️ `<условия>` — это фильтры, которые применяются к данным. Можно использовать несколько условий через `and` и/или `or`.\n\n"
    
    message_text += "📊 Поддерживаемые метрики:\n"
    message_text += "▫️ `cs_stretch` — Свечи с момента последней растяжки (🧨).\n"
    message_text += "▫️ `cs_div` — Свечи с момента последней дивергенции (🟩 для Long и 🟥 для Short).\n"
    message_text += "▫️ `cs_pivot` — Свечи с момента последнего пивота (🔶).\n\n"
    
    message_text += "📊 Поддерживаемые операторы:\n"
    message_text += "▫️ `=` — равно.\n"
    message_text += "▫️ `<=` — меньше или равно.\n"
    message_text += "▫️ `>=` — больше или равно.\n"
    message_text += "▫️ `<` — меньше.\n"
    message_text += "▫️ `>` — больше.\n\n"
    
    message_text += "📊 Операторы `and` и `or`:\n"
    message_text += "▫️ `and` — оба условия должны быть выполнены.\n"
    message_text += "▫️ `or` — одно из условий должно быть выполнено.\n"
    message_text += "Вы можете комбинировать несколько условий через `and` и/или `or` для создания сложных фильтров.\n\n"
    
    message_text += "📊 Примеры использования:\n"
    
    message_text += "▫️ `/filter Long\n1d: cs_stretch <= 50 and cs_div >= 10`\n"
    message_text += "Фильтрация по длинным позициям на таймфрейме 1d, где:\n"
    message_text += "  - Свечей с момента последней растяжки должно быть ≤ 50.\n"
    message_text += "  - Свечей с момента последней дивергенции должно быть ≥ 10.\n\n"
    
    message_text += "▫️ `/filter Short\n4h: cs_pivot > 20`\n"
    message_text += "Фильтрация по коротким позициям на таймфрейме 4h, где:\n"
    message_text += "  - Свечей с момента последнего пивота должно быть > 20.\n\n"
    
    message_text += "▫️ `/filter Long\n1d: cs_stretch <= 50 or cs_div >= 10`\n"
    message_text += "Фильтрация по длинным позициям на таймфрейме 1d, где должно быть выполнено хотя бы одно из условий:\n"
    message_text += "  - Свечей с момента последней растяжки ≤ 50.\n"
    message_text += "  - Или свечей с момента последней дивергенции ≥ 10.\n\n"
    
    message_text += "▫️ `/filter Long\n1d: cs_stretch <= 50 and cs_div >= 10\n4h: cs_pivot > 15 and cs_stretch <= 30`\n"
    message_text += "Фильтрация по длинным позициям на таймфреймах 1d и 4h, где:\n"
    message_text += "  - На таймфрейме 1d: свечей с момента последней растяжки ≤ 50 и свечей с момента последней дивергенции ≥ 10.\n"
    message_text += "  - На таймфрейме 4h: свечей с момента последнего пивота > 15 и свечей с момента последней растяжки ≤ 30.\n\n"
    
    message_text += "📊 Ошибки и предупреждения:\n"
    message_text += "▫️ Если команда составлена некорректно или содержит недопустимые операторы, бот вернет сообщение:\n"
    message_text += "Неверная конструкция. Пожалуйста, проверьте формат команды.\n\n"

    return message_text

def token_selection_keyboard(item_key):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🥬", callback_data=BaseCallbackData(data=f'add_long_list_{item_key}').pack()),
        InlineKeyboardButton(text="🍁", callback_data=BaseCallbackData(data=f'add_short_list_{item_key}').pack()),
        InlineKeyboardButton(text="🔄", callback_data=BaseCallbackData(data=f'refresh_single_token_{item_key}').pack()),
        InlineKeyboardButton(text="❌", callback_data=BaseCallbackData(data=f'close').pack())
    )
    return builder.as_markup()