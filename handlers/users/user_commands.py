from aiogram import types, filters
from loader import dp
from utils.Quran_api import Quran_parser as Quran
from keyboards.inline import keyboard


@dp.message_handler(chat_type="private", commands="start")
async def new_user_start(message: types.Message):
    await message.answer(
        "Ас-саляму алейкум! Напиши /random, чтобы прочитать случайный аят, или отправь номер суры и аята!"
    )


@dp.message_handler(chat_type="private", commands="random")
async def send_random_ayah_in_private(message: types.Message):
    num = Quran.get_random_ayah()
    text = Quran.get_ayah_by_num(num)
    await message.answer(text, reply_markup=keyboard.get_keyboard(
        'ayahFromPrivate_',
        Quran.get_prev_ayah(Quran.get_real_ayah_num(num)),
        Quran.get_next_ayah(Quran.get_real_ayah_num(num))
    ))


@dp.message_handler(chat_type="private")
async def send_specific_ayah_in_private(message: types.Message):
    num = message.text
    text = Quran.get_ayah_by_num(num)
    if text == 'Такого аята нет (':
        await message.answer(text)
        return
    await message.answer(text, reply_markup=keyboard.get_keyboard(
        'ayahFromPrivate_',
        Quran.get_prev_ayah(Quran.get_real_ayah_num(num)),
        Quran.get_next_ayah(Quran.get_real_ayah_num(num))
    ))


@dp.callback_query_handler(filters.Text(startswith='ayahFromPrivate_'), chat_type='private')
async def get_ayah_by_button_private(call: types.CallbackQuery):
    num = call.data.split('_')[-1]
    text = Quran.get_ayah_by_num(num)
    await call.message.answer(text, reply_markup=keyboard.get_keyboard(
        'ayahFromPrivate_',
        Quran.get_prev_ayah(Quran.get_real_ayah_num(num)),
        Quran.get_next_ayah(Quran.get_real_ayah_num(num))
    ))
    await call.answer()
