import logging
import asyncio
from database.engine import Session
from database.models import Item, Product, Buyer, Seed, Player, Garden
from sqlalchemy import select, update, func
from logic.weather_logic import get_random_weather, weather_manager

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
        find_seed = session.execute(select(Seed).where(Seed.seed_item_id == int(seed))).scalar_one_or_none()
        if find_seed:
            return('Такое семя уже существует! Функция add_seed')
        n_seed = Seed(seed_item_id=seed, result_item_id=result, grow_time=grow)
        session.add(n_seed)
        session.commit()

def add_product(new_id, new_price, new_cat):
    with Session() as session:
        find_product = session.execute(select(Product).where(Product.item_id == int(new_id))).scalar_one_or_none()
        if find_product:
            return('Такой продукт уже существует! Функция add_product')
        new_product = Product(item_id=new_id, price=new_price, category=new_cat)
        session.add(new_product)
        session.commit()
        logging.info('Успешно создан новый товар')

def add_buyer(item_id, min, max):
    with Session() as session:
        find_buy = session.execute(select(Buyer).where(Buyer.item_id == int(item_id))).scalar_one_or_none()
        if find_buy:
            return('Этот товар уже скупается! Ошибка add_buyer функция')
        new_buys = Buyer(item_id=item_id, min_price=min, max_price=max)
        session.add(new_buys)
        session.commit()

async def restore_all_energy_cycle(sleep_time):
    while True:
        await asyncio.sleep(sleep_time)
        try:
            with Session() as session:
                session.execute(update(Player).where(Player.energy < Player.max_energy).values(energy=func.least(Player.energy + 5 + weather_manager.current.energy_bonus, Player.max_energy)))
                session.commit()
                logging.info('Энергия всех юзнеров восстановлена!')
        except Exception as eror:
            logging.error(f'Ошибка при восстановлении энергии: {eror}')

async def hydration_min(sleep_time):
    while True:
        await asyncio.sleep(sleep_time)
        try:
            with Session() as session:
                session.execute(update(Garden).values(hydration = func.greatest(func.least(Garden.hydration + weather_manager.current.hydration_boost, 1.0), 0.0)))
                session.commit()
                logging.info(f'Влажность всех огородов упала на {weather_manager.current.hydration_boost}!')
        except Exception as error:
            logging.error(f'Не удалось уменьшить влажность: {error}')

async def random_weather_choise(sleep_time):
    while True:
        await asyncio.sleep(sleep_time)
        try:
            n_weather = get_random_weather()
            weather_manager.current = n_weather
            logging.info(f'Установлена погода {n_weather.name}, множитель {n_weather.grow_multiplier}')
        except Exception as error:
            logging.error(f'Ошибка при смене погоды: {error}')
