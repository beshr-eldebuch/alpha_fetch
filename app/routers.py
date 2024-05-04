from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
#
from .schemas import StockRequest, StockResponse
from .services import StockService, StockDBRepository, StockAPIRepository
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
    stock_service = StockService(StockAPIRepository(db), StockDBRepository(db), db)
    try:
        result = stock_service.get_processed_stock_data(stock_req.symbol, stock_req.start_date, stock_req.end_date, stock_req.currency)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
