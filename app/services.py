import os
from datetime import datetime
from typing import Union

from sqlalchemy.orm import Session
from .models import Stock
import requests
import logging

def get_stock_data_from_db(symbol: str, start_date: str, end_date: str, db: Session) -> Stock:
    query = db.query(Stock).filter(
        Stock.symbol == symbol,
        Stock.date >= start_date,
        Stock.date <= end_date
    ).all()
    logging.info(f"Fetched {len(query)} stock data from db for {symbol} between {start_date} and {end_date}")
    return query

def create_stock(db: Session, symbol: str, currency: str, close_price: float, date: str) -> Stock:
    date = datetime.strptime(date, "%Y-%m-%d")
    stock = Stock(symbol=symbol, currency=currency, close_price=close_price, date=date)
    db.add(stock)
    db.commit()
    db.refresh(stock)
    logging.info(f"Created stock data for {symbol} on {date}")
    return stock

def get_exchange_rate(src_currency: str, dest_currency: str) -> Union[float, None]:
    API_KEY = os.environ.get('API_KEY')
    logging.info(f"Fetching currency exchange rate from {src_currency} to {dest_currency}")
    url = f"https://alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={src_currency}&to_currency={dest_currency}&apikey={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            rate = response.json().get('Realtime Currency Exchange Rate',{}).get('5. Exchange Rate')
            return float(rate) if rate else None
        logging.error(f"Failed to fetch currency exchange rate from {src_currency} to {dest_currency} with status code {response.status_code}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch currency exchange rate from {src_currency} to {dest_currency}")
        logging.error(e)
        return None

