import json
import logging
import random
import re
import asyncio
import aioschedule
import psycopg2
import gspread

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types.message import ContentType
from aiogram.types.bot_command import BotCommand
from aiogram.types.bot_command_scope import BotCommandScopeAllGroupChats
from aiogram.utils.executor import start_webhook
from aiogram.dispatcher import filters
from bot.config import (BOT_TOKEN, HEROKU_APP_NAME,
                          WEBHOOK_URL, WEBHOOK_PATH,
                          WEBAPP_HOST, WEBAPP_PORT, DATABASE_URL)
from datetime import datetime


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
conn.autocommit = True

gc = gspread.service_account(filename="token.json")
sh = gc.open("Power Muslims Reports")

Quran = {}
ayah_nums = {}

keyboard = types.InlineKeyboardMarkup()

def create_checkboxes(col, sheet_id):
    requests = {"requests": [
        {
            'repeatCell': {
                'cell': {'dataValidation': {'condition': {'type': 'BOOLEAN'}}},
                'range': {'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 50,
                            'startColumnIndex': col - 1,
                            'endColumnIndex': col},
                'fields': 'dataValidation'
            }
        }
    ]}
    sh.batch_update(requests)


def update_report_sync(worksheet_id, user_name, user_id, chat_id, flag = 0):
    worksheet = sh.get_worksheet(worksheet_id)
    cell = worksheet.find(str(user_id))
    col = 0
    if cell == None:
        print(worksheet.row_values(100))
        user_cnt = len(worksheet.row_values(100)) + 1
        worksheet.update_cell(100, user_cnt, user_id)
        worksheet.update_cell(101, user_cnt, chat_id)
        worksheet.update_cell(1, user_cnt, user_name)
        create_checkboxes(user_cnt, worksheet.id)
        col = user_cnt
    else:
        col = cell.col
    date = datetime.today().date()
    row = worksheet.find(f'{date.day - flag}.{date.month}.{date.year}').row
    worksheet.update_cell(row, col, True)


async def update_report(worksheet_id, user_name, user_id, chat_id, flag = 0):
    await asyncio.get_event_loop().run_in_executor(None, update_report_sync, worksheet_id, user_name, user_id, chat_id, flag)
    print("OK, I updated cells")


def create_keyboard(prev="", next=""):
    buttons = []
    if len(prev) > 0:
        buttons.append(types.InlineKeyboardButton(text=prev, callback_data=('ayah_' + prev)))
    if len(next) > 0:
        buttons.append(types.InlineKeyboardButton(text=next, callback_data=('ayah_' + next)))
    global keyboard
    if len(buttons) > 0:
        keyboard = types.InlineKeyboardMarkup(row_width=len(buttons))
        keyboard.add(*buttons)
        print("Keyboard created")


@dp.callback_query_handler(filters.Text(startswith='ayah_'))
async def get_adjacent_ayahs(call: types.CallbackQuery):
    # ayah_2:6, 7
    ayah = call.data.split('_')[-1].split(':')
    msg = get_ayah_by_num([ayah[0], re.split(', |-|,', ayah[-1])[-1]])
    print(ayah[0] + ' ' + re.split(', |-|,', ayah[-1])[-1])
    if not msg[1]:
        if call.message.chat.id < 0:
            await call.message.reply(msg[0])
        else:
            await call.message.answer(msg[0])
    else:
        if call.message.chat.id < 0:
            await call.message.reply(msg[0], reply_markup=keyboard)
        else:
            await call.message.answer(msg[0], reply_markup=keyboard)
    await call.answer()


def correct(msg):
    explanation_index = msg.find('***')
    if (explanation_index > -1):
        msg = msg[:explanation_index]
    ending_index = msg.find('Милостью Всевышнего тафсир')
    if (ending_index > -1):
        msg = msg[:ending_index]
    if len(msg) > 4096:
        msg = msg[:4097]
        for i in range(4095, 0, -1):
            if msg[i] == '.':
                msg = msg[:i + 1]
                break
    return msg


