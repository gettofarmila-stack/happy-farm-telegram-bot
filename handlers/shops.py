import asyncio
import re
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters.command import Command
from aiogram.filters import CommandObject
from logic.shop_logic import seed_shop, buy, sell_item, buyer, store
from keyboards.shop_menu import shop_menu_kb
router = Router()

@router.message(F.text == 'Магазины')
async def kb_shops(message: types.Message):
    await message.answer('Выберите магазин', reply_markup=shop_menu_kb())

@router.message(Command('seed_shop'))
@router.message(F.text == 'Магазин Семян')
async def cmd_seed_shop(message: types.Message):
    shop = await asyncio.to_thread(seed_shop)
    await message.answer('Добро пожаловать в магазин семян, выбирайте любой товар', reply_markup=shop)

@router.message(Command(re.compile(r'buy_(\d+)')))
async def cmd_buy(message: types.Message, command: CommandObject):
    item_id = message.text.split('_')[1]
    item_buy = await asyncio.to_thread(buy, message.from_user.id, item_id)
    await message.answer(item_buy)

@router.callback_query(F.data.startswith('buy_'))
async def inline_buy(callback: types.CallbackQuery):
    item_id = callback.data.split('_')[1]
    buye = await asyncio.to_thread(buy, callback.from_user.id, item_id)
    shop = await asyncio.to_thread(seed_shop)
    await callback.answer(buye)
    await callback.message.edit_text(buye, reply_markup=shop)

@router.callback_query(F.data.startswith('sell_'))
async def inline_buy(callback: types.CallbackQuery):
    item_id = callback.data.split('_')[1]
    sell = await asyncio.to_thread(sell_item, callback.from_user.id, item_id)
    buye = await asyncio.to_thread(buyer)
    await callback.answer(sell)
    await callback.message.edit_text(sell, reply_markup=buye)

@router.message(Command('buyer'))
@router.message(F.text == 'Скупщик')
async def cmd_buyer(message: types.Message):
    buys = await asyncio.to_thread(buyer)
    await message.answer('Добро пожаловать на рынок, цены меняются каждые 15 минут, цены могут быть как выше цены закупки, так и ниже. Будьте внимательны!\nЧтобы продать товар, нажмите на него: ', reply_markup=buys)

@router.message(Command('shop'))
@router.message(F.text == 'Магазин бустов')
async def cmd_shop(message: types.Message):
    shop = await asyncio.to_thread(store)
    await message.answer(shop)