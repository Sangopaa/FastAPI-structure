from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "data": None,
            "message": str(exc.detail)
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Flatten the pydantic validation errors nicely
    errors = [{"loc": ".".join(map(str, err["loc"])), "msg": err["msg"], "type": err["type"]} for err in exc.errors()]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "ok": False,
            "data": errors,
            "message": "Validation Error"
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    # Depending on the environment, you might log the actual exc here instead of exposing it
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "ok": False,
            "data": None,
            "message": "Internal Server Error"
        }
    )
