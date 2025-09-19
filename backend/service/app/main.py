import logging
import os

from fastapi.exceptions import ValidationException
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_sqlalchemy import DBSessionMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.core.router import router
from app.models import Base
from app.core.database import engine
from app.core.config import settings
from app.utils.exception_handler import (
    CustomException,
    fastapi_error_handler,
    validation_exception_handler,
    custom_error_handler,
)

logging.config.fileConfig(settings.LOGGING_CONFIG_FILE, disable_existing_loggers=False)
Base.metadata.create_all(bind=engine)


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        docs_url="/docs",
        redoc_url="/re-docs",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        description="""
        Base frame with FastAPI micro framework + Postgresql
            - Login/Register with JWT
            - Permission_required & Login_required
            - CRUD User
            - Unit testing with Pytest
            - Dockerize
            - MMSE Assessment API
        """,
        debug=settings.DEBUG,
        swagger_ui_init_oauth={
            "clientId": settings.KEYCLOAK_CLIENT_ID,
            "scopes": {"openid": "OpenID Connect scope"},
        },
        swagger_ui_parameters={
            "docExpansion": "none",
        },
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(DBSessionMiddleware, db_url=settings.DATABASE_URL)
    
    # Mount static files for MMSE media assets (only if directory exists)
    static_dir = "static"
    if os.path.exists(static_dir) and os.path.isdir(static_dir):
        application.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    application.include_router(router, prefix=settings.API_PREFIX)
    application.add_exception_handler(CustomException, custom_error_handler)
    application.add_exception_handler(ValidationException, validation_exception_handler)
    application.add_exception_handler(Exception, fastapi_error_handler)

    return application


app = get_application()
if __name__ == "__main__":
    # Note: reload=True is not compatible with workers > 1
    if settings.DEBUG:
        uvicorn.run(app, host="0.0.0.0", port=8777, reload=True)
    else:
        uvicorn.run(app, host="0.0.0.0", port=8777, workers=4)
