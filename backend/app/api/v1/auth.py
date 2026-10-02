from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/test")
async def auth_test():
    return {"message": "Auth API is working"}