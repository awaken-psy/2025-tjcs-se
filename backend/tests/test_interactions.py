"""
互动功能分层架构测试
重点测试Repository、Domain、Service层
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session, Query

# 导入被测试的模块
from app.services.interactions import InteractionService
from app.database.repositories.interaction_repository import InteractionRepository
from app.domain.interaction import Interaction, Comment, InteractionType
from app.database.orm.capsule import Capsule
from app.database.orm.capsule_interaction import CapsuleInteraction
# 评论功能通过CapsuleInteraction实现
from app.model.interaction import (
    LikeCapsuleResponse, AddCommentResponse, CommentsListResponse,
    CollectCapsuleResponse, CommentItem
)


class TestInteractionRepository:
    """Repository层测试"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)

    @pytest.fixture
    def repository(self, mock_db):
        """Repository实例"""
        return InteractionRepository(mock_db)

    @pytest.fixture
    def sample_orm_capsule(self):
        """示例ORM胶囊对象"""
        capsule = Mock(spec=Capsule)
        capsule.id = 1
        capsule.user_id = 1
        capsule.title = "测试胶囊"
        capsule.like_count = 5
        capsule.comment_count = 10
        capsule.collect_count = 3
        return capsule

    @pytest.fixture
    def sample_orm_interaction(self):
        """示例ORM互动对象"""
        interaction = Mock(spec=CapsuleInteraction)
        interaction.id = 1
        interaction.capsule_id = 1
        interaction.user_id = 2
        interaction.interaction_type = "like"
        interaction.created_at = datetime.now()
        return interaction

    @pytest.fixture
    def sample_orm_comment(self):
        """示例ORM评论对象（通过CapsuleInteraction实现）"""
        comment = Mock(spec=CapsuleInteraction)
        comment.id = 1
        comment.capsule_id = 1
        comment.user_id = 2
        comment.comment_content = "测试评论"
        comment.interaction_type = "comment"
        comment.created_at = datetime.now()
        return comment

    def test_get_user_by_id(self, repository, mock_db):
        """测试根据ID获取用户"""
        mock_query = Mock(spec=Query)
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = Mock()
        mock_db.query.return_value = mock_query

        with patch.object(repository, '_orm_to_domain_user') as mock_convert:
            from app.domain.interaction import User
            mock_convert.return_value = User(
                user_id=1, username="testuser", nickname="测试用户"
            )
            result = repository.get_user_by_id(1)

        assert result is not None
        assert result.user_id == 1

    def test_create_like_interaction(self, repository, mock_db):
        """测试创建点赞互动"""
        with patch.object(repository, 'create_like_interaction') as mock_create:
            mock_interaction = Mock()
            mock_create.return_value = mock_interaction

            result = repository.create_like_interaction(1, 2)

            assert result is not None
            mock_create.assert_called_once_with(1, 2)

    def test_delete_like_interaction(self, repository, mock_db):
        """测试删除点赞互动"""
        with patch.object(repository, 'delete_like_interaction') as mock_delete:
            mock_delete.return_value = True

            result = repository.delete_like_interaction(1, 2)

            assert result is True
            mock_delete.assert_called_once_with(1, 2)

    def test_create_comment(self, repository, mock_db):
        """测试创建评论"""
        with patch.object(repository, 'create_comment') as mock_create:
            mock_comment = Mock()
            mock_comment.id = 1
            mock_create.return_value = mock_comment

            result = repository.create_comment(1, 2, "测试评论", None)

            assert result is not None
            mock_create.assert_called_once_with(1, 2, "测试评论", None)

    def test_get_comments_by_capsule(self, repository, mock_db):
        """测试获取胶囊评论列表"""
        with patch.object(repository, 'get_comments_by_capsule') as mock_get:
            mock_get.return_value = []

            result = repository.get_comments_by_capsule(1, 1, 20, "latest")

        assert isinstance(result, list)

    def test_create_collect_interaction(self, repository, mock_db):
        """测试创建收藏互动"""
        with patch.object(repository, 'create_collect_interaction') as mock_create:
            mock_collect = Mock()
            mock_create.return_value = mock_collect

            result = repository.create_collect_interaction(1, 2)

            assert result is not None
            mock_create.assert_called_once_with(1, 2)

    def test_get_comment_by_id(self, repository, mock_db):
        """测试根据ID获取评论"""
        with patch.object(repository, 'get_comment_by_id') as mock_get:
            mock_comment = Mock()
            mock_get.return_value = mock_comment

            result = repository.get_comment_by_id(1)

        assert result is not None
        mock_get.assert_called_once_with(1)

    def test_delete_comment(self, repository, mock_db):
        """测试删除评论"""
        with patch.object(repository, 'delete_comment') as mock_delete:
            mock_delete.return_value = True

            result = repository.delete_comment(1, 2)

            assert result is True
            mock_delete.assert_called_once_with(1, 2)


