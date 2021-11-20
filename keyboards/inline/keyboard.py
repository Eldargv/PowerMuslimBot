from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_keyboard(data, prev_ayah, next_ayah):
    kb = InlineKeyboardMarkup()
    buttons = []
    if len(prev_ayah) > 0:
        buttons.append(InlineKeyboardButton(text=prev_ayah, callback_data=(data + prev_ayah)))
    if len(next_ayah) > 0:
        buttons.append(InlineKeyboardButton(text=next_ayah, callback_data=(data + next_ayah)))
    kb.add(*buttons)
    print("Keyboard created")
    return kb
