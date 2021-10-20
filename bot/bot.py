import json
import logging
import random
import re
import asyncio
import aioschedule

from aiogram import Bot, Dispatcher, types, filters
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.executor import start_webhook
from bot.config import (BOT_TOKEN, HEROKU_APP_NAME,
                          WEBHOOK_URL, WEBHOOK_PATH,
                          WEBAPP_HOST, WEBAPP_PORT)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
Quran = json


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


@dp.message_handler()
async def reply(message: types.Message):
    print(message)
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


async def time_send():
    print("trying to send message")
    await bot.send_message(916354662, "Cегодняшняя подборка:")
    for i in range(3):
        num = random.randint(1, 114)
        rnum, rtext = random.choice(list(Quran[str(num)].items()))
        await bot.send_message(916354662, correct(rnum + rtext))        


async def scheduler():
    print("Activating scheduler")
    aioschedule.every().day.at("11:50").do(time_send())
    while True:
        print("While True starts")
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
