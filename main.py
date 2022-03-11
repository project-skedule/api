from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import DEFAULT_LOGGER as logger, WEBSITE_HOST
from routers import routers

app = FastAPI(
    title=__file__,
    debug=True,
)
logger.info("App created")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://dartt0n.xyz:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


for router in routers:
    app.include_router(router)
    logger.info(f"Router {router} included")


@app.get("/")
def index_page():
    pass
