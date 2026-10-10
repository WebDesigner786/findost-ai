"""Global Error Handling Middleware

Intercepts all application exceptions, validation errors, and database errors,
formatting them into a standard, typed JSON envelope:
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "details": ...
    }
}
Never leaks raw database connection strings, passwords, or stack traces in production.
"""

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

logger = logging.getLogger("findost.errors")


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handles standard Starlette / FastAPI HTTPExceptions."""
    code = f"HTTP_{exc.status_code}"
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        code = "NOT_FOUND"
    elif exc.status_code == status.HTTP_400_BAD_REQUEST:
        code = "BAD_REQUEST"
    elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
        code = "UNAUTHORIZED"
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        code = "FORBIDDEN"

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": exc.detail if isinstance(exc.detail, str) else "HTTP Request Error",
                "details": exc.detail if not isinstance(exc.detail, str) else None,
            }
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handles Pydantic payload / query validation errors."""
    errors = exc.errors()
    formatted_errors = []
    for err in errors:
        loc = " -> ".join(str(item) for item in err.get("loc", []))
        formatted_errors.append({
            "field": loc,
            "message": err.get("msg"),
            "type": err.get("type"),
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed. Inspect details for affected fields.",
                "details": formatted_errors,
            }
        },
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handles SQLAlchemy database errors securely without leaking connection strings."""
    logger.error(f"Database error on {request.method} {request.url.path}: {str(exc)}", exc_info=True)

    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": {
                    "code": "DATABASE_INTEGRITY_CONFLICT",
                    "message": "A database constraint violation occurred (e.g. duplicate key or invalid foreign key reference).",
                    "details": None,
                }
            },
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "DATABASE_ERROR",
                "message": "An error occurred while communicating with the database.",
                "details": None,
            }
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unhandled exceptions."""
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please try again later.",
                "details": None,
            }
        },
    )
