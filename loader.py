import psycopg2
import gspread

from aiogram import Bot, Dispatcher, types
from data import config
from json import load
from apscheduler.schedulers.asyncio import AsyncIOScheduler

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)

scheduler = AsyncIOScheduler()

conn = psycopg2.connect(config.DATABASE_URL, sslmode='require')
conn.autocommit = True

gc = gspread.service_account(filename="token.json")

with open("Quran.json", encoding='utf-8') as file:
    Quran = load(file)

with open("ayah_nums.json", encoding='utf-8') as file:
    ayah_nums = load(file)
