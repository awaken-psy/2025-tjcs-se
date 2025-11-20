from fastapi import APIRouter

auth_router = APIRouter(prefix='/auth', tags=['Authorization'])
event_router = APIRouter(prefix='/event', tags=['Event'])
hub_router = APIRouter(prefix='/hub', tags=['Hub'])
map_router = APIRouter(prefix='/map', tags=['Map'])
user_router = APIRouter(prefix='/user', tags=['User'])

# 保留前端使用的路由器
browse_router = APIRouter(prefix='/browse', tags=['Browse'])
drafts_router = APIRouter(prefix='/drafts', tags=['Drafts'])
media_router = APIRouter(prefix='/media', tags=['Media'])
upload_router = APIRouter(prefix='/upload', tags=['Upload'])