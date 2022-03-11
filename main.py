from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import DEFAULT_LOGGER as logger
from routers import routers

app = FastAPI(
    title=__file__,
    debug=True,
)
logger.info("App created")

origins = [
    "http://localhost:3000",
    "http://127.0.1.1:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # BUG: FIXME: NOTE: ALERT: INFO: ERROR: TODO: _this is super bad_
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
