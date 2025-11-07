from sqlalchemy import Column, ForeignKey, String, Float, DateTime, Integer
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Customer(Base):
    __tablename__="customers"
    
    customer_id=Column(String(200), primary_key=True,index=True)
    customer_name=Column(String(200), nullable=False,default="Unknown")
    segment=Column(String(200), nullable=True,default="Unknown")
    city=Column(String(200), nullable=False)
    state=Column(String(200), nullable=False)
    postal_code=Column(String(200), nullable=True, default="00000")
    region=Column(String(200), nullable=False)
    created_on=Column(DateTime,nullable=True, default=datetime.utcnow)
    
    orders=relationship("Order",back_populates="customer")
    

class Product(Base):
    __tablename__="products"

    product_id=Column(String(200), primary_key=True,index=True)
    category=Column(String(200), nullable=False)
    sub_category=Column(String(200), nullable=False)
    product_name=Column(String(200), nullable=False)

    orders=relationship("Order",back_populates="product")

class Order(Base):
    __tablename__="orders"

    order_id=Column(String(100), primary_key=True, index=True)
    order_date=Column(DateTime, nullable=False)
    ship_mode=Column(String(100), nullable=False)
    customer_id=Column(String(200), ForeignKey("customers.customer_id"), index=True)
    product_id=Column(String(200), ForeignKey("products.product_id"), index=True)
    sales=Column(Float, nullable=False)
    quantity=Column(Integer, nullable=False)
    discount=Column(Float, nullable=False)
    profit=Column(Float, nullable=False)
    created_on=Column(DateTime, nullable=True, default=datetime.utcnow)

    customer=relationship("Customer",back_populates="orders")
    product=relationship("Product", back_populates="orders")








