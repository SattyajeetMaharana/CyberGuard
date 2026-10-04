from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.auth import router as auth_router
from app.api.v1.departments import router as departments_router
from app.api.v1.devices import router as devices_router
from app.api.v1.events import router as events_router
from app.api.v1.organizations import router as organizations_router
from app.api.v1.users import router as users_router
from app.api.v1.employees import router as employees_router
from app.api.v1.invitations import router as invitations_router
from app.api.v1.security_contexts import router as security_contexts_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(devices_router)
api_router.include_router(events_router)
api_router.include_router(organizations_router)
api_router.include_router(admin_router)
api_router.include_router(departments_router)
api_router.include_router(employees_router)
api_router.include_router(analysis_router)
api_router.include_router(invitations_router)
api_router.include_router(security_contexts_router)