from fastapi import FastAPI
#
from .routers import router as stock_router
from . import models
from .database import engine
#

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Routers
app.include_router(stock_router)