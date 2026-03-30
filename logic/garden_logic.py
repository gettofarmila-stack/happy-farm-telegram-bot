import logging
import time
from database.engine import Session
from datetime import datetime, timedelta
from database.models import User, Garden, Seed, InventoryItem
from sqlalchemy import select
from sqlalchemy.orm import selectinload

def add_seed(seed, result, grow):
    with Session() as session:
        seed = Seed(seed_item_id=seed, result_item_id=result, grow_time=grow)
        session.add(seed)
        session.commit()

def check_my_garden(uid):
    with Session() as session:
        user = session.execute(select(User).options(selectinload(User.garden).selectinload(Garden.current_seed).selectinload(Seed.item)).where(User.user_id == str(uid))).scalar_one_or_none()
        if user and user.garden:
            res = '🌱 Твои грядки:\n'
            for plot in user.garden:
                finish_time = plot.start_time + timedelta(seconds=plot.current_seed.grow_time)
                now = datetime.now()
                remaining_time = (finish_time - now).total_seconds()
                if remaining_time <= 0:
                    res += f'- {plot.current_seed.item.name_key}: ✅ МОЖНО СОБИРАТЬ! /collect\n'
                else:
                    res += f"- {plot.current_seed.item.name_key}: ⏳ Будет готово через {int(remaining_time)} сек.\n"
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

        for plot in user.garden:
            finish_time = plot.start_time + timedelta(seconds=plot.current_seed.grow_time)
            
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
        if user:
            seed = session.execute(select(Seed).where(Seed.seed_item_id == seed_id)).scalar_one_or_none()
            if seed and seed.seed_item_id in user_inventory:
                garden = Garden(owner_id=str(uid), seed_id=seed.id)
                session.add(garden)
                exisiting_item = next((i for i in user.inventory if i.item_id == seed_id), None)
                if exisiting_item:
                    if exisiting_item.count > 1:
                        exisiting_item.count -= 1
                    else:
                        session.delete(exisiting_item)             
                session.commit()
                logging.info('Игрок посадил растение')
                return(f'Вы успешно посадили растение! Все ваши растения можно смотреть в /check')
            else:
                logging.info('Не удалось посадить растение')
                return(f'У вас нет семян! Купить их можно в /seed_shop')

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