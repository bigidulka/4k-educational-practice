# handlers/command_handlers.py

from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.filters.command import CommandObject

from keyboards.inline import *
from data.database import *
from other.data_manager import *
from utils.utils import send_tokens_to_user
from utils.middlewares import UserTrackingMiddleware, SubscriptionMiddleware 
from utils.filters import IsAdminFilter

user_router = Router()
user_router.message.outer_middleware(UserTrackingMiddleware())

# @user_router.message(Command("get_admin"))
# async def get_admin_command(message: Message, command: CommandObject):
#     if command.args:
#         if command.args == "my_secret_admin_key":
#             user_id = message.from_user.id
#             grant_admin(user_id)
#             await message.answer("Теперь у вас есть права администратора!")
#         else:
#             await message.answer("Неверный секретный ключ.")
#     else:
#         await message.answer("Пожалуйста, укажите секретный ключ.")
        


router = Router()
router.message.outer_middleware(UserTrackingMiddleware())
router.message.outer_middleware(SubscriptionMiddleware())

@router.message(CommandStart())
async def show_main_menu(message: Message):
    message_text, reply_markup = main_menu_keyboard()  
    await message.answer(
        text=message_text,
        reply_markup=reply_markup
    )

@router.message(Command('help'))
async def help_command(message: Message):
    user = get_user(message.from_user.id)
    is_admin = user.is_admin
    message_text, reply_markup = help_menu_keyboard(is_admin)
    await message.answer(text=message_text, reply_markup=reply_markup, parse_mode="Markdown")


# Обработчик для команды /get_set
@router.message(Command('get_set'))
async def get_set_handler(message: Message, command: CommandObject):
    args = command.args
    if args:
        try:
            tf, trade_type = args.split()
            latest_tokens = get_stretch(tf, trade_type.capitalize())
            await send_tokens_to_user(latest_tokens, "tokens_set.txt", tf, trade_type, message)
        except ValueError:
            await message.answer("Использование команды: /get_set <таймфрейм> <тип>")
    else:
        await message.answer("Пожалуйста, укажите таймфрейм и тип сделки (long/short).")

# Обработчик для команды /get_piv
@router.message(Command('get_piv'))
async def get_piv_handler(message: Message, command: CommandObject):
    args = command.args
    if args:
        try:
            tf, trade_type = args.split()
            latest_tokens = get_pivot(tf, trade_type.capitalize())
            await send_tokens_to_user(latest_tokens, "tokens_piv.txt", tf, trade_type, message)
        except ValueError:
            await message.answer("Использование команды: /get_piv <таймфрейм> <тип>")
    else:
        await message.answer("Пожалуйста, укажите таймфрейм и тип сделки (long/short).")

# Обработчик для команды /get_div
@router.message(Command('get_div'))
async def get_div_handler(message: Message, command: CommandObject):
    args = command.args
    if args:
        try:
            tf, trade_type = args.split()
            latest_tokens = get_divergence(tf, trade_type.capitalize())
            await send_tokens_to_user(latest_tokens, "tokens_div.txt", tf, trade_type, message)
        except ValueError:
            await message.answer("Использование команды: /get-div <таймфрейм> <тип>")
    else:
        await message.answer("Пожалуйста, укажите таймфрейм и тип сделки (long/short).")

# Обработчик для команды /get_last_set
@router.message(Command('get_last_set'))
async def get_last_set_handler(message: Message, command: CommandObject):
    args = command.args
    if args:
        try:
            tf, trade_type = args.split()
            latest_tokens, latest_time = get_latest_stretch(tf, trade_type.capitalize())
            await send_tokens_to_user(latest_tokens, "tokens_last_set.txt", tf, trade_type, message)
        except ValueError:
            await message.answer("Использование команды: /get_last_set <таймфрейм> <тип>")
    else:
        await message.answer("Пожалуйста, укажите таймфрейм и тип сделки (long/short).")

# Обработчик для команды /get_last_piv
@router.message(Command('get_last_piv'))
async def get_last_piv_handler(message: Message, command: CommandObject):
    args = command.args
    if args:
        try:
            tf, trade_type = args.split()
            latest_tokens, latest_time = get_latest_pivot(tf, trade_type.capitalize())
            await send_tokens_to_user(latest_tokens, "tokens_last_piv.txt", tf, trade_type, message)
        except ValueError:
            await message.answer("Использование команды: /get_last_piv <таймфрейм> <тип>")
    else:
        await message.answer("Пожалуйста, укажите таймфрейм и тип сделки (long/short).")

# Обработчик для команды /get_last_div
@router.message(Command('get_last_div'))
async def get_last_div_handler(message: Message, command: CommandObject):
    args = command.args
    if args:
        try:
            tf, trade_type = args.split()
            latest_tokens, latest_time = get_latest_divergence(tf, trade_type.capitalize())
            await send_tokens_to_user(latest_tokens, "tokens_last_div.txt", tf, trade_type, message)
        except ValueError:
            await message.answer("Использование команды: /get_last_div <таймфрейм> <тип>")
    else:
        await message.answer("Пожалуйста, укажите таймфрейм и тип сделки (long/short).")
    
