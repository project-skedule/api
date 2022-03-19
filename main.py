from config import DEFAULT_LOGGER as logger
from config import WEBSITE_HOST, WEBSITE_PORT
from extra.api_router import LoggingRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import routers

app = FastAPI(
    title="Skedule API v2", debug=False, version="v2", router_class=LoggingRouter
)
logger.info("App created")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://{WEBSITE_HOST}:{WEBSITE_PORT}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in routers:
    app.include_router(router)
    logger.info(f"Router {router.prefix} included")


@app.get("/")
async def index_page():
    pass
