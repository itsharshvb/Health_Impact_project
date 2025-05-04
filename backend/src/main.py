from fastapi import FastAPI
from api.routes import router as api_router
from core.logging_config import setup_logging
from db.session import get_db

app = FastAPI()

setup_logging()
app.include_router(api_router)
