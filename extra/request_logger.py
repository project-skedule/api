from typing import Any, Dict
from fastapi import Request


def create(logger: Any):
    async def logging_dependency(request: Request):
        try:
            logger.debug(f"{request.method} {request.url}")
            logger.debug("Params:")
            params: Dict[
                str, Any
            ] = request.path_params  # pyright: reportUnknownMemberType=false
            for name, value in params.items():
                logger.debug(f"\t{name}: {value}")
            logger.debug("Headers:")
            for name, value in request.headers.items():
                logger.debug(f"\t{name}: {value}")
            logger.debug("BODY:")
            logger.debug((await request.body()))
        except Exception as e:
            logger.debug(f"Error while logging: {e}")

    return logging_dependency
