# File path: main.py
import logging
from fastapi import FastAPI
from src.endpoints.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"  # добавили дату и время
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
