from sqlalchemy import Column, Float, String, Date, DateTime, Integer
from .database import Base

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    currency = Column(String)
    close_price = Column(Float)
    date = Column(Date, index=True)
