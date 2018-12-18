from sqlalchemy import Table, Column, Integer, ForeignKey, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    address = Column(String)
    phone = Column(String)
    user_stock = relationship("stock")
    
    def __repr__(self):
        return "<User(name={}, user_id={},address={},phone={},stock={})>".format(user_name,user_id,address,phone,user_stock)

class Stock(Base):
    __tablename__ = 'stock'
    prod_id = Column(String, primary_key=True)
    unit_type = Column(String)
    available_item = Column(Integer)
    price_per_unit = Column(Float)
    minimum_item = Column(Integer)

    def __repr__(self):
        return "<User(id={}, unit_type={},available_item={},price_per_unit={},min_item={})>".format(prod_id,unit_type,available_item,price_per_unit,minimum_item)