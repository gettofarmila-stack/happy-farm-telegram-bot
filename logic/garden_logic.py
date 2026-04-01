import logging
from database.engine import Session
from datetime import datetime, timedelta
from database.models import User, Garden, Seed, InventoryItem
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from logic.weather_logic import weather_manager
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def check_my_garden(uid):
    builder = InlineKeyboardBuilder()
    with Session() as session:
        user = session.execute(select(User).options(selectinload(User.garden).selectinload(Garden.current_seed).selectinload(Seed.item)).where(User.user_id == str(uid))).scalar_one_or_none()
        if user and user.garden:
            for plot in user.garden:
                finish_time = plot.start_time + timedelta(seconds=plot.current_seed.grow_time) / weather_manager.current.grow_multiplier
                now = datetime.now()
                remaining_time = (finish_time - now).total_seconds()
                if remaining_time <= 0:
                    builder.row(types.InlineKeyboardButton(text=f'{plot.current_seed.item.name_key}: ✅ МОЖНО СОБИРАТЬ!', callback_data=f'inline_collect'))
                else:
                    builder.row(types.InlineKeyboardButton(text=f"{plot.current_seed.item.name_key}: ⏳ {int(remaining_time)} сек. 💧 {round(plot.hydration, 2)}", callback_data='not_ready_seed'))
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
    
def new_garden(uid, seed_id):
    seed_id = int(seed_id)
    with Session() as session:
        user = session.execute(select(User).options(selectinload(User.inventory)).where(User.user_id == str(uid))).scalar_one_or_none()
        user_inventory = [item.item_id for item in user.inventory]
        if user.stats.energy > 1:
            seed = session.execute(select(Seed).where(Seed.seed_item_id == seed_id)).scalar_one_or_none()
            if len(user.garden) >= user.stats.level * 3:
                return(f'❌ *Слишком большой огород!* Максимум грядок: *{user.stats.level * 3}*')
            if seed and seed.seed_item_id in user_inventory:
                garden = Garden(owner_id=str(uid), seed_id=seed.id)
                session.add(garden)
                exisiting_item = next((i for i in user.inventory if i.item_id == seed_id), None)
                if exisiting_item:
                    if exisiting_item.count > 1:
                        exisiting_item.count -= 1
                    else:
                        session.delete(exisiting_item) 
                user.stats.energy -= 1            
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
                builder.row(types.InlineKeyboardButton(text=f'{seed.item.name_key}', callback_data=f'plant_{seed.item.id}'))
                counter += 1
        if counter == 1:
            return None
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