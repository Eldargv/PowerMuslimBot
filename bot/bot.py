import json
import logging
import random
import re
import asyncio
import aioschedule
import psycopg2

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
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
Quran = json
motivation = ["Молодец", "Отлично", "Шикарный день", "Принято", "МАШОЛЛО"]
stickers = [
    'CAACAgIAAxkBAAEDIAdhcaOCtoVYU-LuZ73VCJsFY-eMyQACeBQAAhDEYEsdr5puuyESPCEE',
    'CAACAgIAAxkBAAEDIA9hcaQdKET0Z9gbNU0TrbPJ7E2vfgACKREAAmosWEtNPXH3WL3P7CEE'
]
sticker_demotivation = [
    'CAACAgIAAxkBAAEDIBFhcaTD0FFMFre074ZesVLQERuSEQACmw8AAsjPUEvYEF3ycvz7vyEE',
    'CAACAgIAAxkBAAEDIAthcaPOKzORs6eyNBpjEIHkH0RFLgACKREAAo4bYEsDJz2fSmNFNiEE'
]


class NotDigit(Exception):
    pass


class IncorrectSurah(Exception):
    pass


class IncorrectAyah(Exception):
    pass

class InCorrectInput(Exception):
    pass

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


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer(
        "Ас-саляму алейкум! Напиши /random, чтобы прочитать случайный аят, или отправь номер суры и аята!")


@dp.message_handler(commands="random")
async def get_random_verse(message: types.Message):
    num = random.randint(1, 114)
    rnum, rtext = random.choice(list(Quran[str(num)].items()))
    await message.answer(correct(rnum + rtext))


@dp.message_handler(chat_type=types.ChatType.PRIVATE)
async def get_specific_verse(message: types.Message):
    surah_ayah = re.split(', | |:|,', message.text)
    msg = ""
    try:
        if len(surah_ayah) != 2:
            raise InCorrectInput
        surah, ayah = surah_ayah
        if not surah.isdigit() or not ayah.isdigit():
            raise NotDigit
        print("nums got", surah, ayah)
        if 0 < int(surah) < 115:
            verses = Quran[surah].items()
            print("trying get ayah")
            for n, t in verses:
                nums = list(map(int, re.split('[-:,]', n)))
                if nums[1] <= int(ayah) <= nums[-1]:
                    print("Find!")
                    msg = n + t
                    break
            if len(msg) == 0:
                raise IncorrectAyah
        else:
            raise IncorrectSurah
    except NotDigit:
        msg = "Вы ввели не число"
    except IncorrectSurah:
        msg = "Неверный номер суры"
    except IncorrectAyah:
        msg = "Неверный номер аята"
    except InCorrectInput:
        msg = "Неправильный формат. Вы можете ввести номер суры и аята через пробел, запятую и двоеточие"
    except Exception as ex:
        print("Something goes wrong!!!")
        print(ex)
    await message.answer(correct(msg))


@dp.message_handler(filters.Text(startswith='@PowerMuslimBot'))
async def get_specific_verse(message: types.Message):
    ftext = message.text.replace('@PowerMuslimBot ', '')
    print(ftext)
    surah_ayah = re.split(', | |:|,', ftext)
    msg = ""
    try:
        if len(surah_ayah) != 2:
            raise InCorrectInput
        surah, ayah = surah_ayah
        if not surah.isdigit() or not ayah.isdigit():
            raise NotDigit
        print("nums got", surah, ayah)
        if 0 < int(surah) < 115:
            verses = Quran[surah].items()
            print("trying get ayah")
            for n, t in verses:
                nums = list(map(int, re.split('[-:,]', n)))
                if nums[1] <= int(ayah) <= nums[-1]:
                    print("Find!")
                    msg = n + t
                    break
            if len(msg) == 0:
                raise IncorrectAyah
        else:
            raise IncorrectSurah
    except NotDigit:
        msg = "Вы ввели не число"
    except IncorrectSurah:
        msg = "Неверный номер суры"
    except IncorrectAyah:
        msg = "Неверный номер аята"
    except InCorrectInput:
        msg = "Неправильный формат. Вы можете ввести номер суры и аята через пробел, запятую и двоеточие"
    except Exception as ex:
        print("Something goes wrong!!!")
        print(ex)
    await message.answer(correct(msg))


