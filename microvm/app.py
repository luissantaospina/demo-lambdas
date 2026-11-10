import logging
import uvicorn
from fastapi import FastAPI

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/")
def hello():
    logger.info("Received request to hello world endpoint")
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
