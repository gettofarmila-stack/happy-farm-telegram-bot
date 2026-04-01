import logging
import time
import random
from database.engine import Session
from database.models import User
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database.models import Product, User, Buyer, InventoryItem
from logic.user_logic import add_item_to_user_obj
from bot import start_time
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def buy(uid, product_id):
    with Session() as session:
        user = session.execute(select(User).options(selectinload(User.stats)).where(User.user_id == str(uid))).scalar_one_or_none()
        product = session.execute(select(Product).options(selectinload(Product.item)).where(Product.id == product_id)).scalar_one_or_none()
        if product:
            if user.stats.balance >= product.price:
                add_item_to_user_obj(user, product.item_id, amount=1)
                user.stats.balance -= product.price
                session.commit()
                return(f'Успешная покупка {product.item.name_key}, текущий баланс {user.stats.balance}')
            else:
                return(f'Недостаточно средств, вам не хватает {product.price - user.stats.balance}')
        else:
            return('Такого продукта не существует!')
        
def seed_shop():
    builder = InlineKeyboardBuilder()
    with Session() as session:
        products = session.execute(select(Product).options(selectinload(Product.item)))._raw_row_iterator()
        for product in products:
            builder.row(types.InlineKeyboardButton(text=f'{product.item.name_key}: {product.price}💰', callback_data=f'buy_{product.id}'))
        return builder.as_markup()
    
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

def sell_item(uid, item_id):
    with Session() as session:
        user = session.execute(select(User).options(selectinload(User.stats)).where(User.user_id == str(uid))).scalar_one_or_none()
        inv_item = session.execute(select(InventoryItem).options(selectinload(InventoryItem.item)).where(InventoryItem.owner_id == str(uid)).where(InventoryItem.item_id == item_id)).scalar_one_or_none() 
        update_buyer_price()
        product = session.execute(select(Buyer).options(selectinload(Buyer.item)).where(Buyer.item_id == int(item_id))).scalar_one_or_none()
        if not inv_item:
            return 'У тебя в инвентаре этого нет!'
        res = f'Успешно продано на сумму {product.now_price * inv_item.count}\n'
        user.stats.balance += (product.now_price * inv_item.count)
        user.stats.exp += (product.now_price * inv_item.count) * 0.1
        session.delete(inv_item)
        session.commit()
        res += f'Текущий баланс: {user.stats.balance}, опыта добавлено {(product.now_price * inv_item.count) * 0.1}'
        return(res)


def buyer():
    builder = InlineKeyboardBuilder()
    update_buyer_price()
    global start_time
    with Session() as session:
        buyer_list = session.execute(select(Buyer).options(selectinload(Buyer.item))).scalars().all()
        for i in buyer_list:
            builder.row(types.InlineKeyboardButton(text=f'{i.item.name_key}, Цена: {i.now_price}💰\n', callback_data=f'sell_{i.item_id}'))
        return builder.as_markup()

def store():
    with Session() as session:
        products = session.execute(select(Product).options(selectinload(Product.item)).where(Product.category == 'bonus')).scalars().all()
        res = 'Добро пожаловать в магазин удобрений, и полезных вещей.\nВ наличии:\n'
        count = 0
        for product in products:
            count += 1
            res += f'{count}. {product.item.name_key}, {product.item.description} - {product.price}'
        return(res)