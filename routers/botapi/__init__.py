from routers.botapi.id_getter import router as id_getter_router
from routers.botapi.info import router as info_router
from routers.botapi.lessons import router as lessons_router
from routers.botapi.registration import router as registration_router
from routers.botapi.role_management import router as role_management_router

routers = list(
    map(lambda x: globals()[x], filter(lambda x: "router" in x, globals().keys()))
)
