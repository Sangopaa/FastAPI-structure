from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.v1.api_router import v1_router
from core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    integrity_error_handler,
    no_result_found_handler,
    data_error_handler,
)
from sqlalchemy.exc import IntegrityError, NoResultFound, DataError

app = FastAPI(title="FastAPI Structure")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/api/v1")

# Exception Handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(NoResultFound, no_result_found_handler)
app.add_exception_handler(DataError, data_error_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.get("/health")
def read_root():
    return {"status": "running"}
