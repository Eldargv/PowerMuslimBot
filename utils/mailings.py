from loader import scheduler, dp
from utils.db_api import database as db
from utils.Quran_api import Quran_parser as Quran
from keyboards.inline import keyboard


@scheduler.scheduled_job('cron', hour='18')
async def send_evening_ayah_set():
    chats = db.get_chats()
    for chat_id in chats:
        await dp.bot.send_message(chat_id, "Cегодняшняя подборка:")
        for _ in range(3):
            num = Quran.get_random_ayah()
            text = Quran.get_ayah_by_num(num)
            await dp.bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard.get_keyboard(
                'ayahFromGroup_',
                Quran.get_prev_ayah(Quran.get_real_ayah_num(num)),
                Quran.get_next_ayah(Quran.get_real_ayah_num(num))
            ))


@scheduler.scheduled_job('cron', hour='3')
async def morning_motivation():
    chats = db.get_chats()
    for chat_id in chats:
        await dp.bot.send_message(chat_id,
                                  "Ну что, ребята, топим педаль газа в пол! Идем к божественным подаркам в новом дне!")
