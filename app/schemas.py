from pydantic import BaseModel, validator, Field
from typing import Dict

class StockRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol like 'AAPL'")
    currency: str = Field(..., description="Currency code like 'USD'")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")

class StockResponse(BaseModel):
    symbol: str = Field(..., description="Stock symbol like 'AAPL'")
    currency: str = Field(..., description="Currency code like 'USD'")
    daily_close: Dict[str, float] = Field(..., description="Daily close price in the given currency")
