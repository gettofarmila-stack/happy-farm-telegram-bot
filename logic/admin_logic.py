import logging
import asyncio
from database.engine import Session
from database.models import Item, Product, Buyer, Seed, Player
from sqlalchemy import select, update, func




def create_item(name_item, description):
    with Session() as session:
        item = session.execute(select(Item).where(Item.name_key == name_item)).scalar_one_or_none()
        if item:
            logging.warning(f'Предмет {item.name_key} уже существует под айди {item.id}!')
        else:
            n_item = Item(name_key=name_item, description=description)
            session.add(n_item)
            session.commit()
            logging.info(f'Предмет {n_item.name_key} создан под айди {n_item.id}')

def add_seed(seed, result, grow):
    with Session() as session:
        seed = Seed(seed_item_id=seed, result_item_id=result, grow_time=grow)
        session.add(seed)
        session.commit()

def add_product(new_id, new_price, new_cat):
    with Session() as session:
        new_product = Product(item_id=new_id, price=new_price, category=new_cat)
        session.add(new_product)
        session.commit()
        logging.info('Успешно создан новый товар')

def add_buyer(item_id, min, max):
    with Session() as session:
        new_buys = Buyer(item_id=item_id, min_price=min, max_price=max)
        session.add(new_buys)
        session.commit()

async def restore_all_energy_cycle(sleep_time):
    while True:
        await asyncio.sleep(sleep_time)
        try:
            with Session() as session:
                session.execute(update(Player).where(Player.energy < Player.max_energy).values(energy=func.least(Player.energy + 5, Player.max_energy)))
                session.commit()
                logging.info('Энергия всех юзнеров восстановлена!')
        except Exception as eror:
            logging.error(f'Ошибка при восстановлении энергии: {eror}')