<template>
  <!-- 胶囊卡片：展示胶囊基础信息，支持网格/列表两种视图 -->
  <div 
    class="capsule-card"
    :class="{ 'list-mode': viewMode === 'list' }"
    @click="handleCardClick"
  >
    <!-- 卡片缩略图区域 -->
    <div
      v-if="viewMode === 'grid'"
      class="capsule-thumb"
    >
      <img 
        v-if="capsule.cover_image" 
        :src="capsule.cover_image" 
        :alt="capsule.title"
        class="thumb-img"
      >
      <div
        v-else
        class="thumb-placeholder"
      >
        {{ getVisibilityIcon(capsule.visibility) }}
      </div>
      <!-- 可见性标签 -->
      <div class="capsule-visibility">
        {{ getVisibilityText(capsule.visibility) }}
      </div>
    </div>

    <!-- 卡片内容区域 -->
    <div class="capsule-body">
      <!-- 标题 -->
      <h3 class="capsule-title">
        {{ capsule.title }}
        <span
          v-if="viewMode === 'list'"
          class="visibility-icon"
        >
          {{ getVisibilityIcon(capsule.visibility) }}
        </span>
      </h3>

      <!-- 元信息（时间、状态） -->
      <div class="capsule-meta">
        <span class="meta-time">{{ formatTime(capsule.created_at) }}</span>
        <span class="meta-separator">·</span>
        <span class="meta-status">{{ getStatusText(capsule.status) }}</span>
      </div>

      <!-- 描述（超出省略） -->
      <p class="capsule-desc">
        {{ capsule.content_preview }}
      </p>

      <!-- 统计信息（点赞、解锁、评论） -->
      <div class="capsule-stats">
        <span class="stat-item">
          👍 {{ capsule.like_count || 0 }}
        </span>
        <span class="stat-separator">·</span>
        <span class="stat-item">
          🔓 {{ capsule.unlock_count || 0 }}
        </span>
        <span class="stat-separator">·</span>
        <span class="stat-item">
          💬 {{ capsule.comment_count || 0 }}
        </span>
      </div>

      <!-- 操作按钮（查看、点赞）
      <div class="capsule-actions">
        <button 
          class="action-btn view-btn"
          @click.stop="handleViewClick"
        >
          查看详情
        </button>
        <button 
          class="action-btn like-btn"
          :class="{ liked: capsule.liked }"
          @click.stop="handleLikeClick"
        >
          👍 {{ capsule.like_count || 0 }}
        </button>
      </div> -->
      <!-- ⭐ 重要：这里改为插槽，用于插入操作按钮 -->
      <div class="capsule-actions">
        <slot name="actions"></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatRelative } from '@/utils/formatTime.js'

/**
 * 组件作用：
 * 1. 统一展示胶囊基础信息，支持网格/列表两种视图切换
 * 2. 封装胶囊可见性、状态、统计信息的展示逻辑
 * 3. 触发查看详情、点赞事件，由父页面处理具体业务逻辑
 * 
 * 组件接口（Props）：
 * @param {Object} capsule - 胶囊数据，格式：
 *   {
 *     id: String, // 胶囊ID
 *     title: String, // 胶囊标题
 *     created_at: String, // ISO时间字符串
 *     visibility: String, // 可见性（"public"/"friends"/"private"）
 *     status: String, // 状态（"draft"/"pending"/"published"）
 *     content_preview: String, // 内容预览
 *     like_count: Number, // 点赞数
 *     unlock_count: Number, // 解锁次数
 *     comment_count: Number, // 评论数
 *     cover_image: String // 封面图URL（可选）
 *     liked: Boolean // 是否已点赞（前端状态）
 *   }
 * @param {String} viewMode - 视图模式（"grid"网格 / "list"列表）
 * 
 * 组件事件（Emits）：
 * @emit view - 点击"查看详情"时触发，参数为胶囊ID（String）
 * @emit like - 点击"点赞"时触发，参数为胶囊ID（String）
 * @emit click - 点击卡片非按钮区域时触发，参数为胶囊ID（String）
 */
const props = defineProps({
  capsule: {
    type: Object,
    required: true,
    validator: (value) => {
      // 校验胶囊必填字段
      return value.id && value.title && value.created_at && value.visibility && value.status
    }
  },
  viewMode: {
    type: String,
    required: true,
    validator: (value) => ['grid', 'list'].includes(value)
  }
})

