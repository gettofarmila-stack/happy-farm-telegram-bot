from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
from database.engine import engine

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    username = Column(String)
    user_id = Column(String, unique=True, nullable=False)
    register_at = Column(DateTime, default=datetime.now)

    stats = relationship('Player', back_populates='user', uselist=False)
    inventory = relationship('InventoryItem', back_populates='owner')
    garden = relationship('Garden', back_populates='owner')

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name_key = Column(String)
    description = Column(String)

class InventoryItem(Base):
    __tablename__ = 'inventory_items'
    owner_id = Column(String, ForeignKey('users.user_id'), primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), primary_key=True)
    count = Column(Integer, default=1)

    owner = relationship('User', back_populates='inventory')
    item = relationship('Item')

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    owner_id = Column(String, ForeignKey('users.user_id'), unique=True)
    balance = Column(Integer, default=100)
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    max_energy = Column(Integer, default=100)
    energy = Column(Integer, default=100)
    user = relationship('User', back_populates='stats')

class Seed(Base):
    __tablename__ = 'seeds'
    id = Column(Integer, primary_key=True) 
    seed_item_id = Column(Integer, ForeignKey('items.id'))
    result_item_id = Column(Integer, ForeignKey('items.id'))
    grow_time = Column(Integer)
    
    garden_slots = relationship('Garden', back_populates='current_seed')
    item = relationship('Item', foreign_keys=[seed_item_id])

class Garden(Base):
    __tablename__ = 'gardens'
    id = Column(Integer, primary_key=True)
    owner_id = Column(String, ForeignKey('users.user_id'))
    seed_id = Column(Integer, ForeignKey('seeds.id'))
    
    start_time = Column(DateTime, default=datetime.now)
    boost = Column(Float, default=1.0)
    
    owner = relationship('User', back_populates='garden')
    current_seed = relationship('Seed', back_populates='garden_slots')

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'))
    price = Column(Integer)
    category = Column(String)

    item = relationship('Item')
    
class Buyer(Base):
    __tablename__ = 'buyer'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'))
    min_price = Column(Integer)
    max_price = Column(Integer)
    now_price = Column(Integer)

    item = relationship('Item')

Base.metadata.create_all(engine)