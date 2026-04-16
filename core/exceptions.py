from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound, DataError


async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "ok": False,
            "data": None,
            "message": "Relational integrity error (foreign key not found or duplicated).",
        },
    )


async def no_result_found_handler(request: Request, exc: NoResultFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "ok": False,
            "data": None,
            "message": "Resource not found in the database.",
        },
    )


async def data_error_handler(request: Request, exc: DataError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "ok": False,
            "data": None,
            "message": "Error in the data sent to the database.",
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"ok": False, "data": None, "message": str(exc.detail)},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Flatten the pydantic validation errors nicely
    errors = [
        {"loc": ".".join(map(str, err["loc"])), "msg": err["msg"], "type": err["type"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"ok": False, "data": errors, "message": "Validation Error"},
    )


async def general_exception_handler(request: Request, exc: Exception):
    # Depending on the environment, you might log the actual exc here instead of exposing it
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"ok": False, "data": None, "message": "Internal Server Error"},
    )
