"""
用户系统集成示例 - 展示如何在胶囊API中集成用户权限控制

这个文件演示了如何使用新的用户系统来控制胶囊的访问权限。
实际应用中，应该将这些逻辑集成到现有的 capsules.py 中。
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import Optional
from datetime import datetime
from models.core.capsule import Capsule, CapsuleStatus, Visibility
from models.core.user import BaseUser, Permission
from auth.dependencies import AuthenticationDependencies, PermissionChecker
from auth.permission_manager import PermissionManager


router = APIRouter(prefix="/capsules-integrated", tags=["capsules"])


# ============================================================================
# 示例：如何在创建胶囊时关联用户
# ============================================================================

async def create_capsule_with_user(
    title: str,
    content: str,
    visibility: str = "private",
    user: BaseUser = Depends(AuthenticationDependencies.get_current_user)
):
    """
    创建胶囊时自动关联当前用户
    
    特点：
    1. 需要用户有 CREATE_CAPSULE 权限（访客用户无法创建）
    2. 创建的胶囊自动关联当前用户为所有者
    3. 可以根据用户角色设置默认的可见性
    """
    # 1. 权限检查
    if not PermissionManager.can_create_capsule(user):
        raise HTTPException(
            status_code=403,
            detail="您没有权限创建胶囊"
        )
    
    # 2. 创建胶囊对象
    capsule = Capsule(
        capsule_id="caps_" + datetime.now().strftime("%Y%m%d%H%M%S"),
        owner_id=user.user_id,  # 关键：自动设置所有者为当前用户
        title=title,
        content=content,
        visibility=Visibility(visibility),
        status=CapsuleStatus.LOCKED,
        created_at=datetime.now()
    )
    
    # 3. 保存到数据库（TODO: 实现实际逻辑）
    # db.save_capsule(capsule)
    
    return {
        "success": True,
        "message": "胶囊创建成功",
        "capsule_id": capsule.capsule_id,
        "owner_id": capsule.owner_id,
        "created_at": capsule.created_at
    }


# ============================================================================
# 示例：如何在查看胶囊时根据用户权限进行过滤
# ============================================================================

async def get_visible_capsules(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: BaseUser = Depends(AuthenticationDependencies.get_current_user)
):
    """
    获取当前用户可以查看的胶囊列表
    
    特点：
    1. 访客用户只能看到 visibility=CAMPUS 的胶囊
    2. 已登录用户可以看到自己的胶囊、好友的胶囊、公开胶囊
    3. 管理员可以看到所有胶囊
    """
    # 模拟数据库中的所有胶囊
    all_capsules = [
        Capsule(
            capsule_id="caps_1",
            owner_id="user_001",
            title="毕业纪念",
            visibility=Visibility.PRIVATE,
            status=CapsuleStatus.LOCKED
        ),
        Capsule(
            capsule_id="caps_2",
            owner_id="user_002",
            title="校园足球比赛",
            visibility=Visibility.CAMPUS,
            status=CapsuleStatus.LOCKED
        ),
        Capsule(
            capsule_id="caps_3",
            owner_id="user_001",
            title="朋友圈分享",
            visibility=Visibility.FRIENDS,
            status=CapsuleStatus.LOCKED
        ),
    ]
    
    # 过滤出用户可以查看的胶囊
    visible_capsules = []
    is_admin = PermissionManager.is_admin(user)
    
    for capsule in all_capsules:
        if capsule.can_view_by(user.user_id, is_admin=is_admin):
            visible_capsules.append({
                "capsule_id": capsule.capsule_id,
                "title": capsule.title,
                "owner_id": capsule.owner_id,
                "visibility": capsule.visibility.value,
                "status": capsule.status.value,
                "can_edit": capsule.can_edit_by(user.user_id, is_admin=is_admin),
                "can_delete": capsule.can_delete_by(user.user_id, is_admin=is_admin)
            })
    
    return {
        "success": True,
        "total": len(visible_capsules),
        "page": page,
        "limit": limit,
        "capsules": visible_capsules
    }


# ============================================================================
# 示例：如何在编辑胶囊时进行权限检查
# ============================================================================

async def update_capsule_with_permission_check(
    capsule_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    visibility: Optional[str] = None,
    user: BaseUser = Depends(AuthenticationDependencies.get_current_user)
):
    """
    编辑胶囊时进行权限检查
    
    特点：
    1. 只有胶囊所有者和管理员可以编辑
    2. 检查用户是否有 UPDATE_CAPSULE 权限
    3. 防止权限越级修改
    """
    # 模拟从数据库获取胶囊
    # capsule = db.get_capsule(capsule_id)
    
    capsule = Capsule(
        capsule_id=capsule_id,
        owner_id="user_001",  # 假设这是胶囊的所有者
        title="示例胶囊",
        visibility=Visibility.PRIVATE
    )
    
    # 1. 权限检查
    if not PermissionManager.can_update_capsule(user, capsule.owner_id):
        raise HTTPException(
            status_code=403,
            detail="您没有权限编辑这个胶囊"
        )
    
    # 2. 执行更新（通常会在这里修改胶囊属性）
    if title:
        capsule.title = title
    if content:
        capsule.content = content
    if visibility:
        capsule.visibility = Visibility(visibility)
    capsule.updated_at = datetime.now()
    
    # 3. 保存到数据库（TODO: 实现实际逻辑）
    # db.save_capsule(capsule)
    
    return {
        "success": True,
        "message": "胶囊更新成功",
        "capsule_id": capsule.capsule_id,
        "updated_at": capsule.updated_at
    }


# ============================================================================
# 示例：如何在删除胶囊时进行权限检查
# ============================================================================

async def delete_capsule_with_permission_check(
    capsule_id: str,
    user: BaseUser = Depends(AuthenticationDependencies.get_current_user)
):
    """
    删除胶囊时进行权限检查
    
    特点：
    1. 只有胶囊所有者和管理员可以删除
    2. 访客用户无法删除任何胶囊
    3. 审计日志记录删除操作
    """
    # 模拟从数据库获取胶囊
    capsule = Capsule(
        capsule_id=capsule_id,
        owner_id="user_001",
        title="示例胶囊",
        visibility=Visibility.PRIVATE
    )
    
    # 1. 权限检查
    if not PermissionManager.can_delete_capsule(user, capsule.owner_id):
        raise HTTPException(
            status_code=403,
            detail="您没有权限删除这个胶囊"
        )
    
    # 2. 记录审计日志（TODO: 实现实际逻辑）
    # audit_log.record(
    #     action="delete_capsule",
    #     user_id=user.user_id,
    #     capsule_id=capsule_id,
    #     timestamp=datetime.now()
    # )
    
    # 3. 从数据库删除胶囊（TODO: 实现实际逻辑）
    # db.delete_capsule(capsule_id)
    
    return {
        "success": True,
        "message": "胶囊已删除",
        "capsule_id": capsule_id
    }


# ============================================================================
# 示例：如何处理基于可见性的访问控制
# ============================================================================

async def get_capsule_detail_with_visibility_control(
    capsule_id: str,
    user: BaseUser = Depends(AuthenticationDependencies.get_current_user)
):
    """
    获取胶囊详情时根据可见性进行访问控制
    
    可见性规则：
    - PRIVATE: 仅所有者可见
    - FRIENDS: 好友可见 + 所有者
    - CAMPUS: 全校可见
    """
    # 模拟从数据库获取胶囊
    capsule = Capsule(
        capsule_id=capsule_id,
        owner_id="user_001",
        title="毕业纪念",
        visibility=Visibility.FRIENDS,
        status=CapsuleStatus.LOCKED,
        description="校园回忆",
        created_at=datetime.now(),
        like_count=10,
        comment_count=3
    )
    
    # 检查可见性
    is_admin = PermissionManager.is_admin(user)
    if not capsule.can_view_by(user.user_id, is_admin=is_admin):
        raise HTTPException(
            status_code=403,
            detail="您没有权限查看这个胶囊"
        )
    
    # 构建响应（根据用户权限动态包含信息）
    response = {
        "capsule_id": capsule.capsule_id,
        "title": capsule.title,
        "owner_id": capsule.owner_id,
        "description": capsule.description,
        "visibility": capsule.visibility.value,
        "status": capsule.status.value,
        "created_at": capsule.created_at,
        "like_count": capsule.like_count,
        "comment_count": capsule.comment_count,
    }
    
    # 仅所有者和管理员可以看到完整内容
    if capsule.is_owner(user.user_id) or is_admin:
        response["content"] = capsule.content or "点击解锁查看"
        response["can_edit"] = True
        response["can_delete"] = True
    else:
        response["content"] = "[内容已隐藏，需满足解锁条件]"
        response["can_edit"] = False
        response["can_delete"] = False
    
    return {
        "success": True,
        "capsule": response
    }


# ============================================================================
# 示例：如何实现基于角色的内容管理权限
# ============================================================================

async def moderate_capsule(
    capsule_id: str,
    action: str,  # "approve" 或 "reject"
    reason: Optional[str] = None,
    user: BaseUser = Depends(
        PermissionChecker.require_permission(Permission.MODERATE_CONTENT)
    )
):
    """
    审核胶囊内容（仅管理员）
    
    特点：
    1. 需要 MODERATE_CONTENT 权限（仅管理员）
    2. 可以批准或拒绝胶囊
    3. 记录审核日志
    """
    if action not in ["approve", "reject"]:
        raise HTTPException(
            status_code=400,
            detail="无效的操作"
        )
    
    # TODO: 实现实际的审核逻辑
    # 1. 从数据库获取胶囊
    # 2. 更新胶囊状态
    # 3. 记录审核日志
    
    return {
        "success": True,
        "message": f"胶囊已{('批准' if action == 'approve' else '拒绝')}",
        "capsule_id": capsule_id,
        "action": action,
        "reason": reason,
        "reviewed_by": user.user_id,
        "reviewed_at": datetime.now()
    }
