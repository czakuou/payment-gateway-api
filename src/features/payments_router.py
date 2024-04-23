from fastapi import APIRouter

from src.features.create_checkout import router as create_checkout

router = APIRouter()

router.include_router(create_checkout)
