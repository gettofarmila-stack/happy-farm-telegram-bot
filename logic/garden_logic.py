import logging
from database.engine import Session
from datetime import datetime, timedelta
from database.models import User, Garden, Seed, InventoryItem
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from logic.weather_logic import weather_manager
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def check_my_garden(uid, page: int = 0):
    builder = InlineKeyboardBuilder()
    page_size = 10
    with Session() as session:
        user = session.execute(
            select(User)
            .options(selectinload(User.garden).selectinload(Garden.current_seed).selectinload(Seed.item))
            .where(User.user_id == str(uid))
        ).scalar_one_or_none()
        if user and user.garden:
            start_idx = page * page_size
            end_idx = start_idx + page_size
            garden_slice = user.garden[start_idx:end_idx]
            for plot in garden_slice: 
                finish_time = plot.start_time + timedelta(seconds=plot.current_seed.grow_time) / weather_manager.current.grow_multiplier
                remaining_time = (finish_time - datetime.now()).total_seconds()
                if remaining_time <= 0:
                    builder.row(types.InlineKeyboardButton(
                        text=f'{plot.current_seed.item.name_key}: ✅', 
                        callback_data='inline_collect'
                    ))
                else:
                    text = f"{plot.current_seed.item.name_key}: ⏳{int(remaining_time)}с 💧{round(plot.hydration, 1)}"
                    builder.row(types.InlineKeyboardButton(
                        text=text, 
                        callback_data='not_ready_seed'
                    ))
            # Кнопки навигации
            nav_buttons = []
            if page > 0:
                nav_buttons.append(types.InlineKeyboardButton(text="⬅️", callback_data=f"gardenpage_{page-1}"))            
            if end_idx < len(user.garden):
                nav_buttons.append(types.InlineKeyboardButton(text="➡️", callback_data=f"gardenpage_{page+1}"))            
            if nav_buttons:
                builder.row(*nav_buttons)                
            return builder.as_markup()
        return None


def collect_garden(uid):
    with Session() as session:
        user = session.execute(select(User).options(selectinload(User.garden).selectinload(Garden.current_seed),selectinload(User.inventory)).where(User.user_id == str(uid))).scalar_one_or_none()

        if not user or not user.garden:
            return '🌱 Грядок нет, погоди момент!'

        res = '🚜 *ОТЧЕТ ПО СБОРУ УРОЖАЯ:*\n\n'
        anything_collected = False
        now = datetime.now()
        plots_to_remove = []
        if user.stats.energy < 5:
            return('⚡ *Недостаточно энергии! Нужно: 5*')
        user.stats.energy -= 5
        for plot in user.garden:
            if plot.hydration == 0:
                return('💧 *Полей свой огород! Влажность 0!*')
            finish_time = plot.start_time + timedelta(seconds=plot.current_seed.grow_time) / weather_manager.current.grow_multiplier
            
            if now >= finish_time:
                target_item_id = plot.current_seed.result_item_id
                existing_item = next((i for i in user.inventory if i.item_id == target_item_id), None)
                
                if existing_item:
                    existing_item.count += 1
                else:
                    new_inv_item = InventoryItem(item_id=target_item_id, count=1)
                    user.inventory.append(new_inv_item)
                
                plots_to_remove.append(plot)
                res += f"✅ *{plot.current_seed.item.name_key}* собран!\n"
                anything_collected = True

        if anything_collected:
            for p in plots_to_remove:
                session.delete(p)
            session.commit()
            return res
        return "❌ *Ничего еще не созрело!*"
    
def new_garden(uid, seed_id, amount):
    seed_id = int(seed_id)
    amount = int(amount)
    with Session() as session:
        user = session.execute(select(User).options(selectinload(User.inventory)).where(User.user_id == str(uid))).scalar_one_or_none()
        inventory = session.execute(select(InventoryItem).where(InventoryItem.item_id == seed_id, InventoryItem.owner_id == str(uid))).scalar_one_or_none()
        user_inventory = [item.item_id for item in user.inventory]
        if user.stats.energy > 1:
            seed = session.execute(select(Seed).where(Seed.seed_item_id == seed_id)).scalar_one_or_none()
            if len(user.garden) >= user.stats.level * 3:
                return(f'❌ *Слишком большой огород!* Максимум грядок: *{user.stats.level * 3}*')
            if seed and seed.seed_item_id in user_inventory and inventory.count >= amount:
                while amount >= 1:                    
                    garden = Garden(owner_id=str(uid), seed_id=seed.id)
                    session.add(garden)
                    amount -= 1
                    user.stats.energy -= 1 
                    exisiting_item = next((i for i in user.inventory if i.item_id == seed_id), None)
                    if exisiting_item:
                        if exisiting_item.count >= amount:
                            exisiting_item.count -= amount
                        else:
                            session.delete(exisiting_item)            
                session.commit()
                logging.info('Игрок посадил растение')
                return(f'🌱 *Успешно посажено!* Проверить статус: /check')
            else:
                logging.info('Не удалось посадить растение')
                return(f'❌ *Нет семян!* Купить в /seed_shop')
        else:
            return('⚡ *Недостаточно энергии!*')
        
def garden(uid):
    builder = InlineKeyboardBuilder()
    with Session() as session:
        user = session.execute(select(User).options(selectinload(User.inventory)).where(User.user_id == str(uid))).scalar_one_or_none()
        seed_list = session.execute(select(Seed).options(selectinload(Seed.item)))._raw_row_iterator()
        user_inventory = [item.item_id for item in user.inventory]
        counter = 1
        for seed in seed_list:
            if seed.seed_item_id in user_inventory:
                builder.row(types.InlineKeyboardButton(text=f'{seed.item.name_key}', callback_data=f'sid_1_{seed.item.id}'))
                counter += 1
        if counter == 1:
            return None
        return builder.as_markup()
    
def garden_second(uid, seed_item_id, amount):
    amount = int(amount)
    builder = InlineKeyboardBuilder()
    with Session() as session:
        item = session.execute(select(InventoryItem).where(InventoryItem.item_id == seed_item_id, InventoryItem.owner_id == str(uid))).scalar_one_or_none()
        max_items = item.count
        builder.row(types.InlineKeyboardButton(text=f'{amount}шт.', callback_data='pass'))
        builder.row(types.InlineKeyboardButton(text='-1', callback_data=f'sid_{amount - 1}_{seed_item_id}'), types.InlineKeyboardButton(text='MAX', callback_data=f'sid_{max_items}_{seed_item_id}'), types.InlineKeyboardButton(text='+1', callback_data=f'sid_{amount + 1}_{seed_item_id}'))
        builder.row(types.InlineKeyboardButton(text='Посадить', callback_data=f'plant_{seed_item_id}_{amount}'))
        builder.row(types.InlineKeyboardButton(text='Назад', callback_data='back_seeding'))
        return builder.as_markup()
    
def watering(uid):
    try:
        with Session() as session:
            user = session.execute(select(User).options(selectinload(User.stats)).where(User.user_id == str(uid))).scalar_one_or_none()
            if user.stats.energy < 10:
                return('⚡ *Недостаточно энергии! Нужно: 10*')
            session.execute(update(Garden).where(Garden.owner_id == str(uid)).values(hydration = func.least(Garden.hydration + 0.25, 1.0)))
            user.stats.energy -= 10
            session.commit()
            return(f'💧 *Полили огород!* Влажность +0.25 (⚡-10)')
    except Exception as error:
        logging.info(f'{uid} не смог полить огород! {error}')
        return('❌ *Ошибка!* Проверьте огород')