def get_ayah_by_num(surah_ayah):
    if len(surah_ayah) != 2:
        return "Неправильный формат. Вы можете ввести номер суры и аята через пробел, запятую и двоеточие", False
    surah, ayah = surah_ayah
    if not surah.isdigit() or not ayah.isdigit():
        return "Вы ввели не число", False
    print("nums got", surah, ayah)
    if 0 < int(surah) < 115:
        print("trying get ayah")
        if 0 < int(ayah) < len(ayah_nums[surah]) + 1:
            next = ""
            prev = ""
            now = ayah_nums[surah][ayah]
            print(f"AAAAAAAA {now}")
            prev_num = int(re.split('[:|, |-]', now)[1])
            next_num = int(re.split('[:|, |-]', now)[-1])
            if prev_num > 1:
                prev = ayah_nums[surah][str(prev_num - 1)]
                print("prev ayah got")
            if next_num < len(ayah_nums[surah]):
                next = ayah_nums[surah][str(next_num + 1)]
                print("next ayah got")
            create_keyboard(prev, next)
            return (correct(now + Quran[now]), not (next == "" and prev == ""))
        return "Неверный номер аята", False
    else:
        return "Неверный номер суры", False


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer(
        "Ас-саляму алейкум! Напиши /random, чтобы прочитать случайный аят, или отправь номер суры и аята!")


@dp.message_handler(commands="random")
async def get_random_verse(message: types.Message):
    rnum = random.choice(list(Quran))
    surah_ayah_parse = re.split('[:| ,|-|]', rnum)
    msg = get_ayah_by_num([surah_ayah_parse[0], surah_ayah_parse[-1]])
    if msg[1]:
        await message.answer(msg[0], reply_markup=keyboard)
    else:
        await message.answer(msg[0])


@dp.message_handler(chat_type=types.ChatType.PRIVATE)
async def get_specific_verse(message: types.Message):
    surah_ayah = re.split(', | |:|,', message.text)
    msg = get_ayah_by_num(surah_ayah)
    if msg[1]:
        print("try to attack keyboard")
        await message.answer(msg[0], reply_markup=keyboard)
    else:
        await message.answer(msg[0])


@dp.my_chat_member_handler(chat_type=('group', 'supergroup'))
async def chat_member_handler(update: types.ChatMemberUpdated):
    print("New chat update")
    chat_id = update.chat.id
    print(chat_id)
    stat = update.new_chat_member.is_chat_member()
    if (stat):
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Chats')
        cnt = len(cursor.fetchall())
        cursor.execute(f'INSERT INTO Chats (chat_id, worksheet) VALUES ({chat_id}, {cnt}) ON CONFLICT DO NOTHING')
        cursor.close()
        await update.bot.send_message(chat_id, text=
                                                "Ас-саляму алейкум! Я буду менеджить ваши ежедневные отчеты!"
                                                "\nОтчеты принимаются с 15:00 до 00:00 по мск за текущий день. А досылать их можно с 00:00 до 15:00 - они учтутся за прошедший день."
                                                " Таблица с отчетами доступна по [ссылке](https://docs.google.com/spreadsheets/d/1A7Vy3UATSCjBKENvPPfOaeDbq5mmF7l640M-XysGbj0/edit?usp=sharing)."
                                                " Вы в нее попадете с первым вашим отчетом."
                                                "\n\nТакже я каждый день в 21:00 буду присылать подборку из трех случайно выбранных аятов."
                                                " Чтобы вручную сгенерировать случайный аят, напишите /random."
                                                " Чтобы получить конкретный аят, тегните меня @PowerMuslimBot с сообщением номера суры и аята через пробел, "
                                                "запятую или двоеточие. А если хотите почитать Коран самостоятельно, то жду вас в лс. Всем удачи!",
                                            parse_mode='Markdown')


