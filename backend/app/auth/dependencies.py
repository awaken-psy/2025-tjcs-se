from fastapi import Depends, Header
from fastapi import HTTPException
from typing import Optional, Union

# 修复导入路径
from app.auth.jwt_handler import JWTHandler, AccessTokenPayload, RefreshTokenPayload
from app.domain.user import UserFactory, UserRole, BaseUser, RegisteredUser, AdminUser, AuthorizedUser

def get_user_from_token(authorization:str) -> BaseUser:
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid header. Token should be 'Bearer <token>'")
    token = parts[1]
    success, payload, error = JWTHandler.verify_access_token(token)
    if not success or not payload:
        raise HTTPException(status_code=401, detail=error)
    
    if payload.role == UserRole.GUEST:
        return UserFactory.create_guest_user()
    elif payload.role == UserRole.USER:
        return UserFactory.create_registered_user(user_id=int(payload.sub), username=payload.username)
    elif payload.role == UserRole.ADMIN:
        return UserFactory.create_admin_user(user_id=int(payload.sub), username=payload.username)
    else:
        raise HTTPException(status_code=401, detail="Unkown user role")
    
def login_required(authorization: str=Header(alias="Authorization")) -> AuthorizedUser:
    user = get_user_from_token(authorization)
    if not isinstance(user, (RegisteredUser, AdminUser)):
        raise HTTPException(status_code=401, detail="User not authorized")
    return user

def admin_required(user: AuthorizedUser=Depends(login_required)) -> AdminUser:
    if not isinstance(user, AdminUser):
        raise HTTPException(status_code=403, detail="Admin required")
    return user
    


    