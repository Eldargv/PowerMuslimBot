from loader import gc
from utils.db_api import database as db
from datetime import datetime, timezone, timedelta

sh = gc.open("Power Muslims Reports")


def create_dates(sheet_id):
    dates = []
    tz = timezone(timedelta(hours=+3.0))
    now = datetime.now(tz) + timedelta(days=-1)
    for _ in range(50):
        dates.append({
            'values': [
                {'userEnteredValue': {'stringValue': f'{now.day}.{now.month}.{now.year}'}}
            ]
        })
        now += timedelta(days=1)

    sh.batch_update({
        "requests": [
            {
                'updateCells': {
                    'rows': dates,
                    'fields': '*',
                    'range': {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                        "endRowIndex": 52,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1
                    }
                }
            }
        ]
    })


def create_worksheet(chat_name):
    sheet_id = sh.add_worksheet(title=f'{chat_name}', rows=1000, cols=100).id
    create_dates(sheet_id)
    sh.get_worksheet_by_id(sheet_id).update_cell(1, 1, 'Дата')
    return sheet_id


def create_checkboxes(col, sheet_id):
    sh.batch_update({
        "requests": [
            {
                'repeatCell': {
                    'cell': {'dataValidation': {'condition': {'type': 'BOOLEAN'}}},
                    'range': {'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 50,
                              'startColumnIndex': col - 1,
                              'endColumnIndex': col},
                    'fields': 'dataValidation'
                }
            }
        ]
    })


def record_report(worksheet_id, user_name, user_id, chat_id):
    worksheet = sh.get_worksheet_by_id(worksheet_id)
    col = db.get_users_column(user_id, chat_id)
    if col == -1:
        col = len(worksheet.row_values(1)) + 1
        db.add_users_column(user_id, chat_id, col)
        worksheet.update_cell(1, col, user_name)
        create_checkboxes(col, worksheet.id)
    tz = timezone(timedelta(hours=+3.0))
    date = datetime.now(tz)
    # Принимаем вчерашний отчет
    if datetime.now(tz).hour <= 14:
        date += timedelta(days=-1)
    row = worksheet.find(f'{date.day}.{date.month}.{date.year}').row
    worksheet.update_cell(row, col, True)
