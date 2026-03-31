import asyncio
import re
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters.command import Command
from aiogram.filters import CommandObject
from logic.shop_logic import seed_shop, buy, sell_all, buyer, store
router = Router()


@router.message(Command('seed_shop'))
async def cmd_seed_shop(message: types.Message):
    shop = await asyncio.to_thread(seed_shop)
    await message.answer(shop)

@router.message(Command(re.compile(r'buy_(\d+)')))
async def cmd_buy(message: types.Message, command: CommandObject):
    item_id = message.text.split('_')[1]
    item_buy = await asyncio.to_thread(buy, message.from_user.id, item_id)
    await message.answer(item_buy)

@router.message(Command('sell_all'))
async def cmd_sell_all(message: types.Message):
    sell = await asyncio.to_thread(sell_all, message.from_user.id)
    await message.answer(sell)

@router.message(Command('buyer'))
async def cmd_buyer(message: types.Message):
    buys = await asyncio.to_thread(buyer)
    await message.answer(buys)

@router.message(Command('shop'))
async def cmd_shop(message: types.Message):
    shop = await asyncio.to_thread(store)
    await message.answer(shop)