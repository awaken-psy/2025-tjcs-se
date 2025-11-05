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
        v-if="capsule.img" 
        :src="capsule.img" 
        :alt="capsule.title"
        class="thumb-img"
      >
      <div
        v-else
        class="thumb-placeholder"
      >
        {{ getVisibilityIcon(capsule.vis) }}
      </div>
      <!-- 可见性标签 -->
      <div class="capsule-visibility">
        {{ getVisibilityText(capsule.vis) }}
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
          {{ getVisibilityIcon(capsule.vis) }}
        </span>
      </h3>

      <!-- 元信息（时间、位置） -->
      <div class="capsule-meta">
        <span class="meta-time">{{ formatTime(capsule.time) }}</span>
        <span
          v-if="capsule.location"
          class="meta-separator"
        >·</span>
        <span
          v-if="capsule.location"
          class="meta-location"
        >{{ capsule.location }}</span>
      </div>

      <!-- 描述（超出省略） -->
      <p class="capsule-desc">
        {{ capsule.desc }}
      </p>

      <!-- 标签 -->
      <div class="capsule-tags">
        <span 
          v-for="(tag, idx) in capsule.tags" 
          :key="idx"
          class="tag-item"
        >
          {{ tag }}
        </span>
      </div>

      <!-- 统计信息（点赞、浏览） -->
      <div class="capsule-stats">
        <span class="stat-item">
          👍 {{ capsule.likes || 0 }}
        </span>
        <span class="stat-separator">·</span>
        <span class="stat-item">
          👁️ {{ capsule.views || 0 }}
        </span>
      </div>

      <!-- 操作按钮（查看、点赞） -->
      <div class="capsule-actions">
        <button 
          class="action-btn view-btn"
          @click.stop="handleViewClick"
        >
          查看详情
        </button>
        <button 
          class="action-btn like-btn"
          @click.stop="handleLikeClick"
        >
          👍 {{ capsule.likes || 0 }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatRelative } from '@/utils/formatTime.js'

/**
 * 组件作用：
 * 1. 统一展示胶囊基础信息，支持网格/列表两种视图切换
 * 2. 封装胶囊可见性、标签、统计信息的展示逻辑
 * 3. 触发查看详情、点赞事件，由父页面处理具体业务逻辑
 * 
 * 组件接口（Props）：
 * @param {Object} capsule - 胶囊数据，格式：
 *   {
 *     id: String, // 胶囊ID
 *     title: String, // 胶囊标题
 *     time: String, // ISO时间字符串（如"2024-06-15T22:30:00"）
 *     vis: String, // 可见性（"public"/"friend"/"private"）
 *     desc: String, // 胶囊描述
 *     tags: Array, // 标签列表（如["毕业","图书馆"]）
 *     likes: Number, // 点赞数
 *     views: Number, // 浏览数
 *     location: String, // 位置（可选，如"图书馆四楼"）
 *     img: String // 缩略图URL（可选）
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
      return value.id && value.title && value.time && value.vis
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
 * @param {String} vis - 可见性（"public"/"friend"/"private"）
 * @returns {String} 图标字符串
 */
const getVisibilityIcon = (vis) => {
  switch (vis) {
  case 'private': return '🔒'
  case 'friend': return '👥'
  default: return '🌐'
  }
}

/**
 * 辅助函数：获取可见性文字
 * @param {String} vis - 可见性（"public"/"friend"/"private"）
 * @returns {String} 文字描述
 */
const getVisibilityText = (vis) => {
  switch (vis) {
  case 'private': return '仅自己可见'
  case 'friend': return '好友可见'
  default: return '公开'
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
/* 样式说明：支持网格/列表两种视图，复用原HTML胶囊卡片样式 */
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

.capsule-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
}

.tag-item {
  background: var(--accent-light);
  color: var(--accent);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
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