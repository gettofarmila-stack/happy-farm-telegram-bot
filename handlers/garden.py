import asyncio
import re
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters.command import Command
from aiogram.filters import CommandObject
from logic.garden_logic import check_my_garden, collect_garden, garden, new_garden
router = Router()


@router.message(Command('check'))
async def cmd_check_garden(message: types.Message):
    checked = await asyncio.to_thread(check_my_garden, message.from_user.id)
    await message.answer(checked)

@router.message(Command('collect'))
async def cmd_collect(message: types.Message):
    collected = await asyncio.to_thread(collect_garden, message.from_user.id)
    await message.answer(collected)

@router.message(Command('garden'))
async def cmd_garden(message: types.Message):
    my_garden = await asyncio.to_thread(garden, message.from_user.id)
    await message.answer(my_garden)

@router.message(Command(re.compile(r'plant_(\d+)')))
async def cmd_buy(message: types.Message, command: CommandObject):
    item_id = message.text.split('_')[1]
    planter = await asyncio.to_thread(new_garden, message.from_user.id, item_id)
    await message.answer(planter)