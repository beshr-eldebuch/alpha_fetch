import abc
import os
from datetime import datetime
from typing import Union
import requests
import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc
#
from .models import Stock, StockPrice
from .schemas import StockResponse
#

class IStockRepository:
    def __init__(self, db: Session):
        self.db = db
    @abc.abstractmethod
    def get_stock_data(
        self, symbol: str, start_date: str, end_date: str
    ) -> Union[StockResponse, None]:
        pass


class StockDBRepository(IStockRepository):
    def get_stock_data(
        self, symbol: str, start_date: str, end_date: str
    ):
        """
        Get stock data from db for the given symbol and date range.
        """
        query = (
            self.db.query(
               Stock.symbol, Stock.currency, StockPrice.date, StockPrice.close, Stock.last_refreshed
            )
            .join(Stock, Stock.id == StockPrice.stock_id)
            .filter(
                Stock.symbol == symbol, StockPrice.date >= start_date, StockPrice.date <= end_date
            )
            .order_by(desc(StockPrice.date))
            .all()
        )
        if not query:
            logging.info(f"No stock data found in db for {symbol} between {start_date} and {end_date}")
            return None
        logging.info(
            f"Fetched {len(query)} stock data from db for {symbol} between {start_date} and {end_date}"
        )
        daily_close = {
            str(item[2]): item[3] for item in query
        }
        last_refreshed = query[0][4] if query else None
        last_refreshed = last_refreshed.strftime("%Y-%m-%d") if last_refreshed else None
        return StockResponse(symbol=symbol, currency=query[0][1], daily_close=daily_close, last_refreshed=last_refreshed)
class StockAPIRepository(IStockRepository):
    def get_stock_data(
        self, symbol: str, start_date: str, end_date: str
    ):
        """
        Fetch stock data from AlphaVantage API for the given symbol and date range.
        """
        API_KEY = os.environ.get("ALPHA_API_KEY")
        logging.info(f"Fetching stock data from AlphaVantage for {symbol}")
        url = f"https://alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # last refreshed date = last API call date.
                last_refreshed = datetime.now().strftime("%Y-%m-%d")
                data = response.json().get("Time Series (Daily)", {})
                daily_close = {}
                for date, values in data.items():
                    close_price = float(values.get("4. close"))
                    daily_close[str(date)] = close_price
                stock_res = StockResponse(symbol=symbol, currency="USD", daily_close=daily_close, last_refreshed=last_refreshed)
                # cache stock data in db
                self.cache_stock_data(stock_res)
                # filter data between start_date and end_date
                stock_res.daily_close = {
                    date: price
                    for date, price in stock_res.daily_close.items()
                    if start_date <= date <= end_date
                }
                return stock_res
            logging.error(
                f"Failed to fetch stock data from AlphaVantage for {symbol} between {start_date} and {end_date} with status code {response.status_code}"
            )
            return None
        except requests.exceptions.RequestException as e:
            logging.error(
                f"Failed to fetch stock data from AlphaVantage for {symbol} between {start_date} and {end_date}"
            )
            logging.error(e)
            return None
    def cache_stock_data(
        self, stock: StockResponse
    ) -> None:
        """
        Cache stock data in db to avoid frequent API calls.
        Since we're storing daily close price data, it makes sense to call the api once a day and store the data in the database.
        """
        # check if stock already exists in db
        stock_db = self.db.query(Stock).filter(Stock.symbol == stock.symbol).first()
        if not stock_db:
            # Create new stock record
            last_refreshed = datetime.strptime(stock.last_refreshed, "%Y-%m-%d")
            stock_db = Stock(symbol=stock.symbol, currency=stock.currency, last_refreshed=last_refreshed)
            logging.info(f"Created stock record for {stock.symbol}")
            self.db.add(stock_db)
            self.db.commit()
        # Get last date for which stock data is cached
        last_date = self.db.query(StockPrice.date).filter(StockPrice.stock_id == stock_db.id).order_by(StockPrice.date.desc()).first()
        last_date = last_date[0] if last_date else None
        # Cache stock price data, starting from the next day of last cached date
        for date, close_price in stock.daily_close.items():
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            if last_date and date_obj <= last_date:
                continue
            stock_price = StockPrice(stock_id=stock_db.id, date=date_obj, close=close_price)
            self.db.add(stock_price)
            self.db.commit()
        logging.info(f"Cached stock data for {stock.symbol} between {min(stock.daily_close.keys())} and {max(stock.daily_close.keys())}")


class StockService:
    def __init__(self, api_repo: StockAPIRepository, db_repo: StockDBRepository, db: Session):
        self.api_repo = api_repo
        self.db_repo = db_repo
        self.db = db

    def get_processed_stock_data(self, symbol: str, start_date: str, end_date: str, currency: str) -> StockResponse:
        """
        Get stock data for the given symbol and date range.
        If stock data is not present in db or stale, fetch it from API.
        If stock data is present in db and not stale, fetch it from db.
        Convert the stock price to the given currency.
        """
        # Check if stock data is available in db, else fetch from API
        if self.is_data_needs_refresh(symbol, end_date):
            stock_data = self.api_repo.get_stock_data(symbol, start_date, end_date)
        else:
            stock_data = self.db_repo.get_stock_data(symbol, start_date, end_date)

        if not stock_data:
            raise ValueError("No stock data found")

        exchange_rate = get_exchange_rate(stock_data.currency, currency)
        if exchange_rate is None:
            raise ValueError("Failed to fetch exchange rate")

        stock_data.daily_close  = {date: price * exchange_rate for date, price in stock_data.daily_close.items()}

        return stock_data

    def is_data_needs_refresh(self, symbol: str, end_date: str) -> bool:
        """
        Check if stock data needs to be refreshed from API.
        If stock data is not present in db, return True.
        If stock data is present in db and last refreshed date is older than 1 day, return True.
        If stock data is present in db and last refreshed date is same or older than end_date, return False ( we already have the data).
        """
        stock = self.db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            logging.info(f"No stock data found in db for {symbol}")
            return True
        if end_date <= stock.last_refreshed.strftime("%Y-%m-%d"):
            logging.info(f"Stock data found in db for {symbol}, no refresh needed")
            return False
        if (datetime.utcnow() - stock.last_refreshed).days > 1:
            logging.info(f"Stock data found in db for {symbol}, but stale, needs refresh")
            return True
        logging.info(f"Stock data found in db for {symbol}, no refresh needed")
        return False

def get_exchange_rate(src_currency: str, dest_currency: str) -> Union[float, None]:
    """
    Fetch currency exchange rate from AlphaVantage API.
    Since the exchange rate is dynamic, we fetch it from the API every time.
    """
    API_KEY = os.environ.get("ALPHA_API_KEY")
    logging.info(
        f"Fetching currency exchange rate from {src_currency} to {dest_currency}"
    )
    url = f"https://alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={src_currency}&to_currency={dest_currency}&apikey={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            rate = (
                response.json()
                .get("Realtime Currency Exchange Rate", {})
                .get("5. Exchange Rate")
            )
            logging.info(
                f"Currency exchange rate from {src_currency} to {dest_currency} is {rate}"
            )
            return float(rate) if rate else None
        logging.error(
            f"Failed to fetch currency exchange rate from {src_currency} to {dest_currency} with status code {response.status_code}"
        )
        return None
    except requests.exceptions.RequestException as e:
        logging.error(
            f"Failed to fetch currency exchange rate from {src_currency} to {dest_currency}"
        )
        logging.error(e)
        return None
