from routers.webapi.cabinet import router as cabinet_router
from routers.webapi.corpus import router as corpus_router
from routers.webapi.lesson import router as lesson_router
from routers.webapi.lesson_timetable import (
    router as lesson_timetable_router,
)
from routers.webapi.announcements import router as announcements_router
from routers.webapi.school import router as school_router
from routers.webapi.subclass import router as subclass_router
from routers.webapi.teacher import router as teacher_router

routers = list(
    map(lambda x: globals()[x], filter(lambda x: "router" in x, globals().keys()))
)
