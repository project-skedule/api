from time import time

import ujson
from config import DEFAULT_LOGGER as logger
from fastapi import Request, Response
from fastapi.routing import APIRoute


class LoggingRouter(APIRoute):
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request_id = id(request)
            start = time()
            response: Response = await original_route_handler(request)
            duration = time() - start
            logger.info(
                f"REQ: {request_id} "
                f'MTD: "{request.method}" '
                f"BDY: {(await request.body()) if (await request.body()) else {}} "
                f"HST: {request.client.host} "
                f"HDR: {dict(request.headers)} "
            )
            logger.info(
                f"RES: {request_id} "
                f'STC: "{response.status_code}" '
                f"TMN: {round(duration, 4)}s "
                f"BDY: {ujson.loads(response.body)} "
                f"HDR: {dict(response.headers)} "
            )

            return response

        return custom_route_handler
