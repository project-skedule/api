from typing import List
from fastapi import APIRouter
from routers.botapi import routers as bot_api_routers
from routers.webapi import routers as web_api_routers
from extra.service_auth import router as service_auth_router

routers: List[APIRouter] = [service_auth_router]
routers.extend(web_api_routers)
routers.extend(bot_api_routers)
