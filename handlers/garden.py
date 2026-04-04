import asyncio
import re
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters.command import Command
from aiogram.filters import CommandObject
from logic.garden_logic import check_my_garden, collect_garden, garden, new_garden, watering, garden_second
from keyboards.garden_menu import garden_menu_kb
router = Router()

@router.message(F.text == 'Огород')
async def kd_garden(message: types.Message):
    await message.answer('🌱 Выберите действие', reply_markup=garden_menu_kb())

@router.message(Command('check'))
@router.message(F.text == 'Проверка')
async def cmd_check_garden(message: types.Message):
    checked = await asyncio.to_thread(check_my_garden, message.from_user.id)
    if checked:
        await message.answer('🌿 Ваш огород, чтобы собрать, нажмите на готовый посев', reply_markup=checked)
    else:
        await message.answer('🌻 Огород партте!')

@router.callback_query(F.data.startswith('gardenpage_'))
async def inline_check_garden(callback: types.CallbackQuery):
    page = callback.data.split('_')[1]
    checked = await asyncio.to_thread(check_my_garden, callback.from_user.id, int(page))
    await callback.message.edit_reply_markup(reply_markup = checked)
    await callback.answer()

@router.callback_query(F.data == "inline_collect")
async def process_collecting(callback: types.CallbackQuery):
    collected = await asyncio.to_thread(collect_garden, callback.from_user.id)
    await callback.answer('✅ Урожай собран!')
    await callback.message.edit_text(f"🤏 Отчет по сбору:\n{collected}", parse_mode='Markdown')

@router.message(Command('garden'))
@router.message(F.text == 'Посадка')
async def cmd_garden(message: types.Message):
    my_garden = await asyncio.to_thread(garden, message.from_user.id)
    if my_garden:
        await message.answer('🌾 В вашем кармане эти семена:', reply_markup=my_garden)
    else:
        await message.answer('🌚 Нечего сажать! Купи семена в магазине 🌵')

@router.callback_query(F.data == 'back_seeding')
async def inline_garden(callback: types.CallbackQuery):
    my_garden = await asyncio.to_thread(garden, callback.from_user.id)
    if my_garden:
        await callback.message.edit_text('🌾 В вашем кармане эти семена:', reply_markup=my_garden)
    else:
        await callback.message.edit_text('🌚 Нечего сажать! Купи семена в магазине 🌵')

@router.callback_query(F.data == 'not_ready_seed')
async def inline_notready(callback: types.CallbackQuery):
    await callback.answer('🌚 Не готово ещё!')
    await callback.message.edit_text('🕒 Осталось ещё расти!', reply_markup=check_my_garden)

@router.message(Command(re.compile(r'plant_(\d+)')))
async def cmd_buy(message: types.Message, command: CommandObject):
    item_id = message.text.split('_')[1]
    planter = await asyncio.to_thread(new_garden, message.from_user.id, item_id)
    await message.answer(planter, parse_mode='Markdown')

@router.callback_query(F.data.startswith('plant_'))
async def inline_plant(callback: types.CallbackQuery):
    item_id = callback.data.split('_')[1]
    amount = callback.data.split('_')[2]
    planter = await asyncio.to_thread(new_garden, callback.from_user.id, item_id, amount)
    await callback.answer(f"Результат: {planter}")
    await callback.message.edit_text(f"🌿 Действие выполнено: {planter}", reply_markup=garden)

@router.callback_query(F.data.startswith('sid_'))
async def plant_menu_inline(callback: types.CallbackQuery):
    item_id = callback.data.split('_')[2]
    amount = callback.data.split('_')[1]
    plant_menu = await asyncio.to_thread(garden_second, callback.from_user.id, item_id, amount)
    await callback.message.edit_reply_markup(reply_markup=plant_menu)

@router.message(Command('water'))
@router.message(F.text == 'Полив')
async def cmd_water(message: types.Message):
    water = await asyncio.to_thread(watering, message.from_user.id)
    await message.answer(water, parse_mode='Markdown')