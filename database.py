
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "sqlite:///bot.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=True)
    phone = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default="driver")
    
    # Связь с сменами
    shifts = relationship("Shift", back_populates="driver")

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True)
    number = Column(String, unique=True, nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    fuel = Column(String, nullable=False)
    current_mileage = Column(Integer, default=0)
    
    # Связь с сменами
    shifts = relationship("Shift", back_populates="car")

class Shift(Base):
    __tablename__ = "shifts"
    id = Column(Integer, primary_key=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    start_mileage = Column(Integer, nullable=True)
    end_mileage = Column(Integer, nullable=True)
    status = Column(String, default="active")
    
    # Связи
    driver = relationship("User", back_populates="shifts")
    car = relationship("Car", back_populates="shifts")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Связь с пользователем
    user = relationship("User")

# Создание таблиц
Base.metadata.create_all(bind=engine)
