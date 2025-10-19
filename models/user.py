from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__="user"

    id=Column(Integer, primary_key=True, nullable=False,index=True)
    username=Column(String(100), nullable=False,index=True)
    password=Column(String(255), nullable=False)
    created_at=Column(DateTime,nullable=False,default=datetime.utcnow)
    updated_at=Column(DateTime,nullable=False,default=datetime.utcnow)
    
    user_role=relationship("UserRole", back_populates="user",cascade="all, delete-orphan")

class Role(Base):
    __tablename__="role"

    id=Column(Integer, primary_key=True, nullable=False, index=True)
    name=Column(String(100), nullable=False, unique=True, index=True)
    created_at=Column(DateTime, default=datetime.utcnow)

    user_role=relationship("UserRole", back_populates="role",cascade="all, delete-orphan")

class UserRole(Base):
    __tablename__="UserRole"
    id=Column(Integer, primary_key=True, nullable=False, index=True)
    user_id=Column(Integer, ForeignKey("user.id"),nullable=False,index=True)
    role_id=Column(Integer,ForeignKey("role.id"),nullable=False,index=True)

    role=relationship("Role", back_populates="user_role")
    user=relationship("User", back_populates="user_role")

