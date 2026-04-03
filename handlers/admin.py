import asyncio
import logging
from aiogram import types, Router
from aiogram.filters.command import Command
from logic.admin_logic import create_item, add_seed, add_product, add_buyer, broadcast
from config import ADMINS
router = Router()


@router.message(Command('new_item'))
async def cmd_newitem(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer('🚫 Ошибка! Вы не админ')
    raw_args = message.text.replace('/new_item', '').strip()
    if ',' not in raw_args:
        return await message.answer('🚫 Ошибка! Формат: `/new_item Название, Описание` (через запяту)')
    parts = raw_args.split(',', maxsplit=1)
    item_name = parts[0].strip()
    item_desc = parts[1].strip()
    if not item_name or not item_desc:
        return await message.answer('🚫 Ошибка! Имя или описание не могут быть пустыми!')
    success = await asyncio.to_thread(create_item, item_name, item_desc)
    if success:
        logging.info(f'Предмет {item_name} создан!')
        return await message.answer(f'✅ Предмет сохранён: {item_name}, под айди: {success}')
    
@router.message(Command('new_seed'))
async def cmd_newseed(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer('🚫 Ошибка! Вы не админ')
    raw_args = message.text.replace('/new_seed', '').strip()
    if ',' not in raw_args:
        return await message.answer('🚫 Ошибка! Формат: `/new_seed Айди семени, Айди результата, Время роста`')
    parts = raw_args.split(',', maxsplit=2)
    seed_id = parts[0].strip()
    res_id = parts[1].strip()
    grow_time = parts[2].strip()
    if not seed_id or not res_id or not grow_time:
        return await message.answer('🚫 Ошибка! Айди семени, айди результата или время роста не могут быть пустыми!')
    success = await asyncio.to_thread(add_seed, seed_id, res_id, grow_time)
    if success:
        logging.info(f'Семя создано!')
        return await message.answer(f'✅ Семя сохранено!')
    
@router.message(Command('add_product'))
async def cmd_add_product(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer('🚫 Ошибка! Вы не админ')   
    raw_args = message.text.replace('/add_product', '').strip()
    parts = [p.strip() for p in raw_args.split(',')]    
    if len(parts) < 3:
        return await message.answer('🚫 Ошибка! Нужно: `/add_product ID, Цена, Категория`')
    new_id, new_price, new_cat = parts[0], parts[1], parts[2]
    if not new_id.isdigit() or not new_price.isdigit():
        return await message.answer('🚫 Ошибка! ID и Цена должны быть числами!')
    result = await asyncio.to_thread(add_product, int(new_id), int(new_price), new_cat)
    if result:
        return await message.answer(f'⚠️ {result}')
    await message.answer(f'✅ Товар сохранён! ID: *{new_id}*, Цена: *{new_price}*, Категория: *{new_cat}*')

@router.message(Command('add_buyer'))
async def cmd_add_buyer(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer('🚫 Ошибка! Вы не админ')
    raw_args = message.text.replace('/add_buyer', '').strip()
    parts = [p.strip() for p in raw_args.split(',')]
    if len(parts) < 3:
        return await message.answer('🚫 Ошибка! Нужно: `/add_buyer ID, Мин_Цена, Макс_Цена`')
    item_id, min_p, max_p = parts[0], parts[1], parts[2]
    if not all(x.isdigit() for x in [item_id, min_p, max_p]):
        return await message.answer('🚫 Ошибка! Все аргументы должны быть числами!')
    result = await asyncio.to_thread(add_buyer, int(item_id), int(min_p), int(max_p))
    if result:
        return await message.answer(f'⚠️ {result}')
    await message.answer(f'✅ Скупщик настроен! ID: *{item_id}*, Диапазон: *{min_p}-{max_p}*')

@router.message(Command('broadcast'))
async def cmd_broadcast(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer('Вы не админ')
    args = message.text.replace('/broadcast', '')
    await broadcast(message.bot, args)
    await message.answer('Успешно разослал!')