const emit = defineEmits(['view', 'like', 'click'])

/**
 * 辅助函数：获取可见性图标
 * @param {String} visibility - 可见性（"public"/"friends"/"private"）
 * @returns {String} 图标字符串
 */
const getVisibilityIcon = (visibility) => {
  switch (visibility) {
    case 'private': return '🔒'
    case 'friends': return '👥'
    case 'campus': return '🌐'  // 处理后端返回的campus
    case 'public': return '🌐'  // 处理前端可能的public
    default: return '🌐'
  }
}

/**
 * 辅助函数：获取可见性文字
 * @param {String} visibility - 可见性（"public"/"friends"/"private"）
 * @returns {String} 文字描述
 */
const getVisibilityText = (visibility) => {
  switch (visibility) {
    case 'private':
      return '仅自己可见'
    case 'friends':
      return '好友可见'
    case 'campus':
      return '校园公开'  // 处理后端返回的campus
    case 'public':
      return '校园公开'  // 处理前端可能的public
    default:
      return '公开'
  }
}

/**
 * 辅助函数：获取状态文字
 * @param {String} status - 状态（"draft"/"pending"/"published"）
 * @returns {String} 状态描述
 */
const getStatusText = (status) => {
  switch (status) {
    case 'draft': return '草稿'
    case 'pending': return '待审核'
    case 'published': return '已发布'
    default: return status
  }
}

/**
 * 辅助函数：格式化时间（调用通用工具函数）
 * @param {String} isoStr - ISO时间字符串
 * @returns {String} 格式化后的相对时间
 */
const formatTime = (isoStr) => {
  return formatRelative(isoStr)
}

/**
 * 事件处理：点击卡片整体
 */
const handleCardClick = () => {
  emit('click', props.capsule.id)
}

/**
 * 事件处理：点击"查看详情"按钮
 */
const handleViewClick = () => {
  emit('view', props.capsule.id)
}

/**
 * 事件处理：点击"点赞"按钮
 */
const handleLikeClick = () => {
  emit('like', props.capsule.id)
}
</script>

<style scoped>
/* 样式保持不变，只修改了点赞按钮的样式以支持 liked 状态 */
.capsule-card {
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(250, 251, 255, 0.8));
  border: 1px solid rgba(12, 18, 36, 0.06);
  transition: all 0.3s;
  cursor: pointer;
}

.capsule-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(108, 140, 255, 0.2);
}

/* 网格视图样式 */
.capsule-thumb {
  height: 160px;
  background: #f8fafc;
  position: relative;
  overflow: hidden;
}

.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: var(--accent);
  opacity: 0.5;
}

.capsule-visibility {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255, 255, 255, 0.9);
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  color: var(--muted);
  backdrop-filter: blur(4px);
}

/* 列表视图样式 */
.capsule-card.list-mode {
  display: flex;
  gap: 16px;
  padding: 16px;
}

.capsule-card.list-mode .capsule-body {
  flex: 1;
}

.visibility-icon {
  margin-left: 8px;
  font-size: 14px;
}

/* 卡片内容样式 */
.capsule-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.capsule-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
  margin: 0;
}

.capsule-meta {
  color: var(--muted);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-separator {
  margin: 0 4px;
  color: var(--muted);
  opacity: 0.6;
}

.capsule-desc {
  color: var(--muted);
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.capsule-stats {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: auto;
  font-size: 12px;
  color: var(--muted);
}

.stat-separator {
  opacity: 0.6;
}

.capsule-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(12, 18, 36, 0.05);
}

.action-btn {
  background: transparent;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.view-btn {
  color: var(--accent);
  flex: 1;
}

.view-btn:hover {
  background: var(--accent-light);
}

.like-btn {
  color: var(--muted);
}

.like-btn.liked {
  color: var(--danger);
}

.like-btn:hover {
  color: var(--danger);
  background: rgba(239, 68, 68, 0.05);
}

/* 设计令牌：复用全局样式变量 */
:root {
  --bg: #f5f8ff;
  --card: #ffffff;
  --muted: #6b7280;
  --accent: #6c8cff;
  --accent-light: rgba(108, 140, 255, 0.1);
  --danger: #ef4444;
  --shadow: 0 6px 18px rgba(12, 18, 36, 0.06);
  --shadow-lg: 0 10px 25px rgba(12, 18, 36, 0.1);
}
</style>