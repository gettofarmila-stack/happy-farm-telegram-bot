from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types


def shop_menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text='Магазин Семян'), types.KeyboardButton(text='Магазин бустов'))
    builder.row(types.KeyboardButton(text='Скупщик'))
    builder.row(types.KeyboardButton(text='Главное меню'))
    return builder.as_markup(resize_keyboard=True)