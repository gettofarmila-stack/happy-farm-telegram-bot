import logging
import time
import random
from database.engine import Session
from database.models import User
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database.models import Product, User, Buyer
from logic.user_logic import add_item_to_user_obj
from bot import start_time

def buy(uid, product_id):
    with Session() as session:
        user = session.execute(select(User).options(selectinload(User.stats)).where(User.user_id == str(uid))).scalar_one_or_none()
        product = session.execute(select(Product).options(selectinload(Product.item)).where(Product.id == product_id)).scalar_one_or_none()
        if product:
            if user.stats.balance > product.price:
                add_item_to_user_obj(user, product.item_id, amount=1)
                user.stats.balance -= product.price
                session.commit()
                return(f'Успешная покупка {product.item.name_key}, текущий баланс {user.stats.balance}')
            else:
                return(f'Недостаточно средств, вам не хватает {product.price - user.stats.balance}')
        else:
            return('Такого продукта не существует!')
        
def seed_shop():
    with Session() as session:
        products = session.execute(select(Product).options(selectinload(Product.item)))._raw_row_iterator()
        res = 'Сейчас в наличии:\n'
        counter = 1
        for product in products:
            res += f'{counter}. {product.item.name_key}: {product.price}💰, для покупки {product.item.name_key}, введите /buy_{product.id}\n'
            counter += 1
        return(res)
    
def update_buyer_price():
    global start_time
    elapsed_time = time.time() - start_time
    logging.info(f'{elapsed_time} прошло')
    if elapsed_time >= 900:
        start_time = time.time()
        with Session() as session:
            buy_list = session.execute(select(Buyer))._raw_row_iterator()
            for i in buy_list:
                i.now_price = random.randint(i.min_price, i.max_price)
            session.commit()

def sell_all(uid):
    with Session() as session:
        user = session.execute(
            select(User)
            .options(selectinload(User.inventory), selectinload(User.stats))
            .where(User.user_id == str(uid))
        ).scalar_one_or_none()
        
        if not user or not user.inventory:
            return "Твой инвентарь пуст, продавать нечего!"

        update_buyer_price()
        buys = session.execute(select(Buyer)).scalars().all()
        buyer_prices = {b.item_id: b.now_price for b in buys}

        total_profit = 0
        items_sold_count = 0
        items_to_remove = []
        for inv_item in user.inventory:
            if inv_item.item_id in buyer_prices:
                price_per_one = buyer_prices[inv_item.item_id]
                profit = price_per_one * inv_item.count
                
                total_profit += profit
                items_sold_count += inv_item.count
                
                items_to_remove.append(inv_item)

        if total_profit > 0:
            for item in items_to_remove:
                session.delete(item)
            
            user.stats.balance += total_profit
            user.stats.exp += (total_profit * 0.001)
            session.commit()
            logging.info(f'Юзер {uid} продал все ресурсы ({items_sold_count} шт.) и заработал {total_profit} монет! Опыта начислено {total_profit * 0.001}')
            return f"💰 Ты продал все ресурсы ({items_sold_count} шт.) и заработал {total_profit} монет! Опыта начислено {total_profit * 0.001}"
        
        return "У тебя нет ресурсов, которые сейчас принимает скупщик."

def buyer():
    update_buyer_price()
    global start_time
    with Session() as session:
        buyer_list = session.execute(select(Buyer).options(selectinload(Buyer.item))).scalars().all()
        res = f'Цены у скупщика меняются каждые 15 минут\nСейчас цены:\n'
        counter = 1
        for i in buyer_list:
            res += f'{counter}. {i.item.name_key}, Цена: {i.now_price}💰\n'
            counter += 1
        res += f'До смены цен осталось {round((900 - (time.time() - start_time)) / 60)} минут\nЧтобы продать всё, введите /sell_all'
        return res

def store():
    with Session() as session:
        products = session.execute(select(Product).options(selectinload(Product.item)).where(Product.category == 'bonus')).scalars().all()
        res = 'Добро пожаловать в магазин удобрений, и полезных вещей.\nВ наличии:\n'
        count = 0
        for product in products:
            count += 1
            res += f'{count}. {product.item.name_key}, {product.item.description} - {product.price}'
        return(res)