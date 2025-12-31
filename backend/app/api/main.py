from fastapi import APIRouter

from app.api.routes import document, files, items, login, users, utils

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(users.private_router)
api_router.include_router(items.router)
api_router.include_router(utils.router)
api_router.include_router(files.router)
api_router.include_router(document.router)