# admin

admin_router = Router()
admin_router.message.outer_middleware(UserTrackingMiddleware())

@admin_router.message(IsAdminFilter(), Command('grant_admin'))
async def grant_admin_command(message: Message, command: CommandObject):
    if command.args:
        try:
            user_id = int(command.args)
            grant_admin(user_id)
            await message.answer("Привилегии администратора предоставлены пользователю с ID: {}".format(user_id))
        except:
            await message.answer("Пожалуйста, укажите действительный ID пользователя.")
    else:
        await message.answer("Пожалуйста, укажите ID пользователя.")

@admin_router.message(IsAdminFilter(), Command('revoke_admin'))
async def revoke_admin_command(message: Message, command: CommandObject):
    if command.args:
        try:
            user_id = int(command.args)
            revoke_admin(user_id)
            await message.answer("Привилегии администратора отозваны у пользователя с ID: {}".format(user_id))
        except:
            await message.answer("Пожалуйста, укажите действительный ID пользователя.")
    else:
        await message.answer("Пожалуйста, укажите ID пользователя.")

@admin_router.message(IsAdminFilter(), Command('get_username'))
async def get_username_command(message: Message, command: CommandObject):
    if command.args:
        try:
            user_id = int(command.args)
            username = get_username(user_id)
            if username:
                await message.answer(f"Имя пользователя для ID {user_id} — {username}.")
            else:
                await message.answer("Пользователь не найден для ID: {}".format(user_id))
        except:
            await message.answer("Пожалуйста, укажите действительный ID пользователя.")
    else:
        await message.answer("Пожалуйста, укажите ID пользователя.")

@admin_router.message(IsAdminFilter(), Command('get_all_users'))
async def get_all_users_command(message: Message):
    users = get_all_users()
    users_info = "\n".join([f"ID: {user['id']} ИМЯ: @{user['username']}" for user in users])
    await message.answer(users_info)

@admin_router.message(IsAdminFilter(), Command('grant_subscription'))
async def grant_subscription_command(message: Message, command: CommandObject):
    if command.args:
        args = command.args.split()
        if len(args) == 2:
            try:
                user_id = int(args[0])
                days = int(args[1])
                grant_subscription(user_id, days)
                await message.answer(f"Подписка предоставлена пользователю с ID {user_id} на {days} дней.")
            except ValueError:
                await message.answer("Пожалуйста, укажите действительный ID пользователя и количество дней.")
        else:
            await message.answer("Использование: /grant_subscription <user_id> <days>")
    else:
        await message.answer("Пожалуйста, укажите ID пользователя и количество дней.")

@admin_router.message(IsAdminFilter(), Command('revoke_subscription'))
async def revoke_subscription_command(message: Message, command: CommandObject):
    if command.args:
        try:
            user_id = int(command.args)
            revoke_subscription(user_id)
            await message.answer(f"Подписка отозвана у пользователя с ID {user_id}.")
        except ValueError:
            await message.answer("Пожалуйста, укажите действительный ID пользователя.")
    else:
        await message.answer("Пожалуйста, укажите ID пользователя.")

@admin_router.message(IsAdminFilter(), Command('get_subscribed_users'))
async def get_subscribed_users_command(message: Message):
    users = get_all_subscribed_users()
    if users:
        users_info = "\n".join([
            f"ID: {user['id']} | Имя пользователя: @{user['username']} | Подписка заканчивается: {user['subscription_end'].strftime('%Y-%m-%d %H:%M:%S')}"
            for user in users
        ])
        await message.answer(f"Подписанные пользователи:\n{users_info}")
    else:
        await message.answer("В данный момент у пользователей нет активной подписки.")

# Обработчик для команды /filter
@router.message(Command('filter'))
async def filter_handler(message: Message, command: CommandObject):
    args = command.args
    if args and args.lower() == 'help':
        # Если аргумент "help", возвращаем справочную информацию
        help_text = filter_help_menu()
        await message.answer(help_text, parse_mode="Markdown")
    elif args:
        try:
            direction, timeframe_conditions = parse_conditions(args)
            
            filtered_coins = filter_coins(direction.capitalize(), timeframe_conditions)
            if filtered_coins:
                file_name = 'filtered_tokens.txt'
                await send_tokens_to_user(list(filtered_coins.keys()), file_name, message=message, trade_type=None, tf=None)
            else:
                await message.answer("Нет токенов, соответствующих условиям.")
                
        except Exception as e:
            # Выводим информацию об ошибке пользователю для отладки
            await message.answer(f"Ошибка: {str(e)}")
    else:
        await message.answer("Использование команды: /filter help")
