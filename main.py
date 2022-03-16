from fastapi import FastAPI, Depends, HTTPException
from extra.api_router import LoggingRouter
from extra.auth import authenticate_user, create_access_token, get_current_user
from config import DEFAULT_LOGGER as logger, API_TOKEN_URl, get_session

from fastapi.middleware.cors import CORSMiddleware
from routers import routers
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI(
    title="Skedule API v2", debug=False, version="v2", router_class=LoggingRouter
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
    logger.info(f"Router {router.prefix} included")


@app.get("/")
async def index_page():
    pass


@app.post(API_TOKEN_URl)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)
):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": create_access_token(data={"sub": user.name}),
        "token_type": "Bearer",
    }


@app.post("/test")
async def test(_=Depends(get_current_user)):
    pass
