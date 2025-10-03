from fastapi import FastAPI
from app.api.api import register_routes
from app.utils.logging import configure_logging, LogLevels
from dotenv import load_dotenv
from app.db.core import mongo_conn
import logging
load_dotenv()

configure_logging(log_level=LogLevels.info)

app = FastAPI()
register_routes(app)

