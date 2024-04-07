from fastapi import APIRouter

from .account import router as account_router
from .auth import router as auth_router

router = APIRouter(prefix="/api")
router.include_router(account_router, prefix="/account", tags=["Account"])
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
