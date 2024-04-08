from fastapi import APIRouter

from .account import router as account_router
from .auth import router as auth_router
from .risks import router as risk_router

router = APIRouter(prefix="/api")
router.include_router(account_router, prefix="/account", tags=["Account"])
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(risk_router, prefix="/risks", tags=["Risks"])
