from aiogram import types
from aiogram.types import BotCommandScopeAllGroupChats


async def set_default_commands(dp):
    print("Setting commands")

    default_commands = [
        types.BotCommand(command="random", description="Случайный аят"),
    ]
    await dp.bot.set_my_commands(default_commands)

    group_commands = [
        types.BotCommand(command="random", description="Случайный аят"),
    ]
    await dp.bot.set_my_commands(group_commands, BotCommandScopeAllGroupChats())