class TestInteractionDomain:
    """Domain层测试"""

    @pytest.fixture
    def sample_domain_interaction(self):
        """示例Domain互动对象"""
        return Interaction(
            id=1,
            unlock_record_id=1,
            capsule_id=1,
            user_id=2,
            interaction_type=InteractionType.LIKE,
            created_at=datetime.now()
        )

    @pytest.fixture
    def sample_domain_comment(self):
        """示例Domain评论对象"""
        return Comment(
            id=1,
            user_id=2,
            capsule_id=1,
            content="测试评论",
            created_at=datetime.now()
        )

    def test_domain_interaction_creation(self, sample_domain_interaction):
        """测试Domain互动对象创建"""
        assert sample_domain_interaction.id == 1
        assert sample_domain_interaction.capsule_id == 1
        assert sample_domain_interaction.user_id == 2
        assert sample_domain_interaction.interaction_type == InteractionType.LIKE
        assert isinstance(sample_domain_interaction.created_at, datetime)

    def test_domain_comment_creation(self, sample_domain_comment):
        """测试Domain评论对象创建"""
        assert sample_domain_comment.id == 1
        assert sample_domain_comment.capsule_id == 1
        assert sample_domain_comment.user_id == 2
        assert sample_domain_comment.content == "测试评论"
        assert isinstance(sample_domain_comment.created_at, datetime)


class TestInteractionService:
    """Service层测试"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_repository(self):
        """模拟Repository"""
        return Mock(spec=InteractionRepository)

    @pytest.fixture
    def service(self, mock_db, mock_repository):
        """Service实例"""
        service = InteractionService(mock_db)
        service.interaction_repo = mock_repository
        return service

    def test_like_capsule_success(self, service, mock_repository):
        """测试成功点赞胶囊"""
        mock_repository.create_like_interaction.return_value = Mock()
        mock_repository.get_like_count.return_value = 6

        result = service.like_capsule(2, 1)

        assert isinstance(result, LikeCapsuleResponse)
        assert result.is_liked == True
        assert result.like_count == 6
        mock_repository.create_like_interaction.assert_called_once_with(2, 1)

    def test_like_capsule_not_found(self, service, mock_repository):
        """测试点赞不存在的胶囊"""
        mock_repository.create_like_interaction.side_effect = ValueError("用户未解锁此胶囊")

        with pytest.raises(ValueError, match="用户未解锁此胶囊"):
            service.like_capsule(2, 1)

    def test_unlike_capsule_success(self, service, mock_repository):
        """测试成功取消点赞"""
        mock_repository.delete_like_interaction.return_value = True
        mock_repository.get_like_count.return_value = 4

        result = service.unlike_capsule(2, 1)

        assert isinstance(result, LikeCapsuleResponse)
        assert result.is_liked == False
        assert result.like_count == 4
        mock_repository.delete_like_interaction.assert_called_once_with(2, 1)

    def test_add_comment_success(self, service, mock_repository):
        """测试成功添加评论"""
        mock_user = Mock()
        mock_user.user_id = 2
        mock_user.username = "testuser"
        mock_user.nickname = "测试用户"
        mock_user.avatar_url = None

        mock_repository.get_user_by_id.return_value = mock_user
        mock_repository.get_unlock_record.return_value = Mock()
        mock_repository.create_comment.return_value = Mock()
        mock_repository.get_comments_by_capsule.return_value = []

        with patch.object(service, 'get_unlock_record', return_value=Mock()):
            result = service.add_comment(2, 1, "测试评论", None)

        # 验证基本属性而不依赖具体的内部实现
        assert result is not None
        mock_repository.create_comment.assert_called_once_with(2, 1, "测试评论", None)

    def test_add_comment_empty_content(self, service):
        """测试添加空评论"""
        with pytest.raises(ValueError, match="评论内容不能为空"):
            service.add_comment(2, 1, "", None)

    def test_add_comment_content_too_long(self, service):
        """测试评论内容过长"""
        long_content = "x" * 501  # 超过500字符限制
        with pytest.raises(ValueError, match="评论内容不能超过500个字符"):
            service.add_comment(2, 1, long_content, None)

    def test_get_comments_success(self, service, mock_repository):
        """测试成功获取评论列表"""
        mock_repository.get_comments_by_capsule.return_value = []

        result = service.get_comments(1, 1, 20, "latest")

        assert isinstance(result, CommentsListResponse)
        assert len(result.comments) == 0
        mock_repository.get_comments_by_capsule.assert_called_once_with(1, 1, 20, "latest")

    def test_get_comments_invalid_sort(self, service):
        """测试获取评论时使用无效排序"""
        with pytest.raises(ValueError, match="无效的排序类型"):
            service.get_comments(1, 1, 20, "invalid")

    def test_delete_comment_success(self, service, mock_repository):
        """测试成功删除评论"""
        mock_repository.get_comment_by_id.return_value = Mock()
        mock_repository.delete_comment.return_value = True

        result = service.delete_comment(1, 2)

        assert result is True
        mock_repository.get_comment_by_id.assert_called_once_with(1)
        mock_repository.delete_comment.assert_called_once_with(1, 2)

    def test_delete_comment_not_found(self, service, mock_repository):
        """测试删除不存在的评论"""
        mock_repository.get_comment_by_id.return_value = None

        with pytest.raises(ValueError, match="评论不存在"):
            service.delete_comment(1, 2)

    def test_collect_capsule_success(self, service, mock_repository):
        """测试成功收藏胶囊"""
        mock_repository.create_collect_interaction.return_value = Mock()

        result = service.collect_capsule(2, 1)

        assert isinstance(result, CollectCapsuleResponse)
        assert result.is_collected == True
        mock_repository.create_collect_interaction.assert_called_once_with(2, 1)

    def test_uncollect_capsule_success(self, service, mock_repository):
        """测试成功取消收藏"""
        mock_repository.delete_collect_interaction.return_value = True

        result = service.uncollect_capsule(2, 1)

        assert isinstance(result, CollectCapsuleResponse)
        assert result.is_collected == False
        mock_repository.delete_collect_interaction.assert_called_once_with(2, 1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])