"""
Admin Repository - 处理管理员相关的数据访问
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from typing import Optional, Dict, Any, List

from app.database.orm.capsule import Capsule
from app.database.orm.user import User
from app.database.database import get_db
from app.core.exceptions import RecordNotFoundException


class AdminRepository:
    """管理员数据访问层"""

    def __init__(self, db: Optional[Session] = None):
        try:
            if db is not None:
                self.db = db
            else:
                self.db = next(get_db())
        except Exception as e:
            raise Exception(f"数据库连接失败: {str(e)}")

    def get_pending_capsules(
        self,
        page: int = 1,
        page_size: int = 20,
        sort: str = "latest"
    ) -> Dict[str, Any]:
        """获取待审核胶囊列表"""
        offset = (page - 1) * page_size

        # 基础查询 - 获取被举报的胶囊
        query = self.db.query(
            Capsule,
            User.nickname.label('creator_nickname'),
            func.count(func.nullif(Capsule.id, None)).label('report_count')
        ).join(
            User, Capsule.user_id == User.id
        ).filter(
            # 查询待审核的胶囊
            Capsule.status.in_(['pending', 'pending_review', 'reported'])
        ).group_by(Capsule.id, User.nickname)

        # 排序
        if sort == "latest":
            query = query.order_by(desc(Capsule.created_at))
        elif sort == "oldest":
            query = query.order_by(asc(Capsule.created_at))
        elif sort == "most_reported":
            query = query.order_by(desc('report_count'))

        # 分页
        total = query.count()
        capsules = query.offset(offset).limit(page_size).all()

        # 转换结果
        pending_capsules = []
        for capsule, creator_nickname, report_count in capsules:
            pending_capsules.append({
                "id": str(capsule.id),
                "title": capsule.title,
                "creator_nickname": creator_nickname,
                "created_at": capsule.created_at,
                "report_count": report_count,
                "content_preview": capsule.text_content[:100] + "..." if capsule.text_content else None
            })

        return {
            "capsules": pending_capsules,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def get_reports(
        self,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        target_type: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取举报列表"""
        offset = (page - 1) * page_size

        # 这里假设有一个 report 表，需要根据实际表结构调整
        # 临时返回示例数据，需要根据实际数据库结构调整
        from app.database.orm import unlock_attempts, capsule_interactions

        query = self.db.query(
            # 这里的字段需要根据实际的 report 表调整
        )

        # 添加筛选条件
        if status:
            query = query.filter(status == status)
        if target_type:
            query = query.filter(target_type == target_type)
        if reason:
            query = query.filter(reason == reason)

        # 分页
        total = query.count()
        reports = query.offset(offset).limit(page_size).all()

        # 这里需要根据实际的 report 结构转换数据
        reports_data = []

        return {
            "reports": reports_data,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def review_capsule(self, capsule_id: str, action: str, reason: Optional[str] = None) -> bool:
        """审核胶囊"""
        capsule = self.db.query(Capsule).filter(Capsule.id == int(capsule_id)).first()
        if not capsule:
            raise RecordNotFoundException(f"胶囊 {capsule_id} 不存在")

        if action == "approve":
            capsule.status = "approved"
        elif action == "reject":
            capsule.status = "rejected"
            # 这里可以添加拒绝原因的存储逻辑
        else:
            raise ValueError(f"无效的审核动作: {action}")

        self.db.commit()
        return True

    def resolve_report(self, report_id: str) -> bool:
        """处理举报"""
        # 这里需要根据实际的 report 表结构调整
        # 临时实现
        return True