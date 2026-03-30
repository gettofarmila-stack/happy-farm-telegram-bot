import asyncio
from aiogram import types, Router
from aiogram.filters.command import Command
from logic.user_logic import registation, get_profile, lvl_up, inventory_check
router = Router()

@router.message(Command('start'))
async def cmd_start(message: types.Message):
    is_new = await asyncio.to_thread(registation, name=message.from_user.first_name,
                username=message.from_user.username, 
                user_id=message.from_user.id
    )
    if is_new:
        await message.answer('Вы успешно зарегестрировались!')
    else:
        await message.answer('Вы уже зарегестрированы')


@router.message(Command('profile'))
async def cmd_profile(message: types.Message):
    prof = await asyncio.to_thread(get_profile, uid=message.from_user.id)
    await message.answer(prof)

@router.message(Command('lvl_up'))
async def cmd_lvlup(message: types.Message):
    lvl = await asyncio.to_thread(lvl_up, message.from_user.id)
    await message.answer(lvl)

@router.message(Command('inventory'))
async def cmd_inv(message: types.Message):
    inventory = await asyncio.to_thread(inventory_check, message.from_user.id)
    await message.answer(inventory)

@router.message(Command('help'))
async def cmd_help(message: types.Message):
    await message.answer('''
🚜 Фермерство и грядки

    /garden - Посмотреть, что из семян в твоем инвентаре можно посадить прямо сейчас.
    /plant_[ID] - Посадить растение на грядку (вместо [ID] пишем номер предмета)
    /check - Проверить статус твоих грядок (сколько осталось расти или пора ли собирать).
    /collect - Собрать созревший урожай в инвентарь

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