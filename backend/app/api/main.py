from fastapi import APIRouter

from app.api.routes import document, files, utils

api_router = APIRouter()
api_router.include_router(utils.router)
api_router.include_router(files.router)
api_router.include_router(document.router)
