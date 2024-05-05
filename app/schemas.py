from datetime import datetime

from pydantic import BaseModel, validator, Field
from typing import Dict

class StockRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol like 'AAPL'", example="AAPL")
    currency: str = Field(..., description="Currency code like 'USD'", example="USD")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format",example="2021-06-17")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format", example="2021-06-18")

class StockResponse(BaseModel):
    symbol: str = Field(..., description="Stock symbol like 'AAPL'", example="AAPL")
    currency: str = Field(..., description="Currency code like 'USD'", example="USD")
    last_refreshed: str = Field(..., description="Last refreshed date in YYYY-MM-DD format, when the api data was last called", example="2021-06-18")
    daily_close: Dict[str, float] = Field(..., description="Daily close price in the given currency", example={"2021-06-18": 131.79})
