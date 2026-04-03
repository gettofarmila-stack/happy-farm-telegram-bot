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

def buy(uid, product_id, amount):
    with Session() as session:
        user = session.execute(select(User).options(selectinload(User.stats)).where(User.user_id == str(uid))).scalar_one_or_none()
        product = session.execute(select(Product).options(selectinload(Product.item)).where(Product.id == product_id)).scalar_one_or_none()
        amount = int(amount)
        if product:
            if user.stats.balance >= product.price * amount:
                add_item_to_user_obj(user, product.item_id, amount=amount)
                user.stats.balance -= product.price * amount
                session.commit()
                return(f'✅ *Покупка!* {product.item.name_key}\n💰 Баланс: *{user.stats.balance}$*')
            else:
                deficit = product.price * amount - user.stats.balance
                return(f'❌ *Недостаточно денег!* Не хватает: *{deficit}$*')
        else:
            return('❌ *Продукт не найден!*')
        
def seed_shop():
    builder = InlineKeyboardBuilder()
    with Session() as session:
        products = session.execute(select(Product).options(selectinload(Product.item)))._raw_row_iterator()
        for product in products:
            builder.row(types.InlineKeyboardButton(text=f'{product.item.name_key}: {product.price}💰', callback_data=f'pid_1_{product.id}'))
        return builder.as_markup()
    
def second_seed_shop_page(uid, product_id, amount: int):
    builder = InlineKeyboardBuilder()
    with Session() as session:
        user = session.execute(select(User).options(selectinload(User.stats)).where(User.user_id == str(uid))).scalar_one_or_none()
        product = session.execute(select(Product).options(selectinload(Product.item)).where(Product.id == int(product_id))).scalar_one_or_none()
        balance = user.stats.balance
        max_items = int(balance / product.price)
        amount = int(amount)
        builder.row(types.InlineKeyboardButton(text=f'{amount}шт.', callback_data='ignore'))
        builder.row(types.InlineKeyboardButton(text='-1', callback_data=f'pid_{amount - 1}_{product_id}'), types.InlineKeyboardButton(text='MAX', callback_data=f'pid_{max_items}_{product_id}'), types.InlineKeyboardButton(text='+1', callback_data=f'pid_{amount + 1}_{product_id}'))
        builder.row(types.InlineKeyboardButton(text='✅ Купить', callback_data=f'buy_{product.id}_{amount}'))
        builder.row(types.InlineKeyboardButton(text='❌ Назад', callback_data='back_seed'))
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
            return '❌ *Нет такого предмета* в инвентаре!'
        total_price = product.now_price * inv_item.count
        exp_gain = (product.now_price * inv_item.count) * 0.1
        res = f'✅ *Продано!* {inv_item.item.name_key}\n'
        res += f'💰 Получено: *{total_price}$*\n'
        user.stats.balance += total_price
        user.stats.exp += exp_gain
        session.delete(inv_item)
        session.commit()
        res += f'💾 Баланс: *{user.stats.balance}$*\n⭐ Опыт: +*{exp_gain:.1f}*'
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
        res = '🥝 *МАГАЗИН БУСТОВ* 🦕\n\n'
        count = 0
        for product in products:
            count += 1
            res += f'{count}. *{product.item.name_key}*\n   📝 {product.item.description}\n   💰 Цена: *{product.price}$*\n\n'
        return(res)