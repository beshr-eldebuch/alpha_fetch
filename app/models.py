from sqlalchemy import Column, Float, String, Date, DateTime, Integer, ForeignKey, BigInteger
from .database import Base
from datetime import datetime

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True, unique=True)
    currency = Column(String)
    last_refreshed = Column(DateTime, default=datetime.utcnow)

class StockPrice(Base):
    __tablename__ = "stocks_prices"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    currency = Column(String)
    close = Column(Float)
    date = Column(Date, index=True)
