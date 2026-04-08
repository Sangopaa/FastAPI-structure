from fastapi import APIRouter
from api.v1.endpoints import users, auth
from core.custom_route import StandardResponseRoute

v1_router = APIRouter(route_class=StandardResponseRoute)
v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
v1_router.include_router(users.router, prefix="/users", tags=["Users"])
