import logging
from database.engine import Session
from database.models import User, Player, InventoryItem
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def is_register(uid):
    with Session() as session:
        user = session.execute(select(User).where(User.user_id == str(uid))).scalar_one_or_none()
        return user

def registation(name, username, user_id, referer_id):
    with Session() as session:
       
        user = session.execute(select(User).where(User.user_id == str(user_id))).scalar_one_or_none()
        
        if user:
            logging.warning(f'Юзер {user_id} уже есть в базе')
            return False
        else:
            new_user = User(name=name, username=username, user_id=user_id, referer_id=referer_id)
            new_stats = Player(balance=100, level=1, exp=0, max_energy=100, energy=100)
            new_user.stats = new_stats
            session.add(new_user)
            session.commit()
            logging.info(f'Юзер {user_id} успешно зарегистрирован!')
            return True
        
def get_profile(uid):
    with Session() as session:
        user = session.execute(select(User).where(User.user_id == str(uid))).scalar_one_or_none()
        if user:
            return(f'''
        👤 ПРОФИЛЬ
    👨 Имя: *{user.name}*
    📝 Юзернейм: @{user.username}
    🆔 Айди Телеграм: *{user.user_id}*
    💾 Номер в базе: *{user.id}*
    📅 Зарегистрирован: *{user.register_at.strftime("%d.%m.%Y")}*
    
    💰 Баланс: *{user.stats.balance}$*
    ⚡ Текущая энергия: *{user.stats.energy}/{user.stats.max_energy}*
    🏆 Уровень: *{user.stats.level}*
                ''')
        else:
            logging.warning('ПОЛЬЗОВАТЕЛЬ НЕ ЗАРЕГЕСТРИРОВАН')
            return('❌ Ошибка, каким-то образом вы не зарегестрированы')
def lvl_up(uid):
    with Session() as session:
        user = session.execute(select(User).where(User.user_id == str(uid))).scalar_one_or_none()
        if user:
            exp = user.stats.exp
            lvl = user.stats.level
            if exp >= lvl ** 2:
                user.stats.exp -= lvl ** 2
                user.stats.level += 1
                user.stats.max_energy += 20
                session.commit()
                return(f'🎉 Уровень повышен! Текущий уровень: *{user.stats.level}*, опыта осталось: *{user.stats.exp}* \n⚡ Максимальная энергия +20!')
            else:
                return(f'❌ Недостаточно опыта! Нужно: *{lvl ** 2}*, у вас есть: *{exp}*')
            
def add_to_inv(uid, item_id, amount=1):
    with Session() as session:
        user = session.execute(select(User).options(selectinload(User.inventory)).where(User.user_id == str(uid))).scalar_one_or_none()  
        if not user: return "❌ Юзер не найден"
        existing_item = next((i for i in user.inventory if i.item_id == item_id), None)
        if existing_item:
            existing_item.count += amount
            logging.info(f"Добавили {amount} шт. к имеющемуся предмету {item_id}")
        else:
            new_inv_entry = InventoryItem(item_id=item_id, count=amount)
            user.inventory.append(new_inv_entry)
            logging.info(f"Создали новую запись для предмета {item_id}")
        session.commit()
        return f"✅ Инвентарь обновлен! (+*{amount}*)"

def del_item_in_user_obj(session, user, item_id, amount=1):
    exisiting_item = next((i for i in user.inventory if i.item_id == item_id), None)
    if exisiting_item:
        if exisiting_item.count > amount:
            exisiting_item.count -= amount
        else:
            session.delete(exisiting_item)

def add_item_to_user_obj(user, item_id, amount=1):
    existing_item = next((i for i in user.inventory if i.item_id == item_id), None)

    if existing_item:
        existing_item.count += amount
    else:
        new_inv_entry = InventoryItem(item_id=item_id, count=amount)
        user.inventory.append(new_inv_entry)

def inventory_check(uid):
    builder = InlineKeyboardBuilder()
    with Session() as session:
        user = session.execute(select(User).options(selectinload(User.inventory).selectinload(InventoryItem.item)).where(User.user_id == str(uid))).scalar_one_or_none()
        if not user.inventory:
            return None
        else:
            for itemone in user.inventory:
                builder.row(types.InlineKeyboardButton(text=f'{itemone.item.name_key} - {itemone.count}шт.', callback_data=f'inv_item_{itemone.item.id}'))
            return builder.as_markup()
        
def bal_top():
    with Session() as session:
        players = session.execute(select(Player).options(selectinload(Player.user)).order_by(desc(Player.balance)).limit(10)).scalars().all()
        res = '💰 *ТОП 10 ПО БАЛАНСУ*\n\n'
        count = 0
        for p in players:
            count += 1
            medal = '🥇' if count == 1 else '🥈' if count == 2 else '🥉' if count == 3 else f'{count}️⃣'
            res += f'{medal} *{p.user.name}*: {p.balance}$ \n'
        return(res)
    
def lvl_top():
    with Session() as session:
        player = session.execute(select(Player).options(selectinload(Player.user)).order_by(desc(Player.level)).limit(10)).scalars().all()
        res = '🏆 *ТОП 10 ПО УРОВНЮ*\n\n'
        counter = 0
        for p in player:
            counter += 1
            medal = '🥇' if counter == 1 else '🥈' if counter == 2 else '🥉' if counter == 3 else f'{counter}️⃣'
            res += f'{medal} *{p.user.name}*: {p.level}Lvl\n'
        return(res)