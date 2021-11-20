from loader import Quran, ayah_nums
from random import choice
import re


def form_message(num, text):
    # формирует сообщение из номера аята и текста
    return num + text


def get_random_ayah():
    # возвращает текст сообщения со случайным аятом
    return choice(list(ayah_nums.keys()))


def form_ayah_num(surah_ayah):
    # представляет данные номера суры и аята в правильной форме
    return surah_ayah[0] + ':' + surah_ayah[1]


def is_correct_num(surah_ayah):
    # проверяет номера суры и аята на корректность
    return len(surah_ayah) >= 2 and form_ayah_num(surah_ayah) in ayah_nums


def get_real_ayah_num(msg):
    # возвращает номер суры и аята из сообщения в нужной форме
    surah_ayah = re.split(', |:| |-', msg)
    if not is_correct_num(surah_ayah):
        return ""
    return ayah_nums[form_ayah_num(surah_ayah)]


def get_ayah_by_num(msg):
    # возвращает текст сообщения с конкретным аятом
    num = get_real_ayah_num(msg)
    if len(num) == 0:
        return "Такого аята нет ("
    return form_message(num, Quran[num])


def get_prev_ayah(num):
    # возвращает номер предыдущего за num аят
    # если данный номер гарантированно правильный
    ayah_list = list(Quran.keys())
    curr_index = ayah_list.index(num)
    if curr_index == 0:
        return ""
    return ayah_list[curr_index - 1]


def get_next_ayah(num):
    # возвращает номер следующего за num аят
    # если данный номер гарантированно правильный
    ayah_list = list(Quran.keys())
    curr_index = ayah_list.index(num)
    if num == ayah_list[-1]:
        return ""
    return ayah_list[curr_index + 1]
