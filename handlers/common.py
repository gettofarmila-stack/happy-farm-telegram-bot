import asyncio
import logging
from aiogram import types, Router, F
from aiogram.filters.command import Command
from logic.user_logic import registation, get_profile, lvl_up, inventory_check, bal_top, lvl_top
from logic.weather_logic import weather_manager
from keyboards.main_menu import main_menu_kb, profile_menu_kb, menu_top_kb
router = Router()

@router.message(Command('start'))
@router.message(F.text == 'Главное меню')
async def cmd_start(message: types.Message):
    is_new = await asyncio.to_thread(registation, name=message.from_user.first_name, username=message.from_user.username, user_id=message.from_user.id)
    if is_new:
        logging.info('Новый пользователь!')
    else:
        logging.info('Не удалось зарегать юзера, он уже зареган')
    await message.answer('Добро пожаловать на веселую ферму!\nВыбери раздел:', reply_markup=main_menu_kb())

@router.message(F.text == 'Профиль')
async def kb_profile(message: types.Message):
    await message.answer('Выбери, что хочешь посмотреть?', reply_markup=profile_menu_kb())

@router.message(Command('profile'))
@router.message(F.text == 'Статистика')
async def cmd_profile(message: types.Message):
    prof = await asyncio.to_thread(get_profile, uid=message.from_user.id)
    await message.answer(prof)

@router.message(Command('lvl_up'))
@router.message(F.text == 'Повысить уровень')
async def cmd_lvlup(message: types.Message):
    lvl = await asyncio.to_thread(lvl_up, message.from_user.id)
    await message.answer(lvl)

@router.message(Command('inventory'))
@router.message(F.text == 'Инвентарь')
async def cmd_inv(message: types.Message):
    inventory = await asyncio.to_thread(inventory_check, message.from_user.id)
    if inventory:
        await message.answer("Твой инвентарь:", reply_markup=inventory)
    else:
        await message.answer("В инвентаре пока пусто... 🎒")

@router.message(Command('weather'))
@router.message(F.text == 'Погода')
async def cmd_weather(message: types.Message):
    await message.answer(f'Текущая погода: {weather_manager.current.name}\n - множитель огорода x{weather_manager.current.grow_multiplier}\n - бонус к восстановлению энергии: {weather_manager.current.energy_bonus}')

@router.message(F.text == 'Топ')
async def kb_tops(message: types.Message):
    await message.answer('Выберите топ', reply_markup=menu_top_kb())

@router.message(Command('baltop'))
@router.message(F.text == 'Топ по балансу')
async def cmd_baltop(message: types.Message):
    top = await asyncio.to_thread(bal_top)
    await message.answer(top)

@router.message(Command('lvltop'))
@router.message(F.text == 'Топ по уровню')
async def cmd_lvltop(message: types.Message):
    top = await asyncio.to_thread(lvl_top)
    await message.answer(top)

@router.message(Command('help'))
async def cmd_help(message: types.Message):
    await message.answer('''
🚜 Фермерство и грядки

    /garden - Посмотреть, что из семян в твоем инвентаре можно посадить прямо сейчас.
    /plant_[ID] - Посадить растение на грядку (вместо [ID] пишем номер предмета)
    /check - Проверить статус твоих грядок (сколько осталось расти или пора ли собирать).
    /collect - Собрать созревший урожай в инвентарь
    /weather - узнать погоду
    /water - полить огород

💰 Магазин и Экономика

    /seed_shop - Зайти в магазин семян и посмотреть актуальный ассортимент и цены.
    /buy_[ID] - Купить товар в магазине по его айди
    /sell_all - Продать всё на рынке по текущему курсу                         
    /buyer - Посмотреть актуальные цены на рынке

👤 Профиль и Инвентарь

    /profile - Твоя карточка игрока: баланс.
    /inventory - Посмотреть свой инвентарь.
    /lvl_up - Повысить уровень.
                         ''')