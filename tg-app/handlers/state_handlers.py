# handlers/state_handlers.py

from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.middlewares import UserTrackingMiddleware, SubscriptionMiddleware 
from keyboards.inline import (
    FilterCallbackData, BaseCallbackData, timeframe_selection_keyboard, 
    parameter_selection_keyboard, operator_selection_keyboard
)
from utils.states import FilterStates
from utils.utils import finalize_condition

router = Router()
router.callback_query.outer_middleware(UserTrackingMiddleware())
router.callback_query.outer_middleware(SubscriptionMiddleware())

# Обработчик ввода значения
@router.message(FilterStates.entering_value)
async def enter_value(message: types.Message, state: FSMContext):
    value = message.text.strip()
    if not value.isdigit():
        await message.answer("Пожалуйста, введите корректное число.")
        return
    await finalize_condition(message, state, value=value)

# Обработчик выбора таймфрейма
@router.callback_query(FilterCallbackData.filter(F.action == 'select_timeframe'), FilterStates.selecting_timeframe)
async def select_timeframe_handler(call: CallbackQuery, state: FSMContext, callback_data: FilterCallbackData):
    timeframe = callback_data.additional
    data = await state.get_data()
    current_filter = data.get('current_filter', [])
    
    # Извлекаем уже использованные таймфреймы
    existing_timeframes = [cond.split(':')[0].strip() for cond in current_filter if ':' in cond]
    
    if timeframe in existing_timeframes:
        # Таймфрейм уже используется, предложим выбрать AND/OR
        await state.update_data(selected_timeframe=timeframe)
        message_text = "Таймфрейм уже используется. Выберите логический оператор для соединения условий:"
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text='AND', callback_data=BaseCallbackData(data='add_and').pack()))
        keyboard.add(InlineKeyboardButton(text='OR', callback_data=BaseCallbackData(data='add_or').pack()))
        keyboard.row(InlineKeyboardButton(text='🔙 Вернуться в редактор', callback_data=BaseCallbackData(data='return_to_editor').pack()))
        await call.message.edit_text(text=message_text, reply_markup=keyboard.as_markup())
        await state.set_state(FilterStates.choosing_logical_operator)
    else:
        # Таймфрейм не используется, продолжаем выбор параметра
        await state.update_data(selected_timeframe=timeframe)
        await call.message.edit_text(text="Выберите параметр для фильтра:", reply_markup=parameter_selection_keyboard()[1])
        await state.set_state(FilterStates.selecting_parameter)
        await call.answer()

# Обработчик выбора параметра
@router.callback_query(FilterCallbackData.filter(F.action == 'select_parameter'), FilterStates.selecting_parameter)
async def select_parameter_handler(call: CallbackQuery, state: FSMContext, callback_data: FilterCallbackData):
    parameter = callback_data.additional
    await state.update_data(selected_parameter=parameter)
    await call.message.edit_text(text="Выберите логическое выражение:", reply_markup=operator_selection_keyboard()[1])
    await state.set_state(FilterStates.selecting_operator)
    await call.answer()
        
# Обработчик выбора оператора
@router.callback_query(FilterCallbackData.filter(F.action == 'select_operator'), FilterStates.selecting_operator)
async def select_operator_handler(call: CallbackQuery, state: FSMContext, callback_data: FilterCallbackData):
    operator = callback_data.additional
    await state.update_data(selected_operator=operator)
    if operator in [">=", "<="]:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text='🔙 Вернуться в редактор', callback_data=BaseCallbackData(data='return_to_editor').pack()))
        await call.message.edit_text(text="Введите значение (число):", reply_markup=keyboard.as_markup())  # Убираем клавиатуру
        await state.set_state(FilterStates.entering_value)
    else:
        # Для "Наличие" не требуется значение
        await finalize_condition(call, state, value=None)
