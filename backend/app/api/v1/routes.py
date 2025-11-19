from fastapi import APIRouter
from .capsule.capsule import router as capsule_router
from .capsule.unlock import router as unlock_router

auth_router = APIRouter(prefix='/auth', tags=['Authorization'])
event_router = APIRouter(prefix='/event', tags=['Event'])
hub_router = APIRouter(prefix='/hub', tags=['Hub'])
map_router = APIRouter(prefix='/map', tags=['Map'])
user_router = APIRouter(prefix='/user', tags=['User'])