from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Dict, Any
from datetime import datetime
import math

from app.database.orm.capsule import Capsule
from app.database.orm.unlock_record import UnlockRecord, UnlockAttempt
from app.database.orm.unlock_condition import UnlockCondition
from app.database.repositories.capsule_repository import CapsuleRepository
from app.domain.capsule import Capsule as CapsuleDomain


class UnlockManager:
    """胶囊解锁业务管理类"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = CapsuleRepository(db)

    def get_nearby_capsules(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int = 1000,
        user_id: Optional[int] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        获取附近的胶囊
        """
        try:
            # 计算边界框（简化查询）
            lat_delta = radius_meters / 111000
            lon_delta = radius_meters / (111000 * math.cos(math.radians(latitude)))

            min_lat = latitude - lat_delta
            max_lat = latitude + lat_delta
            min_lon = longitude - lon_delta
            max_lon = longitude + lon_delta

            # 查询附近区域内的胶囊
            query = self.db.query(Capsule).filter(
                and_(
                    Capsule.latitude >= min_lat,
                    Capsule.latitude <= max_lat,
                    Capsule.longitude >= min_lon,
                    Capsule.longitude <= max_lon,
                    Capsule.visibility.in_(['public', 'campus'])  # 只获取可见的胶囊
                )
            )

            # 🔥 修改：允许用户搜索到自己的胶囊，不再排除自己的胶囊
            # if user_id:
            #     # 排除用户自己的胶囊
            #     query = query.filter(Capsule.user_id != user_id)

            total = query.count()

            offset = (page - 1) * limit
            capsules = query.order_by(Capsule.created_at.desc()).offset(offset).limit(limit).all()

            nearby_capsules = []
            for capsule in capsules:
                # 计算实际距离
                capsule_lat = getattr(capsule, 'latitude', 0.0)
                capsule_lon = getattr(capsule, 'longitude', 0.0)
                distance = self.calculate_distance(
                    latitude, longitude,
                    float(capsule_lat), float(capsule_lon)
                )

                if distance <= radius_meters:
                    # 通过Repository转换为Domain对象
                    domain = self.repository._orm_to_domain(capsule)

                    if domain and (user_id is None or self._can_user_view_capsule(user_id, domain)):
                        # 使用Domain的to_api_basic方法转换为API模型
                        api_basic = domain.to_api_basic()

                        # 转换为字典
                        capsule_dict = api_basic.model_dump() if hasattr(api_basic, 'model_dump') else api_basic.model_dump()

                        # 确保位置信息存在（to_api_basic已经处理了位置转换）
                        if capsule_dict.get('latitude') is None or capsule_dict.get('longitude') is None:
                            # 如果Domain对象转换后仍然没有位置信息，从ORM对象直接获取
                            capsule_dict['latitude'] = getattr(capsule, 'latitude', 0.0)
                            capsule_dict['longitude'] = getattr(capsule, 'longitude', 0.0)

                        nearby_capsules.append({
                            'domain': domain,  # 直接返回Domain对象
                            'capsule': capsule_dict,
                            'distance': round(distance, 2),
                            'unlockable': self._can_user_unlock_capsule(user_id, domain, (latitude, longitude)) if user_id is not None else False
                        })
                    else:
                        continue

            # 按距离排序
            nearby_capsules.sort(key=lambda x: x['distance'])

            return {
                'success': True,
                'message': f"找到 {len(nearby_capsules)} 个附近胶囊",
                'capsules': nearby_capsules,
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit,
                'search_center': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'radius': radius_meters
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': f"获取附近胶囊失败: {str(e)}",
                'capsules': []
            }

    def unlock_capsule(
        self,
        user_id: int,
        capsule_id: str,
        user_latitude: Optional[float] = None,
        user_longitude: Optional[float] = None,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        解锁胶囊
        """
        try:
            # 通过Repository获取Domain对象
            domain = self.repository.find_by_id(int(capsule_id))
            if not domain:
                return {
                    'success': False,
                    'message': f"胶囊 {capsule_id} 不存在"
                }

            # 获取解锁条件
            unlock_condition = self.db.query(UnlockCondition).filter(
                UnlockCondition.capsule_id == int(capsule_id)
            ).first()

            # 检查用户是否已解锁
            if self.has_user_unlocked_capsule(user_id, capsule_id):
                return {
                    'success': True,
                    'message': '您已经解锁过这个胶囊',
                    'already_unlocked': True,
                    'capsule_id': capsule_id
                }

            # 检查解锁条件
            unlock_result = self.check_unlock_conditions(
                domain, user_id, (user_latitude, user_longitude), password
            )

            if not unlock_result['can_unlock']:
                return {
                    'success': False,
                    'message': unlock_result['message'],
                    'failed_conditions': unlock_result['failed_conditions']
                }

            # 执行解锁 - 更新Domain对象
            domain.mark_unlocked_by(str(user_id))
            self.repository.save(domain)

            # 记录解锁历史
            self._record_unlock_history(user_id, capsule_id, unlock_result['unlock_method'],
                                      user_latitude, user_longitude)

            # 更新解锁条件记录，标记为已解锁
            self._update_unlock_condition_record(capsule_id, unlock_result)

            # 使用Domain的to_api_detail方法获取详细信息
            capsule_detail = domain.to_api_detail(None)  # 这里需要传入user对象，暂时用None

            return {
                'success': True,
                'message': '解锁成功',
                'capsule_id': capsule_id,
                'unlocked_at': datetime.now().isoformat(),
                'capsule_detail': capsule_detail.model_dump() if hasattr(capsule_detail, 'model_dump') else capsule_detail,
                'unlock_method': unlock_result['unlock_method'],
                'conditions_met': unlock_result['conditions_met']
            }

        except Exception as e:
            self.db.rollback()
            return {
                'success': False,
                'message': f"解锁胶囊失败: {str(e)}"
            }

    def check_unlock_conditions(
        self,
        domain: CapsuleDomain,
        user_id: int,
        user_location: Optional[tuple] = None,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        检查解锁条件（使用Domain对象）
        """
        failed_conditions = []
        conditions_met = []
        unlock_method = 'manual'

        # 获取解锁条件
        unlock_condition = self.db.query(UnlockCondition).filter(
            UnlockCondition.capsule_id == domain.capsule_id
        ).first()

        # 如果没有解锁条件，默认为private类型
        if not unlock_condition:
            unlock_condition = UnlockCondition(
                capsule_id=domain.capsule_id,
                condition_type='private'
            )

        # 初始化条件检查结果
        time_condition_met = False
        location_condition_met = False
        distance_to_trigger = None
        failure_reason = None

        # 1. 检查权限
        if not domain.can_view_by(str(user_id)):
            # 记录权限失败的尝试
            self._record_unlock_attempt(
                capsule_id=str(domain.capsule_id) if domain.capsule_id is not None else None,
                user_id=user_id,
                user_location=user_location,
                time_condition_met=False,
                location_condition_met=False,
                all_conditions_met=False,
                failure_reason='权限不足'
            )
            return {
                'can_unlock': False,
                'message': '您没有权限访问这个胶囊',
                'failed_conditions': ['权限不足']
            }

        # 2. 检查是否已解锁
        if domain.is_unlocked_by(str(user_id)):
            return {
                'can_unlock': True,
                'message': '您已经解锁过这个胶囊',
                'already_unlocked': True
            }

        # 3. 根据解锁条件类型进行检查
        condition_type = getattr(unlock_condition, 'condition_type', 'private')

        if condition_type == 'private':
            # Private类型：只有创建者可以解锁
            if str(domain.owner_id) == str(user_id):
                conditions_met.append('私有胶囊 - 创建者权限满足')
                time_condition_met = True
                location_condition_met = True
                unlock_method = 'private'
            else:
                failed_conditions.append('私有胶囊 - 非创建者无权解锁')
                failure_reason = '您不是此胶囊的创建者'

        elif condition_type == 'public':
            # Public类型：所有人都可以解锁
            conditions_met.append('公开胶囊 - 所有人可解锁')
            time_condition_met = True
            location_condition_met = True
            unlock_method = 'public'

        elif condition_type == 'password':
            # Password类型：需要密码验证
            stored_password = getattr(unlock_condition, 'password', None)
            if password and stored_password and password == stored_password:
                conditions_met.append('密码胶囊 - 密码验证通过')
                time_condition_met = True
                location_condition_met = True
                unlock_method = 'password'
            else:
                failed_conditions.append('密码胶囊 - 密码错误或未提供密码')
                failure_reason = '密码错误或未提供密码'
                # 如果没有密码或密码错误，不允许解锁

        # 4. 检查时间条件（如果有）
        unlockable_time = getattr(unlock_condition, 'unlockable_time', None)
        if unlockable_time is not None:
            if datetime.now() >= unlockable_time:
                conditions_met.append(f'时间条件满足 (解锁时间: {unlockable_time})')
                time_condition_met = True
            else:
                failed_conditions.append(f'时间未到 (解锁时间: {unlockable_time})')
                time_condition_met = False
                if not failure_reason:
                    failure_reason = f'时间未到 (解锁时间: {unlockable_time})'

        # 5. 检查位置条件（如果有）
        trigger_lat = getattr(unlock_condition, 'trigger_latitude', None)
        trigger_lng = getattr(unlock_condition, 'trigger_longitude', None)

        if trigger_lat is not None and trigger_lng is not None and user_location:
            distance = self.calculate_distance(
                user_location[0], user_location[1],
                float(trigger_lat), float(trigger_lng)
            )
            distance_to_trigger = distance
            radius_meters = getattr(unlock_condition, 'radius_meters', 100) or 100
            if distance <= radius_meters:
                conditions_met.append(f'位置条件满足 (距离: {round(distance, 2)}m)')
                location_condition_met = True
                if unlock_method == 'manual':
                    unlock_method = 'location'
            else:
                failed_conditions.append(f'距离过远 ({round(distance, 2)}m > {radius_meters}m)')
                location_condition_met = False
                if not failure_reason:
                    failure_reason = f'距离过远 ({round(distance, 2)}m)'
            unlock_method = 'manual'

        can_unlock = len(failed_conditions) == 0

        # 记录解锁尝试
        self._record_unlock_attempt(
            capsule_id=str(domain.capsule_id) if domain.capsule_id is not None else None,
            user_id=user_id,
            user_location=user_location,
            time_condition_met=time_condition_met,
            location_condition_met=location_condition_met,
            all_conditions_met=can_unlock,
            distance_to_trigger=distance_to_trigger,
            failure_reason=failure_reason if not can_unlock else None
        )

        return {
            'can_unlock': can_unlock,
            'message': '可以解锁' if can_unlock else f'解锁条件不满足: {", ".join(failed_conditions)}',
            'failed_conditions': failed_conditions,
            'conditions_met': conditions_met,
            'unlock_method': unlock_method
        }

    def has_user_unlocked_capsule(self, user_id: int, capsule_id: str) -> bool:
        """
        检查用户是否已解锁胶囊
        """
        unlock_record = self.db.query(UnlockRecord).filter(
            and_(
                UnlockRecord.capsule_id == capsule_id,
                UnlockRecord.user_id == user_id
            )
        ).first()
        return unlock_record is not None

    def _can_user_view_capsule(self, user_id: int, domain: CapsuleDomain) -> bool:
        """
        检查用户是否可以查看胶囊
        """
        if not user_id:
            return domain.visibility.value in ['public', 'campus']
        return domain.can_view_by(str(user_id))

    def _can_user_unlock_capsule(self, user_id: int, domain: CapsuleDomain, user_location: Optional[tuple] = None) -> bool:
        """
        检查用户是否可以解锁胶囊
        """
        if not domain.can_view_by(str(user_id)):
            return False

        if domain.is_unlocked_by(str(user_id)):
            return True

        # 检查位置条件
        if domain.unlock_location and user_location:
            distance = self.calculate_distance(
                user_location[0], user_location[1],
                domain.unlock_location[0], domain.unlock_location[1]
            )
            return distance <= domain.unlock_radius

        return True

    def _record_unlock_attempt(
        self,
        capsule_id: Optional[str],
        user_id: int,
        user_location: Optional[tuple] = None,
        time_condition_met: bool = False,
        location_condition_met: bool = False,
        all_conditions_met: bool = False,
        distance_to_trigger: Optional[float] = None,
        failure_reason: Optional[str] = None
    ):
        """
        记录解锁尝试
        """
        if capsule_id is None:
            return  # 如果胶囊ID为空，不记录

        try:
            unlock_attempt = UnlockAttempt(
                capsule_id=int(capsule_id),  # 转换为整数类型
                user_id=user_id,
                attempt_location_latitude=user_location[0] if user_location else None,
                attempt_location_longitude=user_location[1] if user_location else None,
                attempt_time=datetime.now(),
                time_condition_met=time_condition_met,
                location_condition_met=location_condition_met,
                all_conditions_met=all_conditions_met,
                distance_to_trigger=distance_to_trigger,
                failure_reason=failure_reason
            )
            self.db.add(unlock_attempt)
            self.db.commit()
        except Exception as e:
            # 记录失败不应该影响主流程
            print(f"记录解锁尝试失败: {str(e)}")
            self.db.rollback()

    def _record_unlock_history(self, user_id: int, capsule_id: str, unlock_method: str,
                              latitude: Optional[float] = None, longitude: Optional[float] = None):
        """
        记录解锁历史
        """
        if capsule_id is None:
            return  # 如果胶囊ID为空，不记录

        try:
            unlock_record = UnlockRecord(
                capsule_id=int(capsule_id),  # 转换为整数类型
                user_id=user_id,
                unlock_method=unlock_method,
                unlock_location_latitude=latitude,
                unlock_location_longitude=longitude,
                unlocked_at=datetime.now()
            )
            self.db.add(unlock_record)
            self.db.commit()
        except Exception as e:
            # 记录失败不应该影响主流程
            print(f"记录解锁历史失败: {str(e)}")
            self.db.rollback()

    def _update_unlock_condition_record(self, capsule_id: str, unlock_result: Dict[str, Any]):
        """
        更新解锁条件记录，标记胶囊已解锁
        """
        if capsule_id is None:
            return

        try:
            # 查找现有的解锁条件记录
            unlock_condition = self.db.query(UnlockCondition).filter(
                UnlockCondition.capsule_id == int(capsule_id)
            ).first()

            if unlock_condition:
                # 更新现有记录
                # 注意：updated_at 是一个 Column 对象，不能直接赋值
                # 可以使用 SQL 更新语句或者让数据库自动更新（如果有 onupdate）
                # 如果是时间解锁，记录解锁时间（如果存在 unlock_time 字段）
                if unlock_result.get('unlock_method') == 'time' and hasattr(unlock_condition, 'unlock_time'):
                    # unlock_condition.unlock_time = datetime.now()
                    pass  # 暂时跳过，因为字段可能不存在
                # 可以根据需要添加其他更新逻辑
            else:
                # 创建新的解锁条件记录（理论上不应该发生，因为创建胶囊时应该已有记录）
                unlock_condition = UnlockCondition(
                    capsule_id=int(capsule_id),
                    condition_type=unlock_result.get('unlock_method', 'manual'),
                    created_at=datetime.now()
                )
                self.db.add(unlock_condition)

            self.db.commit()
        except Exception as e:
            # 记录失败不应该影响主流程
            print(f"更新解锁条件记录失败: {str(e)}")
            self.db.rollback()

    def get_user_unlock_history(self, user_id: int, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        获取用户解锁历史
        """
        try:
            query = self.db.query(UnlockRecord).filter(
                UnlockRecord.user_id == user_id
            ).order_by(UnlockRecord.unlocked_at.desc())

            total = query.count()
            offset = (page - 1) * limit
            records = query.offset(offset).limit(limit).all()

            unlock_history = []
            for record in records:
                # 通过Repository获取胶囊信息
                capsule_id = getattr(record, 'capsule_id', None)
                domain = None
                if capsule_id is not None:
                    domain = self.repository.find_by_id(int(capsule_id))
                if domain:
                    api_basic = domain.to_api_basic()
                    unlock_history.append({
                        'id': record.id,
                        'capsule': api_basic.model_dump() if hasattr(api_basic, 'model_dump') else api_basic,
                        'unlock_method': record.unlock_method,
                        'unlock_location': {
                            'latitude': record.unlock_location_latitude,
                            'longitude': record.unlock_location_longitude
                        } if record.unlock_location_latitude is not None and record.unlock_location_longitude is not None else None,
                        'unlocked_at': record.unlocked_at.isoformat()
                    })

            return {
                'success': True,
                'records': unlock_history,
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit
            }

        except Exception as e:
            return {
                'success': False,
                'message': f"获取解锁历史失败: {str(e)}",
                'records': []
            }

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        使用Haversine公式计算两点间距离（米）
        """
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
            return float('inf')

        R = 6371000  # 地球半径（米）

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat/2)**2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c

    # 保留向后兼容的方法
    def check_unlockable_capsules(self, user_id: int, user_latitude: float, user_longitude: float,
                                 max_distance_meters: int = 1000, current_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        向后兼容的方法
        """
        result = self.get_nearby_capsules(user_latitude, user_longitude, max_distance_meters, user_id)

        # 转换格式以保持兼容性
        unlockable_capsules = []
        for item in result.get('capsules', []):
            if item.get('unlockable', False):
                unlockable_capsules.append({
                    'capsule_id': item['capsule'].get('id'),
                    'title': item['capsule'].get('title'),
                    'created_at': item['capsule'].get('created_at'),
                    'distance': item['distance'],
                    'unlock_method': 'position'
                })

        return {
            'success': result['success'],
            'message': result['message'],
            'unlockable_capsules': unlockable_capsules,
            'total_capsules_found': result['total'],
            'unlockable_count': len(unlockable_capsules),
            'user_location': {
                'latitude': user_latitude,
                'longitude': user_longitude,
                'address': '用户当前位置'
            },
            'check_time': current_time.isoformat() if current_time else datetime.now().isoformat()
        }

    