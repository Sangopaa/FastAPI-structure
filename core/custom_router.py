from fastapi import APIRouter
from core.standard_response_route import StandardResponseRoute


def CustomRouter(*args, **kwargs) -> APIRouter:
    kwargs.setdefault("route_class", StandardResponseRoute)
    return APIRouter(*args, **kwargs)
