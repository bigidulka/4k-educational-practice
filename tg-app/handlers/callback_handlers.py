# handlers/callback_handlers.py

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
import sys

from keyboards.inline import *
from data.database import *
from other.data_manager import get_tokens, fetch_tokens
from utils.utils import handle_telegram_exception, form_telegram_message
from utils.states import FilterStates
from utils.middlewares import UserTrackingMiddleware, SubscriptionMiddleware 
from aiogram.types import CallbackQuery
from utils.utils import finalize_condition

router = Router()
router.callback_query.outer_middleware(UserTrackingMiddleware())
router.callback_query.outer_middleware(SubscriptionMiddleware())

# Обработчик кнопки "Фильтры" в основном меню
@router.callback_query(BaseCallbackData.filter(F.data == 'filters'))
@handle_telegram_exception
async def show_filters_menu(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    message_text, keyboard = filters_menu_keyboard()
    await call.message.edit_text(text=message_text, reply_markup=keyboard)
    await call.answer()

# Обработчик для создания нового фильтра
@router.callback_query(BaseCallbackData.filter(F.data == 'create_filter'))
@handle_telegram_exception
async def create_new_filter(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    await state.update_data(current_filter=[])
    await state.set_state(FilterStates.editing)
    message_text, keyboard = filter_editor_keyboard(current_filter=[])
    await call.message.edit_text(text=message_text, reply_markup=keyboard)
    await call.answer()

# Обработчик для добавления условия
@router.callback_query(BaseCallbackData.filter(F.data == 'add_condition'), FilterStates.editing)
@handle_telegram_exception
async def add_condition_handler(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    await call.message.edit_text(text="Выберите таймфрейм:", reply_markup=timeframe_selection_keyboard()[1])
    await state.set_state(FilterStates.selecting_timeframe)
    await call.answer()

# Обработчик выбора логического оператора (AND/OR)
@router.callback_query(BaseCallbackData.filter(F.data.in_(['add_and', 'add_or'])), FilterStates.choosing_logical_operator)
@handle_telegram_exception
async def choose_logical_operator_handler(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    logical_operator = 'AND' if callback_data.data == 'add_and' else 'OR'
    await state.update_data(logical_operator=logical_operator)
    # Продолжаем выбор параметра
    await call.message.edit_text(text="Выберите параметр для фильтра:", reply_markup=parameter_selection_keyboard()[1])
    await state.set_state(FilterStates.selecting_parameter)
    await call.answer()

# Обработчик удаления последнего элемента
@router.callback_query(BaseCallbackData.filter(F.data == 'delete_last'), FilterStates.editing)
@handle_telegram_exception
async def delete_last_handler(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    data = await state.get_data()
    current_filter = data.get('current_filter', [])
    
    if current_filter:
        # Удаляем последнее условие
        removed = current_filter.pop()
        
        # Если после удаления условия в списке остался логический оператор, удаляем его
        if current_filter and current_filter[-1] in ['AND', 'OR']:
            removed_operator = current_filter.pop()  # Удаляем предшествующий оператор
            await call.answer(f"Удалено: {removed} и оператор {removed_operator}")
        else:
            await call.answer(f"Удалено: {removed}")
        
        # Обновляем данные и текст фильтра
        await state.update_data(current_filter=current_filter)
        filter_text = "\n".join(current_filter) if current_filter else "Фильтр пуст."
        message_text, keyboard = filter_editor_keyboard(current_filter=current_filter)
        await call.message.edit_text(text=message_text, reply_markup=keyboard)
    else:
        await call.answer("Фильтр уже пуст.")

# Обработчик сохранения и выхода
@router.callback_query(BaseCallbackData.filter(F.data == 'save_exit'), FilterStates.editing)
@handle_telegram_exception
async def save_and_exit_handler(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    data = await state.get_data()
    current_filter = data.get('current_filter', [])
    filter_str = "\n".join(current_filter) if current_filter else ""
    
    user_id = call.from_user.id
    
    await state.clear()
    await call.message.edit_text(text="Фильтр сохранен.", reply_markup=None)
    await call.answer("Фильтр успешно сохранен.")

# Обработчик выхода без сохранения
@router.callback_query(BaseCallbackData.filter(F.data == 'exit'), FilterStates.editing)
@handle_telegram_exception
async def exit_without_saving_handler(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    await state.clear()
    await call.message.edit_text(text="Редактор фильтров закрыт без сохранения.", reply_markup=None)
    await call.answer("Выход без сохранения.")

# Обработчик возврата в редактор из выбора логического оператора или других шагов
@router.callback_query(BaseCallbackData.filter(F.data == 'return_to_editor'))
@handle_telegram_exception
async def return_to_editor_handler(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    data = await state.get_data()
    current_filter = data.get('current_filter', [])
    filter_text = "\n".join(current_filter) if current_filter else "Фильтр пуст."
    message_text, keyboard = filter_editor_keyboard(current_filter=current_filter)
    await call.message.edit_text(text=message_text, reply_markup=keyboard)
    await state.set_state(FilterStates.editing)
    await call.answer("Возврат в редактор.")

# Обработчик неизвестных действий
@router.callback_query(BaseCallbackData.filter(), FilterStates.editing)
@handle_telegram_exception
async def handle_unknown_filters_actions(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    await call.answer("Неизвестное действие.")

    
    
    
    
    
    
    
    
    
    

@router.callback_query(BaseCallbackData.filter(F.data == 'settings'))
@handle_telegram_exception
async def show_settings_menu(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    message_text, reply_markup = settings_menu_keyboard()
    await call.message.edit_text(text=message_text, reply_markup=reply_markup)
    await call.answer()
    
@router.callback_query(BaseCallbackData.filter(F.data == 'tokens'))
@handle_telegram_exception
async def handle_tokens(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    data = get_tokens()
    await state.update_data(tokens_data=data)
    items = list(data.keys())
    page = 1
    per_page = 10
    message_text, reply_markup = paginated_tokens_menu_keyboard(items=items, page=page, per_page=per_page)
    await call.message.edit_text(text=message_text, reply_markup=reply_markup)
    await call.answer()

@router.callback_query(Pagination.filter(F.data == 'change_token_page'))
@handle_telegram_exception
async def change_token_page(call: CallbackQuery, state: FSMContext, callback_data: Pagination, user_settings, **kwargs):
    page = callback_data.page
    state_data = await state.get_data()
    tokens_data = state_data.get('tokens_data', {})
    items = list(tokens_data.keys())
    per_page = 10
    message_text, reply_markup = paginated_tokens_menu_keyboard(items=items, page=page, per_page=per_page)
    await call.message.edit_text(text=message_text, reply_markup=reply_markup)
    await call.answer()
    
@router.callback_query(BaseCallbackData.filter(F.data == 'refresh_tokens'))
@handle_telegram_exception
async def refresh_tokens(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    await fetch_tokens()
    data = get_tokens()
    await state.update_data(tokens_data=data)
    items = list(data.keys())
    page = 1
    per_page = 10
    message_text, reply_markup = paginated_tokens_menu_keyboard(items=items, page=page, per_page=per_page)
    await call.message.edit_text(text=message_text, reply_markup=reply_markup)
    await call.answer("Информация обновлена.")
    
@router.callback_query(BaseCallbackData.filter(F.data.startswith('token_')))
@handle_telegram_exception
async def handle_token_selection(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    token = '_'.join(callback_data.data.split('_')[1:])
    
    state_data = await state.get_data()
    tokens_data = state_data.get('tokens_data', {})

    if token not in tokens_data:
        await call.answer("Монета не найдена.")
        return

    long_list = user_settings.get('long_list', [])
    short_list = user_settings.get('short_list', [])

    data = tokens_data[token]
    message = form_telegram_message(data, token)

    if token in long_list:
        message += "\n🥬 В Лонг листе"
    if token in short_list:
        message += "\n🍁 В Шорт листе"

    await call.message.answer(text=message, reply_markup=token_selection_keyboard(token))
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data.startswith('add_long_list_')))
@handle_telegram_exception
async def add_to_long_list(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    token = '_'.join(callback_data.data.split('_')[3:])

    user_id = call.from_user.id

    long_list = user_settings.get('long_list', [])
    short_list = user_settings.get('short_list', [])

    if token in long_list:
        remove_item_from_user_list_setting(user_id, ['long_list'], token)
        tokens_data = (await state.get_data()).get('tokens_data', {})
        data = tokens_data.get(token, {})
        message = form_telegram_message(data, token)
        await call.message.edit_text(text=message, reply_markup=token_selection_keyboard(token))
        await call.answer(f"Монета {token} удалена из Лонг листа.")
        return

    if token in short_list:
        remove_item_from_user_list_setting(user_id, ['short_list'], token)

    add_item_to_user_list_setting(user_id, ['long_list'], token)

    tokens_data = (await state.get_data()).get('tokens_data', {})
    data = tokens_data.get(token, {})
    message = form_telegram_message(data, token) + "\n🥬 В Лонг листе"

    await call.message.edit_text(text=message, reply_markup=token_selection_keyboard(token))
    await call.answer(f"Монета {token} перемещена в Лонг лист.")

@router.callback_query(BaseCallbackData.filter(F.data.startswith('refresh_single_token_')))
@handle_telegram_exception
async def refresh_single_token(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    token = '_'.join(callback_data.data.split('_')[3:])
    
    await fetch_tokens()
    data = get_tokens()
    await state.update_data(tokens_data=data)
    
    tokens_data = (await state.get_data()).get('tokens_data', {})
    token_data = tokens_data.get(token, {})
    
    if not token_data:
        await call.answer(f"Монета {token} не найдена.")
        return
    
    message = form_telegram_message(token_data, token)
    await call.message.edit_text(text=message, reply_markup=token_selection_keyboard(token))
    await call.answer(f"Монета {token} обновлена.")

@router.callback_query(BaseCallbackData.filter(F.data.startswith('add_short_list_')))
@handle_telegram_exception
async def add_to_short_list(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    token = '_'.join(callback_data.data.split('_')[3:])

    user_id = call.from_user.id

    long_list = user_settings.get('long_list', [])
    short_list = user_settings.get('short_list', [])

    if token in short_list:
        remove_item_from_user_list_setting(user_id, ['short_list'], token)
        tokens_data = (await state.get_data()).get('tokens_data', {})
        data = tokens_data.get(token, {})
        message = form_telegram_message(data, token)
        await call.message.edit_text(text=message, reply_markup=token_selection_keyboard(token))
        await call.answer(f"Монета {token} удалена из Шорт листа.")
        return

    if token in long_list:
        remove_item_from_user_list_setting(user_id, ['long_list'], token)

    add_item_to_user_list_setting(user_id, ['short_list'], token)

    tokens_data = (await state.get_data()).get('tokens_data', {})
    data = tokens_data.get(token, {})
    message = form_telegram_message(data, token) + "\n🍁 В Шорт листе"

    await call.message.edit_text(text=message, reply_markup=token_selection_keyboard(token))
    await call.answer(f"Монета {token} перемещена в Шорт лист.")

@router.callback_query(BaseCallbackData.filter(F.data == 'help'))
@handle_telegram_exception
async def show_help_menu(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    user = get_user(call.from_user.id)
    is_admin = user.is_admin
    message_text, reply_markup = help_menu_keyboard(is_admin)
    await call.message.edit_text(text=message_text, reply_markup=reply_markup, parse_mode="Markdown")
    await call.answer()
    
@router.callback_query(BaseCallbackData.filter(F.data == 'tracking'))
@handle_telegram_exception
async def show_tracking_menu(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    message_text, reply_markup = tracking_menu_keyboard()
    await call.message.edit_text(text=message_text, reply_markup=reply_markup)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data == 'long_list'))
@handle_telegram_exception
async def show_long_list(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    long_list = user_settings.get('long_list', [])
    message_text, reply_markup = long_list_menu_keyboard(long_list)
    await call.message.edit_text(text=message_text, reply_markup=reply_markup)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data == 'short_list'))
@handle_telegram_exception
async def show_short_list(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    short_list = user_settings.get('short_list', [])
    message_text, reply_markup = short_list_menu_keyboard(short_list)
    await call.message.edit_text(text=message_text, reply_markup=reply_markup)
    await call.answer()

@router.callback_query(BaseCallbackData.filter(F.data.startswith('remove_long_list_')))
@handle_telegram_exception
async def remove_from_long_list(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    token = '_'.join(callback_data.data.split('_')[3:])
    user_id = call.from_user.id
    remove_item_from_user_list_setting(user_id, ['long_list'], token)
    
    user_settings = get_user_settings(user_id)
    long_list = user_settings.get('long_list', [])
    message_text, reply_markup = long_list_menu_keyboard(long_list)
    await call.message.edit_text(text=message_text, reply_markup=reply_markup)
    await call.answer(f"Монета {token} удалена из Лонг листа.")

@router.callback_query(BaseCallbackData.filter(F.data.startswith('remove_short_list_')))
@handle_telegram_exception
async def remove_from_short_list(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    token = '_'.join(callback_data.data.split('_')[3:])
    user_id = call.from_user.id
    remove_item_from_user_list_setting(user_id, ['short_list'], token)
    
    user_settings = get_user_settings(user_id)
    short_list = user_settings.get('short_list', [])
    message_text, reply_markup = short_list_menu_keyboard(short_list)
    await call.message.edit_text(text=message_text, reply_markup=reply_markup)
    await call.answer(f"Монета {token} удалена из Шорт листа.")
    
@router.callback_query(BaseCallbackData.filter(F.data == 'close'))
@handle_telegram_exception
async def handle_close(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    await call.message.delete()
    await call.answer()

@router.callback_query(BaseCallbackData.filter())
@handle_telegram_exception
async def handle_remaining_callbacks(call: CallbackQuery, state: FSMContext, callback_data: BaseCallbackData, user_settings, **kwargs):
    print('none')
    await call.answer()
    
@router.callback_query(Navigation.filter())
@handle_telegram_exception
async def go_back(call: CallbackQuery, callback_data: Navigation, state: FSMContext, user_settings, **kwargs):
    if callback_data.callback_func != 'None':
        func_to_call = getattr(sys.modules[__name__], callback_data.callback_func)
        await func_to_call(call, state, callback_data, user_settings, **kwargs)
    else:
        func_to_call = getattr(sys.modules[__name__], callback_data.previous)
        message_text, reply_markup = func_to_call()
        
        await call.message.edit_text(text=message_text, reply_markup=reply_markup)
        await state.clear()
        await call.answer()