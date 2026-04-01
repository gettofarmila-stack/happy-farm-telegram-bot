from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

# тут все главные менюшки

def main_menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text='Профиль'), types.KeyboardButton(text='Огород'))
    builder.row(types.KeyboardButton(text='Магазины'), types.KeyboardButton(text='Погода'))
    builder.row(types.KeyboardButton(text='Топ'))
    return builder.as_markup(resize_keyboard=True)

def menu_top_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text='Топ по балансу'), types.KeyboardButton(text='Топ по уровню'))
    builder.row(types.KeyboardButton(text='Главное меню'))
    return builder.as_markup(resize_keyboard=True)

def profile_menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text='Статистика'), types.KeyboardButton(text='Инвентарь'))
    builder.row(types.KeyboardButton(text='Повысить уровень'), types.KeyboardButton(text='Реферальная система'))
    builder.row(types.KeyboardButton(text='Главное меню'))
    return builder.as_markup(resize_keyboard=True)