@dp.message_handler(commands="register", chat_type='group')
async def register(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    chat_id = message.chat.id
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO Users (user_id, user_name, chat_id, reports) VALUES ('{user_id}', '{user_name}', {chat_id}, false) ON CONFLICT DO NOTHING")
    cursor.execute(f"INSERT INTO Chats VALUES ({chat_id}) ON CONFLICT DO NOTHING")
    cursor.close()
    await message.answer(f"Игрок №{user_id} зарегистрирован!")


@dp.message_handler(hashtags='отчетзадень')
async def motivation_words(message: types.Message):
    # UTC+3: 15 23
    if 12 <= datetime.now().hour <= 20:
        cursor = conn.cursor()
        user_id = message.from_user.id
        cursor.execute(f"UPDATE Users SET reports = true WHERE user_id = '{user_id}'")
        cursor.close()
        if random.randint(0, 1) == 0:
            await message.reply(random.choice(motivation) + ', ' + message.from_user.first_name + '!')
        else:
            await message.reply_sticker(random.choice(stickers))


@dp.my_chat_member_handler(chat_type='group')
async def chat_member_handler(update: types.ChatMemberUpdated):
    print("New chat update")
    chat_id = update.chat.id
    print(chat_id)
    stat = update.new_chat_member.is_chat_member()
    if (stat):
        cursor = conn.cursor()
        cursor.execute(f'INSERT INTO Chats VALUES ({chat_id}) ON CONFLICT DO NOTHING')
        cursor.close()
        await update.bot.send_message(chat_id,
                                                "Всем ас-саляму алейкум! Отныне я незаконно забираю власть в руки и буду менеджить ваши отчеты! "
                                                "\nОтчеты принимаются с 15:00 до 23:00 по мск. В 22:00 я тегну всех, кто не сдал отчеты к этому времени."
                                                " Чтобы зарегистрироваться, отправьте \\register."
                                                "\n\nТакже я каждый день в 21:00 буду присылать подборку из трех случайно выбранных аятов."
                                                " Чтобы вручную сгенерировать случайный аят, напишите \\random."
                                                " Чтобы получить конкретный аят, тегните меня @PowerMuslimBot с сообщением номера суры и аята через пробел, "
                                                "запятую или двоеточие. Всем удачи!"
                                                )
    else:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM Chats WHERE chat_id = {chat_id} ON CONFLICT DO NOTHING")
        cursor.execute(f"DELETE FROM Users WHERE chat_id = {chat_id} ON CONFLICT DO NOTHING")
        cursor.close()


async def time_send():
    print("trying to send message")
    cursor = conn.cursor()
    cursor.execute('SELECT chat_id FROM Chats')
    chat_list = [int(chat_id[0]) for chat_id in cursor.fetchall()]
    cursor.close()
    for id in chat_list:
        await bot.send_message(id, "Cегодняшняя подборка:")
        for i in range(3):
            num = random.randint(1, 114)
            rnum, rtext = random.choice(list(Quran[str(num)].items()))
            await bot.send_message(id, correct(rnum + rtext))


async def morning_motivation():
    print("morining motivation activated")
    cursor = conn.cursor()
    cursor.execute('SELECT chat_id FROM Chats')
    chat_list = [int(chat_id[0]) for chat_id in cursor.fetchall()]
    cursor.close()
    for id in chat_list:
        await bot.send_message(id, "Ну что, ребята, топим педаль газа в пол! Идем к божественным подаркам в новом дне!")


async def reports_checker():
    cursor = conn.cursor()
    # Забираем из таблицы все id чатов-групп
    cursor.execute('SELECT chat_id FROM Chats')
    # Строим массив
    chat_list = [int(chat_id[0]) for chat_id in cursor.fetchall()]
    # Забираем из второй таблицы юзеров
    cursor.execute('SELECT user_id, user_name, chat_id FROM Users WHERE reports = false')
    # Кладем в массив
    users = cursor.fetchall()
    cursor.close()
    # Начинаме собирать сообщения с индексами юзеров
    messages = {}
    # Строго задаем словарь
    for chat_id in chat_list:
        messages[chat_id] = ""
    # Собираем сообщения с id юзеров
    for user_id, user_name, chat_id in users:
        messages[int(chat_id)] += f"[{user_name}](tg://user?id={user_id}), "
    # Собираем для каждого чата сообщение с теми, кто не прислал отчет
    for chat_id, message in messages.items():
        if len(message) == 0:
            await bot.send_message(int(chat_id), "Молодцы, ребята! Сегодня все прислали отчеты!")
        else:
            await bot.send_message(int(chat_id), "Не понял, а где отчеты от " + message[:-2] + " ...", parse_mode='Markdown')
            await bot.send_sticker(int(chat_id), random.choice(sticker_demotivation))


async def reports_cleaner():
    cursor = conn.cursor()
    cursor.execute('SELECT chat_id FROM Chats')
    chats = cursor.fetchall()
    for chat_id in chats:
        cursor.execute(f'UPDATE Users SET reports = false WHERE chat_id = {chat_id[0]}')
    cursor.close()


async def scheduler():
    print("Activating scheduler")
    # Время на сервере UTC+0
    # Московское +3
    # Следовательно, из желаемого времени нужно вычесть 3
    aioschedule.every().day.at("18:00").do(time_send)
    aioschedule.every().day.at("3:00").do(morning_motivation)
    aioschedule.every().day.at("19:00").do(reports_checker)
    aioschedule.every().day.at("20:01").do(reports_cleaner)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(dp):
    logging.warning(
        'Starting connection. ')
    asyncio.create_task(scheduler())
    await bot.set_webhook(WEBHOOK_URL,drop_pending_updates=True)


async def on_shutdown(dp):
    logging.warning('Bye! Shutting down webhook connection')


def main():
    with open("Quran.json", encoding='utf-8') as file:
        global Quran
        Quran = json.load(file)

    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
