import logging
#
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
#
from .schemas import StockRequest, StockResponse
from .services import get_stock_data_from_db, get_exchange_rate, create_stock
from .database import SessionLocal, engine
from . import  models
from .rate_limiter import limiter
#
router = APIRouter()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/health')
def health_check():
    return {"status": "ok"}

@router.get("/stocks", response_model=StockResponse)
@limiter.limit("25/day")
def get_stock_data(request: Request,
                   stock_req: StockRequest = Depends(),
                   db: Session = Depends(get_db)
                   ):

    # Read stock from db between start date and end date
    stock_data = get_stock_data_from_db(stock_req.symbol, stock_req.start_date, stock_req.end_date, db)
    if not stock_data:
        raise HTTPException(status_code=404, detail="No stock data found for the given range.")

    # Convert to targeted currency
    converted_data = {}
    exchange_rate = get_exchange_rate('USD', stock_req.currency)
    if exchange_rate is None:
        raise HTTPException(status_code=500, detail="Failed to fetch currency exchange rate.")
    for stock in stock_data:
        converted_data[str(stock.date)] = stock.close_price * exchange_rate

    return StockResponse(
        symbol=stock_req.symbol,
        currency=stock_req.currency,
        daily_close=converted_data
    )
