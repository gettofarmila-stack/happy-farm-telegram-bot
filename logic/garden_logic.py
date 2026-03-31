import logging
import time
from database.engine import Session
from datetime import datetime, timedelta
from database.models import User, Garden, Seed, InventoryItem
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from logic.weather_logic import weather_manager

def check_my_garden(uid):
    with Session() as session:
        user = session.execute(select(User).options(selectinload(User.garden).selectinload(Garden.current_seed).selectinload(Seed.item)).where(User.user_id == str(uid))).scalar_one_or_none()
        if user and user.garden:
            res = '🌱 Твои грядки:\n'
            for plot in user.garden:
                finish_time = plot.start_time + timedelta(seconds=plot.current_seed.grow_time) / weather_manager.current.grow_multiplier
                now = datetime.now()
                remaining_time = (finish_time - now).total_seconds()
                if remaining_time <= 0:
                    res += f'- {plot.current_seed.item.name_key}: ✅ МОЖНО СОБИРАТЬ! /collect\n'
                else:
                    res += f"- {plot.current_seed.item.name_key}: ⏳ Будет готово через {int(remaining_time)} сек. текущая влажность {round(plot.hydration, 2)}\n"
            return res
        return 'У тебя пока пусто.'


def collect_garden(uid):
    with Session() as session:
        user = session.execute(select(User).options(selectinload(User.garden).selectinload(Garden.current_seed),selectinload(User.inventory)).where(User.user_id == str(uid))).scalar_one_or_none()

        if not user or not user.garden:
            return 'У тебя пока пусто на грядках!'

        res = '🚜 Отчет по сбору:\n'
        anything_collected = False
        now = datetime.now()
        plots_to_remove = []
        if user.stats.energy < 5: # 5 это я по 5 энергии отнимаю за каждое такое действие
            return('У тебя недостаточно энергии!')
        user.stats.energy -= 5
        for plot in user.garden:
            if plot.hydration == 0:
                return('Полей свой огород!')
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
                res += f"✅ {plot.current_seed.item.name_key} собран!\n"
                anything_collected = True

        if anything_collected:
            for p in plots_to_remove:
                session.delete(p)
            session.commit()
            return res
        return "Ничего еще не созрело!"
    
def new_garden(uid, seed_id):
    seed_id = int(seed_id)
    with Session() as session:
        user = session.execute(select(User).options(selectinload(User.inventory)).where(User.user_id == str(uid))).scalar_one_or_none()
        user_inventory = [item.item_id for item in user.inventory]
        if user.stats.energy > 1: # 1 энергию отнимаю за посадку растения
            seed = session.execute(select(Seed).where(Seed.seed_item_id == seed_id)).scalar_one_or_none()
            if len(user.garden) >= user.stats.level * 3:
                return(f'У тебя слишком большой огород! Ты не можешь создавать больше {user.stats.level * 3} грядок.')
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
                return(f'Вы успешно посадили растение! Все ваши растения можно смотреть в /check')
            else:
                logging.info('Не удалось посадить растение')
                return(f'У вас нет семян! Купить их можно в /seed_shop')
        else:
            return('Недостаточно энергии!')
def garden(uid):
    with Session() as session:
        user = session.execute(select(User).options(selectinload(User.inventory)).where(User.user_id == str(uid))).scalar_one_or_none()
        seed_list = session.execute(select(Seed).options(selectinload(Seed.item)))._raw_row_iterator()
        user_inventory = [item.item_id for item in user.inventory]
        res = 'Вы можете вырастить:\n'
        counter = 1
        for seed in seed_list:
            if seed.seed_item_id in user_inventory:
                res += f'{counter}. {seed.item.name_key}, чтобы посадить: /plant_{seed.item.id}\n'
                counter += 1
        return(res)
    
def watering(uid):
    try:
        with Session() as session:
            user = session.execute(select(User).options(selectinload(User.stats)).where(User.user_id == str(uid))).scalar_one_or_none()
            if user.stats.energy < 10:
                return('Недостаточно энергии!')
            session.execute(update(Garden).where(Garden.owner_id == str(uid)).values(hydration = func.least(Garden.hydration + 0.25, 1.0)))
            session.commit()
            return(f'Вы успешно полили ваш огород! Влажность увеличена на 0.25')
    except Exception as error:
        logging.info(f'{uid} не смог полить огород! {error}')
        return('Не удалось полить огород! Проверьте, возможно вам не нужно его поливать!')