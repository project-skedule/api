from typing import List
from fastapi import APIRouter
from routers.botapi import routers as bot_api_routers
from routers.webapi import routers as web_api_routers

routers: List[APIRouter] = []
routers.extend(web_api_routers)
routers.extend(bot_api_routers)
