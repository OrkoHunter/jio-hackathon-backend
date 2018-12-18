from sqlalchemy import Table, Column, Integer, ForeignKey, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()
engine = create_engine('mysql://fykfncuva5c32yws:y4581v48wq0jchft@ou6zjjcqbi307lip.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/qunovkvl5ol8c6pu', echo=True)

class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    address = Column(String)
    phone = Column(String)
    user_stock = relationship("stock")
    
    def __repr__(self):
        return f"<User(name={user_name}, user_id={user_id},address={address},phone={phone},stock={user_stock})>"

class Stock(Base):
    __tablename__ = 'stock'
    prod_id = Column(String, primary_key=True)
    unit_type = Column(String)
    available_item = Column(Integer)
    price_per_unit = Column(Float)
    minimum_item = Column(Integer)

    def __repr__(self):
        return f"<User(id={prod_id}, unit_type={unit_type},available_item={available_item},price_per_unit={price_per_unit},min_item={minimum_item})>"