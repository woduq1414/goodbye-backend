from fastapi import APIRouter, FastAPI

from api.user.views import router as user_router
from api.target.views import router as target_router


router = APIRouter(
    responses={404: {"description": "Not found"}},
)


router.include_router(user_router, prefix="/user", tags=["user"])
router.include_router(target_router, prefix="/target", tags=["target"])



@router.get("/")
async def root():
    return {"message": "Hello API!"}