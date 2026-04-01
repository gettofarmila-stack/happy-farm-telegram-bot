from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

def garden_menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text='Проверка'), types.KeyboardButton(text='Посадка'))
    builder.row(types.KeyboardButton(text='Полив'))
    builder.row(types.KeyboardButton(text='Главное меню'))
    return builder.as_markup(resize_keyboard=True)