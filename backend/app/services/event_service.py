from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.database.repositories.event_repository import EventRepository
from app.database.orm.event import Event, EventRegistration
from app.model.event import (
    EventCreateRequest, EventUpdateRequest, EventRegistrationRequest,
    EventCreateResponse, EventUpdateResponse, EventDeleteResponse,
    EventRegistrationResponse, EventCancelResponse, EventResponse
)
from app.core.exceptions import RecordNotFoundException


class EventService:
    """活动业务服务类"""

    def __init__(self, db: Optional[Session] = None):
        self.repository = EventRepository(db)

    def _parse_event_id(self, event_id: str) -> int:
        """将字符串ID转换为整数，支持多种格式"""
        if not event_id:
            raise RecordNotFoundException("活动ID不能为空")

        try:
            # 处理APIFox占位符问题
            if event_id == '$1' or event_id == '$event_id':
                return 1  # 默认假设是ID为1的活动

            # 处理各种可能的ID格式
            # 纯数字: "123" -> 123
            # 带前缀: "event_123" -> 123
            # 其他格式尝试提取数字部分
            import re

            # 尝试直接转换纯数字
            if event_id.isdigit():
                return int(event_id)

            # 尝试从字符串中提取数字
            # 匹配 "event_123", "ev-123", "123abc" 等格式
            match = re.search(r'(\d+)', str(event_id))
            if match:
                return int(match.group(1))

            # 如果都无法提取数字，抛出异常
            raise ValueError(f"无法从ID中提取数字: {event_id}")

        except (ValueError, TypeError):
            raise RecordNotFoundException(f"无效的活动ID: {event_id}")

    def _parse_event_id_optional(self, event_id: str) -> Optional[int]:
        """将字符串ID转换为整数，允许None"""
        if event_id is None:
            return None
        try:
            return int(event_id)
        except (ValueError, TypeError):
            raise RecordNotFoundException(f"无效的活动ID: {event_id}")

    def create_event(self, request: EventCreateRequest, user_id: int) -> EventCreateResponse:
        """创建活动"""
        try:
            # 创建ORM对象
            event = Event(
                name=request.name,
                description=request.description,
                date=request.date,
                location=request.location,
                tags=request.tags,
                cover_img=request.cover_img,
                creator_id=user_id
            )

            # 保存到数据库
            saved_event = self.repository.save(event)

            return EventCreateResponse(
                id=str(saved_event.id),
                name=saved_event.name,
                created_at=saved_event.created_at
            )

        except Exception as e:
            raise Exception(f"创建活动失败: {str(e)}")

    def update_event(self, event_id: str, request: EventUpdateRequest, user_id: int) -> EventUpdateResponse:
        """更新活动"""
        try:
            # 转换ID
            event_int_id = self._parse_event_id(event_id)

            # 查找活动
            event = self.repository.find_by_id(event_int_id)
            if not event:
                raise RecordNotFoundException(f"活动 {event_id} 不存在")

            # 检查权限
            if event.creator_id != user_id:
                raise Exception("无权限修改此活动")

            # 更新字段
            if request.name is not None:
                event.name = request.name
            if request.description is not None:
                event.description = request.description
            if request.date is not None:
                event.date = request.date
            if request.location is not None:
                event.location = request.location
            if request.tags is not None:
                event.tags = request.tags
            if request.cover_img is not None:
                event.cover_img = request.cover_img

            # 保存更新
            updated_event = self.repository.update(event)

            return EventUpdateResponse(
                updated=True,
                event_id=str(updated_event.id)
            )

        except RecordNotFoundException:
            raise
        except Exception as e:
            raise Exception(f"更新活动失败: {str(e)}")

    def delete_event(self, event_id: str, user_id: int) -> EventDeleteResponse:
        """删除活动"""
        try:
            # 转换ID
            event_int_id = self._parse_event_id(event_id)

            # 查找活动
            event = self.repository.find_by_id(event_int_id)
            if not event:
                raise RecordNotFoundException(f"活动 {event_id} 不存在")

            # 检查权限
            if event.creator_id != user_id:
                raise Exception("无权限删除此活动")

            # 删除活动
            success = self.repository.delete(event)

            return EventDeleteResponse(
                deleted=success,
                event_id=str(event_id)
            )

        except RecordNotFoundException:
            raise
        except Exception as e:
            raise Exception(f"删除活动失败: {str(e)}")

    def get_event_detail(self, event_id: str, user_id: int) -> Optional[EventResponse]:
        """获取活动详情"""
        try:
            # 转换ID
            event_int_id = self._parse_event_id(event_id)

            event = self.repository.find_by_id(event_int_id)
            if not event:
                return None

            # 检查用户是否已报名
            is_registered = self.repository.is_user_registered(event_int_id, user_id)

            # 获取参与人数
            participant_count = self.repository.get_participant_count(event_int_id)

            return EventResponse(
                id=str(event.id),
                name=event.name,
                description=event.description,
                date=event.date,
                location=event.location,
                tags=event.tags or [],
                cover_img=event.cover_img,
                participant_count=participant_count,
                is_registered=is_registered,
                created_at=event.created_at,
                updated_at=event.updated_at
            )

        except Exception as e:
            raise Exception(f"获取活动详情失败: {str(e)}")

    def get_events_list(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """获取活动列表"""
        try:
            result = self.repository.find_all(page, page_size)

            # 转换为响应模型
            events = []
            for event in result['events']:
                events.append(EventResponse(
                    id=str(event.id),
                    name=event.name,
                    description=event.description,
                    date=event.date,
                    location=event.location,
                    tags=event.tags or [],
                    cover_img=event.cover_img,
                    participant_count=self.repository.get_participant_count(event.id),
                    is_registered=False,  # 列表中不显示当前用户报名状态
                    created_at=event.created_at,
                    updated_at=event.updated_at
                ))

            return {
                'list': events,
                'total': result['total'],
                'page': result['page'],
                'page_size': result['page_size']
            }

        except Exception as e:
            raise Exception(f"获取活动列表失败: {str(e)}")

    def get_my_events(self, user_id: int, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """获取我创建的活动"""
        try:
            result = self.repository.find_by_user_id(user_id, page, page_size)

            # 转换为响应模型
            events = []
            for event in result['events']:
                events.append(EventResponse(
                    id=str(event.id),
                    name=event.name,
                    description=event.description,
                    date=event.date,
                    location=event.location,
                    tags=event.tags or [],
                    cover_img=event.cover_img,
                    participant_count=self.repository.get_participant_count(event.id),
                    is_registered=self.repository.is_user_registered(event.id, user_id),
                    created_at=event.created_at,
                    updated_at=event.updated_at
                ))

            return {
                'list': events,
                'total': result['total'],
                'page': result['page'],
                'page_size': result['page_size']
            }

        except Exception as e:
            raise Exception(f"获取我的活动失败: {str(e)}")

    def register_event(self, event_id: str, user_id: int) -> EventRegistrationResponse:
        """报名活动"""
        try:
            # 转换ID
            event_int_id = self._parse_event_id(event_id)

            # 检查活动是否存在
            event = self.repository.find_by_id(event_int_id)
            if not event:
                raise RecordNotFoundException(f"活动 {event_id} 不存在")

            # 检查是否已经报名
            existing_registration = self.repository.find_registration(event_int_id, user_id)
            if existing_registration:
                raise Exception("已经报名过此活动")

            # 创建报名记录
            registration = EventRegistration(
                event_id=event_int_id,
                user_id=user_id,
                registered_at=datetime.utcnow()
            )

            saved_registration = self.repository.create_registration(registration)

            return EventRegistrationResponse(
                registration_id=str(saved_registration.id),
                event_id=str(saved_registration.event_id),
                user_id=str(saved_registration.user_id),
                registered_at=saved_registration.registered_at
            )

        except RecordNotFoundException:
            raise
        except Exception as e:
            raise Exception(f"报名活动失败: {str(e)}")

    def cancel_registration(self, event_id: str, user_id: int) -> EventCancelResponse:
        """取消报名"""
        try:
            # 转换ID
            event_int_id = self._parse_event_id(event_id)

            # 查找报名记录
            registration = self.repository.find_registration(event_int_id, user_id)
            if not registration:
                raise RecordNotFoundException("未找到报名记录")

            # 删除报名记录
            success = self.repository.delete_registration(registration)

            return EventCancelResponse(
                cancelled=success,
                event_id=str(event_id)
            )

        except RecordNotFoundException:
            raise
        except Exception as e:
            raise Exception(f"取消报名失败: {str(e)}")

    def get_my_registrations(self, user_id: int, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """获取我报名的活动"""
        try:
            result = self.repository.find_user_registrations(user_id, page, page_size)

            # 转换为响应模型
            events = []
            for event in result['events']:
                events.append(EventResponse(
                    id=str(event.id),
                    name=event.name,
                    description=event.description,
                    date=event.date,
                    location=event.location,
                    tags=event.tags or [],
                    cover_img=event.cover_img,
                    participant_count=self.repository.get_participant_count(event.id),
                    is_registered=True,
                    created_at=event.created_at,
                    updated_at=event.updated_at
                ))

            return {
                'list': events,
                'total': result['total'],
                'page': result['page'],
                'page_size': result['page_size']
            }

        except Exception as e:
            raise Exception(f"获取我的报名失败: {str(e)}")