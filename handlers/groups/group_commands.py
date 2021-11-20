from loader import dp, scheduler
from aiogram import types, filters
from asyncio import get_event_loop
from keyboards.inline import keyboard
from datetime import datetime, timedelta
from utils.Quran_api import Quran_parser as Quran
from utils.db_api import database as db
from utils.spreadsheet_api import spreadsheet as sh


@dp.my_chat_member_handler(chat_type=('group', 'supergroup'))
async def new_chat_start(update: types.ChatMemberUpdated):
    chat_id = update.chat.id
    if update.new_chat_member.is_chat_member():
        # get_event_loop().run_until_complete(db.add_chat(chat_id))
        get_event_loop().run_in_executor(None, db.add_chat, chat_id)
        link = 'https://docs.google.com/spreadsheets/d/1A7Vy3UATSCjBKENvPPfOaeDbq5mmF7l640M-XysGbj0/edit?usp=sharing'
        hello = \
            "Ас-саляму алейкум! Я буду менеджить ваши ежедневные отчеты!" \
            "\nОтчеты принимаются с 15:00 до 00:00 по мск за текущий день. " \
            "А досылать их можно с 00:00 до 15:00 - они учтутся за прошедший день." \
            " Таблица с отчетами доступна по " \
            f"[ссылке]({link})." \
            " Вы в нее попадете с первым вашим отчетом." \
            "\n\nТакже я каждый день в 21:00 буду присылать подборку из трех случайно выбранных аятов." \
            " Чтобы вручную сгенерировать случайный аят, напишите /random." \
            " Чтобы получить конкретный аят, тегните меня @PowerMuslimBot " \
            "с сообщением номера суры и аята через пробел, " \
            "запятую или двоеточие. А если хотите почитать Коран самостоятельно, то жду вас в лс. Всем удачи!"
        await update.bot.send_message(chat_id, text=hello, parse_mode='Markdown')


@dp.message_handler(content_types=types.message.ContentType.ANY, hashtags=['отчетзадень', 'отчётзадень'], chat_type=('group', 'supergroup'))
async def motivation_words(message: types.Message):
    # UTC+3: 15 23
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    get_event_loop().run_in_executor(None, sh.record_report, db.get_worksheet(chat_id), user_name, user_id, chat_id)
    await message.reply(db.get_motivation(user_name))


@dp.message_handler(chat_type=('group', 'supergroup'), commands="random")
async def send_random_ayah_in_chat(message: types.Message):
    num = Quran.get_random_ayah()
    text = Quran.get_ayah_by_num(num)
    await message.answer(text, reply_markup=keyboard.get_keyboard(
        'ayahFromGroup_',
        Quran.get_prev_ayah(Quran.get_real_ayah_num(num)),
        Quran.get_next_ayah(Quran.get_real_ayah_num(num))
    ))


@dp.message_handler(filters.Text(startswith='@PowerMuslimBot'), chat_type=('group', 'supergroup'))
async def send_specific_ayah_in_chat(message: types.Message):
    num = message.text.replace('@PowerMuslimBot ', '')
    text = Quran.get_ayah_by_num(num)
    if text == 'Такого аята нет (':
        await message.answer(text)
        return
    await message.answer(text, reply_markup=keyboard.get_keyboard(
        'ayahFromGroup_',
        Quran.get_prev_ayah(Quran.get_real_ayah_num(num)),
        Quran.get_next_ayah(Quran.get_real_ayah_num(num))
    ))


@dp.callback_query_handler(filters.Text(startswith='ayahFromGroup_'), chat_type=('group', 'supergroup'))
async def get_ayah_by_button_groups(call: types.CallbackQuery):
    num = call.data.split('_')[-1]
    text = Quran.get_ayah_by_num(num)
    ans = await call.message.reply(text, reply_markup=keyboard.get_keyboard(
        'ayahFromGroup_',
        Quran.get_prev_ayah(Quran.get_real_ayah_num(num)),
        Quran.get_next_ayah(Quran.get_real_ayah_num(num))
    ))
    await call.answer()
    scheduler.add_job(ans.delete, "date", run_date=(datetime.now() + timedelta(minutes=3)))
