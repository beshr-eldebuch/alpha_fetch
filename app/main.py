import logging

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
#
from .rate_limiter import limiter
from .routers import router as stock_router
from . import models
from .database import engine
#

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Routers
app.include_router(stock_router)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# middleware
app.add_middleware(SlowAPIMiddleware)
#logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
