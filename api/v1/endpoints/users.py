from fastapi import APIRouter

router = APIRouter()


@router.get("/me/profile")
async def get_me():
    return {"user": "current_user_data"}
