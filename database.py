from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///bot.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    phone = Column(String, unique=True)
    name = Column(String)
    role = Column(String, default="driver")

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True)
    number = Column(String, unique=True)
    brand = Column(String)
    model = Column(String)
    fuel = Column(String)
    current_mileage = Column(Integer)

class Shift(Base):
    __tablename__ = "shifts"
    id = Column(Integer, primary_key=True)
    driver_id = Column(Integer, ForeignKey("users.id"))
    car_id = Column(Integer, ForeignKey("cars.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    start_mileage = Column(Integer)
    end_mileage = Column(Integer)
    status = Column(String, default="active")

Base.metadata.create_all(bind=engine)