@dp.message_handler(filters.Text(startswith='@PowerMuslimBot'))
async def get_specific_verse(message: types.Message):
    ftext = message.text.replace('@PowerMuslimBot ', '')
    surah_ayah = re.split(', | |:|,', ftext)
    msg = get_ayah_by_num(surah_ayah)
    if msg[1]:
        print("try to attack keyboard")
        await message.answer(msg[0], reply_markup=keyboard)
    else:
        await message.answer(msg[0])


@dp.message_handler(content_types=ContentType.ANY, hashtags='отчетзадень')
async def motivation_words(message: types.Message):
    # UTC+3: 15 23
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    cursor = conn.cursor()

    cursor.execute(f'SELECT worksheet FROM CHATS WHERE chat_id = {chat_id}')
    worksheet_id = cursor.fetchone()[0]

    cursor.execute('select text from motivation_text')
    moti = [str(a[0]) for a in cursor.fetchall()]

    cursor.close()

    await message.reply(random.choice(moti).replace('*имя*', user_name))
    flag = 0
    if 21 <= datetime.now().hour or datetime.now().hour <= 12:
        flag = 1
    await update_report(worksheet_id, user_name, user_id, chat_id, flag)


@dp.message_handler(content_types=ContentType.ANY, chat_type=('group', 'supergroup'))
async def funny_message_to_reply(message: types.Message):
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.id:
        pack = await bot.get_sticker_set('Power_Muslims')
        await message.reply_sticker(random.choice(pack.stickers).file_id)


async def evening_ayah_set():
    print("trying to send message")
    cursor = conn.cursor()
    cursor.execute('SELECT chat_id FROM Chats')
    chat_list = [int(chat_id[0]) for chat_id in cursor.fetchall()]
    cursor.close()
    for id in chat_list:
        await bot.send_message(id, "Cегодняшняя подборка:")
        for i in range(3):
            rnum = random.choice(list(Quran))
            surah_ayah_parse = re.split('[:| ,|-|]', rnum)
            msg = get_ayah_by_num([surah_ayah_parse[0], surah_ayah_parse[-1]])
            if msg[1]:
                await bot.send_message(chat_id=id, text=msg[0], reply_markup=keyboard)
            else:
                await bot.send_message(chat_id=id, text=msg[0])


async def morning_motivation():
    print("morining motivation activated")
    cursor = conn.cursor()
    cursor.execute('SELECT chat_id FROM Chats')
    chat_list = [int(chat_id[0]) for chat_id in cursor.fetchall()]
    cursor.close()
    for id in chat_list:
        await bot.send_message(id, "Ну что, ребята, топим педаль газа в пол! Идем к божественным подаркам в новом дне!")


async def scheduler():
    print("Activating scheduler")
    # Время на сервере UTC+0
    # Московское +3
    # Следовательно, из желаемого времени нужно вычесть 3
    aioschedule.every().day.at("18:00").do(evening_ayah_set)
    aioschedule.every().day.at("3:00").do(morning_motivation)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def set_default_commands():
    print("Setting commands")
    default_commands = [
        BotCommand(command="random", description="Случайный аят"),
    ]
    await dp.bot.set_my_commands(default_commands)

    group_commands = [
        BotCommand(command="random", description="Случайный аят"),
    ]
    await dp.bot.set_my_commands(group_commands, BotCommandScopeAllGroupChats())


async def on_startup(dp):
    logging.warning(
        'Starting connection. '
    )
    
    with open("Quran.json", encoding='utf-8') as file:
        global Quran
        Quran = json.load(file)

    with open("ayah_nums.json", encoding='utf-8') as file:
        global ayah_nums
        ayah_nums = json.load(file)
    
    asyncio.create_task(scheduler())

    await set_default_commands()

    await bot.set_webhook(WEBHOOK_URL,drop_pending_updates=True)


async def on_shutdown(dp):
    logging.warning('Bye! Shutting down webhook connection')


def main():
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
