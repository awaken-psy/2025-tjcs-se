from fastapi import APIRouter

auth_router = APIRouter(prefix='/auth', tags=['Authorization'])
capsule_router = APIRouter(prefix='/capsule', tags=['Capsule'])
unlock_router = APIRouter(prefix='/unlock', tags=['Unlock'])
event_router = APIRouter(prefix='/event', tags=['Event'])
hub_router = APIRouter(prefix='/hub', tags=['Hub'])
map_router = APIRouter(prefix='/map', tags=['Map'])
user_router = APIRouter(prefix='/user', tags=['User'])