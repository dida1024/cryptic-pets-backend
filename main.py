import sentry_sdk
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.routing import APIRoute
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from infrastructure.config import settings
from interfaces.http.exceptions_handler import (
    BizException,
    biz_exception_handler,
    global_exception_handler,
)
from interfaces.http.v1.routers import api_router


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting application...")
    logger.info("Initializing database...")
    from infrastructure.persistence.postgres.init_db import init_db
    await init_db()

    logger.info("Registering event handlers...")
    from infrastructure.events.event_registry import register_all_event_handlers
    register_all_event_handlers()

    yield
    logger.info("Application shutdown complete.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    root_path=settings.ROOTPATH,
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

app.add_exception_handler(BizException, biz_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVER_PORT,
        reload=True if settings.ENVIRONMENT == "local" else False,
    )
