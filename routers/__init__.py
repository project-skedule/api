from routers.botapi import routers as bot_api_routers
from routers.webapi import routers as web_api_routers

routers = []
routers.extend(web_api_routers)
routers.extend(bot_api_routers)
