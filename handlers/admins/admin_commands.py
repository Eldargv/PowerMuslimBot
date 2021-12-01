from aiogram import types
from loader import dp


@dp.message_handler(chat_type="private", commands="send_message", user_id=916354662)
async def new_user_start(message: types.Message):
    await dp.bot.send_message(-1001444174142, message.text.replace("/send_message", ''))


@dp.message_handler(chat_type=('group', 'supergroup'), is_reply=True)
async def new_user_start(message: types.Message):
    await dp.bot.forward_message(916354662, message.chat.id, message.message_id)
