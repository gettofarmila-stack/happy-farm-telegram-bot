import asyncio
import re
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters.command import Command
from aiogram.filters import CommandObject
from logic.garden_logic import check_my_garden, collect_garden, garden, new_garden, watering
from keyboards.garden_menu import garden_menu_kb
router = Router()

@router.message(F.text == 'Огород')
async def kd_garden(message: types.Message):
    await message.answer('Выберите действие', reply_markup=garden_menu_kb())

@router.message(Command('check'))
@router.message(F.text == 'Проверка')
async def cmd_check_garden(message: types.Message):
    checked = await asyncio.to_thread(check_my_garden, message.from_user.id)
    if checked:
        await message.answer('Ваш огород, чтобы собрать, нажмите на готовый посев', reply_markup=checked)
    else:
        await message.answer('У тебя пусто!')

@router.callback_query(F.data == "inline_collect")
async def process_collecting(callback: types.CallbackQuery):
    collected = await asyncio.to_thread(collect_garden, callback.from_user.id)
    await callback.answer('Успешно')
    await callback.message.edit_text(f"Урожай собран! {collected}")

@router.message(Command('garden'))
@router.message(F.text == 'Посадка')
async def cmd_garden(message: types.Message):
    my_garden = await asyncio.to_thread(garden, message.from_user.id)
    if my_garden:
        await message.answer('В вашем кармане оказались:', reply_markup=my_garden)
    else:
        await message.answer('Вам нечего сажать! Купите семена в магазине')

@router.callback_query(F.data == 'not_ready_seed')
async def inline_notready(callback: types.CallbackQuery):
    await callback.answer('Посев ещё не готов!')
    await callback.message.edit_text('Ещё не выросло!', reply_markup=check_my_garden)

@router.message(Command(re.compile(r'plant_(\d+)')))
async def cmd_buy(message: types.Message, command: CommandObject):
    item_id = message.text.split('_')[1]
    planter = await asyncio.to_thread(new_garden, message.from_user.id, item_id)
    await message.answer(planter)

@router.callback_query(F.data.startswith('plant_'))
async def inline_plant(callback: types.CallbackQuery):
    item_id = callback.data.split('_')[1]
    planter = await asyncio.to_thread(new_garden,callback.from_user.id , item_id)
    await callback.answer(f"Результат: {planter}")
    await callback.message.edit_text(f"🌿 Действие выполнено: {planter}", reply_markup=garden)
    
@router.message(Command('water'))
@router.message(F.text == 'Полив')
async def cmd_water(message: types.Message):
    water = await asyncio.to_thread(watering, message.from_user.id)
    await message.answer(water)