import logging, os

from fastapi import Depends, FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth.adapter.input.api import router as auth_router
from app.container import Container
from app.user.adapter.input.api import router as user_router
from core.config import config
from core.exceptions import CustomException
from core.fastapi.dependencies import Logging
from core.fastapi.middlewares import (
    AuthBackend,
    AuthenticationMiddleware,
    SQLAlchemyMiddleware,
    RequestIDMiddleware,
    AccessLogMiddleware
)
# from core.helpers.cache import Cache, CustomKeyMaker
from app.api.event import event_router
from app.api.calendar import calendar_router
from app.logging_config import LOGGING_CONFIG

import sentry_sdk

def init_routers(app_: FastAPI) -> None:
    container = Container()
    user_router.container = container
    auth_router.container = container
    app_.include_router(user_router)
    app_.include_router(auth_router)
    app_.include_router(event_router)
    app_.include_router(calendar_router)


def init_listeners(app_: FastAPI) -> None:
    # Exception handler
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )


def on_auth_error(request: Request, exc: Exception):
    status_code, error_code, message = 401, None, str(exc)
    if isinstance(exc, CustomException):
        status_code = int(exc.code)
        error_code = exc.error_code
        message = exc.message

    return JSONResponse(
        status_code=status_code,
        content={"error_code": error_code, "message": message},
    )


def make_middleware() -> list[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(RequestIDMiddleware),
        Middleware(AccessLogMiddleware),
        Middleware(
            AuthenticationMiddleware,
            backend=AuthBackend(),
            on_error=on_auth_error,
        ),
        Middleware(SQLAlchemyMiddleware),
    ]
    return middleware


# def init_cache() -> None:
#     Cache.init(backend=RedisBackend(), key_maker=CustomKeyMaker())


def create_app() -> FastAPI:
    # Init Central Logger
    log_dir = os.path.dirname(f'{config.CENTRAL_LOG_FILE_PATH}/{config.CENTRAL_LOG_FILE_NAME}')

    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)

    # Init Sentry
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        send_default_pii=True,
    )

    app_ = FastAPI(
        title="Hide",
        description="Hide API",
        version="1.0.0",
        docs_url=None if config.ENV == "production" else "/docs",
        redoc_url=None if config.ENV == "production" else "/redoc",
        dependencies=[Depends(Logging)],
        middleware=make_middleware(),
    )
    init_routers(app_=app_)
    init_listeners(app_=app_)
    # init_cache()

    @app_.on_event("startup")
    async def startup_msg():
        logger = logging.getLogger(config.CENTRAL_LOGGER_NAME)
        logger.info("Application startup complete")

    return app_


app = create_app()
