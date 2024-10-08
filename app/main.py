# File path: app/main.py

from fastapi import *
from src.endpoints import *

app = FastAPI()

app.include_router(router)