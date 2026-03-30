import asyncio
import logging
from aiogram import types, Router
from aiogram.filters.command import Command
from logic.admin_logic import create_item
from config import ADMINS
router = Router()


@router.message(Command('new_item'))
async def cmd_newitem(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer('Ошибка! Вы не админ')
    raw_args = message.text.replace('/new_item', '').strip()
    if ',' not in raw_args:
        return await message.answer('Ошибка! Нужно писать так: `/new_item Имя, Описание` (через запятую)')
    parts = raw_args.split(',', maxsplit=1)
    item_name = parts[0].strip()
    item_desc = parts[1].strip()
    if not item_name or not item_desc:
        return await message.answer('Имя или описание не могут быть пустыми!')
    success = await asyncio.to_thread(create_item, item_name, item_desc)
    if success:
        logging.info(f'Предмет {item_name} создан!')
        return await message.answer(f'✅ Успешно создан предмет: {item_name}')