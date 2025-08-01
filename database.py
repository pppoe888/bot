from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)  # admin, driver, logist

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True, nullable=False)
    brand = Column(String, default="")
    model = Column(String, default="")
    fuel = Column(String, default="")
    current_mileage = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    # Связи
    driver = relationship("User", foreign_keys=[driver_id])
    car = relationship("Car", foreign_keys=[car_id])

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Связи
    user = relationship("User", foreign_keys=[user_id])

class ShiftPhoto(Base):
    __tablename__ = "shift_photos"

    id = Column(Integer, primary_key=True, index=True)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    photo_type = Column(String, nullable=False)  # front, back, left, right, oil, coolant, interior
    file_id = Column(String, nullable=False)  # Telegram file_id
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    shift = relationship("Shift", foreign_keys=[shift_id])

class CargoItem(Base):
    __tablename__ = "cargo_items"

    id = Column(Integer, primary_key=True, index=True)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    item_number = Column(String, nullable=False)
    item_name = Column(String, nullable=False)
    is_loaded = Column(Boolean, default=False)
    loaded_at = Column(DateTime, nullable=True)

    # Связи
    shift = relationship("Shift", foreign_keys=[shift_id])

# Создание таблиц
Base.metadata.create_all(bind=engine)