import json
import logging
import random
import re
import asyncio
import aioschedule
import psycopg2

from aiogram import Bot, Dispatcher, types
from aiogram.utils import markdown
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.executor import start_webhook
from aiogram.dispatcher import filters
from bot.config import (BOT_TOKEN, HEROKU_APP_NAME,
                          WEBHOOK_URL, WEBHOOK_PATH,
                          WEBAPP_HOST, WEBAPP_PORT, DATABASE_URL)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
conn.autocommit = True
Quran = json
Chats = [-691197382, 916354662]
motivation = ["Молодец", "Отлично", "Шикарный день"]


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


@dp.message_handler()
async def register(message: types.Message):
    await message.answer(f'[inline mention of a user](tg://user?id={message.from_user.id})', parse_mode=markdown)
    # bot.send_message()
    # if '@' in message.text:
    #     user = message.text.replace('/register @', '')
    #     chat_id = message.chat.id
    #     cursor = conn.cursor()
    #     cursor.execute(f"INSERT INTO Users VALUES ('{user}', {chat_id}, false)")
    #     cursor.close()
    #     await message.answer(f"Игрок @{user} зарегистрирован!")
    # else:
    #     await message.answer("Неверное имя пользователя")


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


@dp.message_handler(hashtags='отчетзадень')
async def motivation_words(message: types.Message):
    cursor = conn.cursor()
    user = message.from_user.username
    cursor.execute(f"UPDATE Users SET reports = true WHERE user_handle = '{user}'")
    cursor.close()
    await message.reply(random.choice(motivation) + ', ' + message.from_user.first_name + '!')


@dp.my_chat_member_handler(chat_type='group')
async def chat_member_handler(update: types.ChatMemberUpdated):
    print("New chat update")
    chat_id = update.chat.id
    print(chat_id)
    stat = update.new_chat_member.is_chat_member()
    if (stat):
        # cursor = conn.cursor()
        # print("Trying to insert in table")
        # cursor.execute(f'INSERT INTO Users VALUES (234, {chat_id})')
        # cursor.close()
        await update.bot.send_message(chat_id, "Всем ас-саляму алейкум!")


async def time_send():
    print("trying to send message")
    for id in Chats:
        await bot.send_message(id, "Cегодняшняя подборка:")
        for i in range(3):
            num = random.randint(1, 114)
            rnum, rtext = random.choice(list(Quran[str(num)].items()))
            await bot.send_message(id, correct(rnum + rtext))


async def morning_motivation():
    print("morining motivation activated")
    for id in Chats:
        await bot.send_message(id, "Ну что, ребята, топим педаль газа в пол! Идем к божественным подаркам в новом дне!")


async def scheduler():
    print("Activating scheduler")
    # Время на сервере UTC+0
    # Московское +3
    # Следовательно, из желаемого времени нужно вычесть 3
    aioschedule.every().day.at("18:00").do(time_send)
    aioschedule.every().day.at("3:00").do(morning_motivation)
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
