from loader import conn
from utils.spreadsheet_api.spreadsheet import create_worksheet
from random import choice as random_choice


def add_chat(chat_id):
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO Chats (chat_id, worksheet) VALUES ({chat_id}, {create_worksheet(chat_id)}) ON CONFLICT DO NOTHING')
    cursor.close()


def remove_chat(chat_id):
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM Chats WHERE chat_id = {chat_id}')
    conn.close()


def get_worksheet(chat_id):
    cursor = conn.cursor()
    cursor.execute(f'SELECT worksheet FROM CHATS WHERE chat_id = {chat_id}')
    worksheet_id = cursor.fetchone()[0]
    cursor.close()
    return worksheet_id


def get_users_column(user_id, chat_id):
    cursor = conn.cursor()
    cursor.execute(f'select col from users where user_id = {user_id} and chat_id = {chat_id}')
    res = -1
    finds = cursor.fetchone()
    if finds is not None:
        res = finds[0]
    cursor.close()
    return res


def add_users_column(user_id, chat_id, col):
    cursor = conn.cursor()
    cursor.execute(f'insert into users(user_id, chat_id, col) values ({user_id}, {chat_id}, {col})')
    cursor.close()


def get_motivation(user_name):
    cursor = conn.cursor()
    cursor.execute('select text from motivation_text')
    motivation_list = [str(a[0]) for a in cursor.fetchall()]
    cursor.close()
    return random_choice(motivation_list).replace('*имя*', user_name)
