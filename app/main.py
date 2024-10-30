# File path: main.py
import logging
from fastapi import FastAPI
from src.endpoints.routes import router
from pyngrok import ngrok

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(router)

port = 8000
public_url = ngrok.connect(port)
logger.info(f"ngrok запущен: {public_url}")

@app.on_event("shutdown")
def shutdown_event():
    """Закрываем ngrok туннель при завершении приложения."""
    ngrok.disconnect(public_url)
    ngrok.kill()
