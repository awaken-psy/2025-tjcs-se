"""
用户数据仓库层 - 封装用户相关的数据库操作
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException

from app.database.orm.user import User
from app.database.config import get_db
from app.domain.user import UserFactory, AuthorizedUser


class UserRepository:
    """用户数据仓库"""

    def __init__(self):
        try:
            self.db:Session = next(get_db())
        except Exception as e:
            raise Exception(f"数据库会话创建失败: {e}")

    def create_user(
        # 必填
        self,
        username: str,
        email: str,
        password_hash: str,
        nickname: str,

        # 必要，但有默认值，为None时自动替换默认值
        user_type: Optional[str] = None,
        userrole: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        
        # 非必填，可以为空
        avatar_url:Optional[str] = None,
        bio:Optional[str] = None,
        campus_id:Optional[str] = None,
    ) -> AuthorizedUser:
        """
        创建新用户

        Args:
            必填：
            username: 用户名
            email: 邮箱
            password_hash: 密码哈希
            nickname: 昵称

            必要，但有默认值，为None时自动替换默认值：
            user_type: 用户类型
            userrole: 用户角色
            is_active: 是否激活
            is_verified: 是否已验证

            # 非必填，可以为空
            avatar_url: 头像URL
            bio: 个人简介
            campus_id: 校园ID/学号

        Returns:
            用户模型
        """
        try:
            new_user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                nickname=nickname,

                user_type=user_type,
                userrole=userrole,
                is_active=is_active,
                is_verified=is_verified,

                avatar_url=avatar_url,
                bio=bio,
                campus_id=campus_id
            )

            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)

            user_domain = self._orm2domain(new_user)
            if not user_domain:
                raise HTTPException(status_code=400, detail="用户角色不正确")
            return user_domain
        except Exception as e:
            self.db.rollback()
            raise e

    def get_user_by_id(self, user_id: int) -> Optional[AuthorizedUser]:
        """
        根据用户ID获取用户

        Args:
            user_id: 用户ID

        Returns:
            用户领域模型或None
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        return self._orm2domain(user) if user else None

    def get_user_by_email(self, email: str) -> Optional[AuthorizedUser]:
        """
        根据邮箱获取用户

        Args:
            email: 邮箱

        Returns:
            用户领域模型或None
        """
        user = self.db.query(User).filter(User.email == email).first()
        return self._orm2domain(user) if user else None

    def get_user_by_username(self, username: str) -> Optional[AuthorizedUser]:
        """
        根据用户名获取用户

        Args:
            username: 用户名

        Returns:
            用户数据字典或None
        """
        user = self.db.query(User).filter(User.username == username).first()
        return self._orm2domain(user) if user else None

    def get_user_by_email_or_username(self, email_or_username: str) -> Optional[AuthorizedUser]:
        """
        根据邮箱或用户名获取用户

        Args:
            email_or_username: 邮箱或用户名

        Returns:
            用户领域模型或None
        """
        user = self.db.query(User).filter(
            or_(User.email == email_or_username, User.username == email_or_username)
        ).first()
        return self._orm2domain(user) if user else None

    def get_user_by_student_id(self, student_id: str) -> Optional[AuthorizedUser]:
        """
        根据学号获取用户

        Args:
            student_id: 学号

        Returns:
            用户领域模型或None
        """
        user = self.db.query(User).filter(User.campus_id == student_id).first()
        return self._orm2domain(user) if user else None

    def check_email_exists(self, email: str) -> bool:
        """
        检查邮箱是否存在

        Args:
            email: 邮箱

        Returns:
            是否存在
        """
        user = self.db.query(User).filter(User.email == email).first()
        return user is not None

    def check_username_exists(self, username: str) -> bool:
        """
        检查用户名是否存在

        Args:
            username: 用户名

        Returns:
            是否存在
        """
        user = self.db.query(User).filter(User.username == username).first()
        return user is not None

    def check_student_id_exists(self, student_id: str) -> bool:
        """
        检查学号是否存在

        Args:
            student_id: 学号

        Returns:
            是否存在
        """
        user = self.db.query(User).filter(User.campus_id == student_id).first()
        return user is not None

    def update_user_last_login(self, user_id: int) -> bool:
        """
        更新用户最后登录时间

        Args:
            user_id: 用户ID

        Returns:
            是否成功
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.update_last_login()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            return False

    def _orm2domain(self, user:User) -> Optional[AuthorizedUser]:
        """
        将用户数据转换为领域用户对象

        Args:
            user_data: 用户数据字典

        Returns:
            领域用户对象或None
        """
        if user.userrole == "user": # type: ignore
            return UserFactory.create_registered_user(
                user_id = user.id,# type: ignore
                username = user.username,# type: ignore
                email = user.email,# type: ignore
                nickname = user.nickname,# type: ignore
                password_hash=user.password_hash,# type: ignore
                
                user_type=user.user_type,# type: ignore
                is_active=user.is_active,# type: ignore
                is_verified=user.is_verified,# type: ignore
                
                avatar_url=user.avatar_url,# type: ignore
                bio=user.bio,# type: ignore
                campus_id=user.campus_id,# type: ignore
                last_login=user.last_login_at# type: ignore
            )
        elif user.userrole == "admin":# type: ignore
            return UserFactory.create_admin_user(
                user_id = user.id,# type: ignore
                username = user.username,# type: ignore
                email = user.email,# type: ignore
                password_hash=user.password_hash,# type: ignore
            )
        else:
            return None
        
    def _orm2dict(self, user:User)->dict:
        return {
            "id":user.id,
            "username":user.username,
            "email":user.email,
            "nickname":user.nickname,

            "user_type":user.user_type,
            "userrole":user.userrole,
            "is_active":user.is_active,
            "is_verified":user.is_verified,

            "avatar_url":user.avatar_url,
            "bio":user.bio,
            "campus_id":user.campus_id,
            "last_login_at":user.last_login_at
        }

