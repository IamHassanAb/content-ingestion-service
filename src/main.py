from fastapi import FastAPI
from src.api.api import register_routes
from src.utils.logging import configure_logging, LogLevels
from dotenv import load_dotenv

load_dotenv()

configure_logging(log_level=LogLevels.info)

app = FastAPI()
register_routes(app)
