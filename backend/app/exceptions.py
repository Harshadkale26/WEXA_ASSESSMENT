from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.logging import get_logger

log = get_logger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError):
        log.info("request_validation_error", errors=exc.errors())
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException):
        log.info("http_exception", status_code=exc.status_code, detail=exc.detail)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(_: Request, exc: SQLAlchemyError):
        log.exception("database_error")
        return JSONResponse(status_code=500, content={"detail": "Database error"})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception):
        log.exception("unhandled_error")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

