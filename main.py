from fastapi import FastAPI

from config import DEFAULT_LOGGER as logger
from routers import routers

app = FastAPI(
    title=__file__,
    debug=True,
)
logger.info("App created")

for router in routers:
    app.include_router(router)
    logger.info(f"Router {router} included")


@app.get("/")
def index_page():
    pass
