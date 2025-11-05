<template>
  <!-- 时间轴内容项：统一时间轴中单个内容的渲染逻辑，支持胶囊和活动两种类型，可复用在时间轴页、校园活动页 -->
  <div
    class="timeline-item"
    @click="$emit('click', item.id)"
  >
    <!-- 时间轴节点（区分类型） -->
    <div
      class="item-dot"
      :class="getDotClass(item.type)"
    />
    
    <!-- 内容主体 -->
    <div class="item-content">
      <!-- 标题 + 类型徽章 -->
      <div class="item-header">
        <h4 class="item-title">
          {{ item.title }}
          <EventStatusBadge 
            :status="getItemStatus(item)"
            size="small"
            :show-icon="false"
          />
        </h4>
        
        <!-- 元信息（作者/时间/地点） -->
        <div class="item-meta">
          <span
            v-if="item.author || item.organizer"
            class="meta-author"
          >
            <img 
              :src="item.authorAvatar || item.organizerAvatar" 
              alt="作者头像" 
              class="author-avatar"
            >
            {{ item.author || item.organizer }}
          </span>
          <span class="meta-time">{{ formatRelative(item.time) }}</span>
          <span
            v-if="item.location"
            class="meta-location"
          >
            <i class="fas fa-map-marker-alt" /> {{ item.location }}
          </span>
        </div>
      </div>

      <!-- 内容图片（可选） -->
      <div
        v-if="item.img || item.coverImg"
        class="item-image"
      >
        <img 
          :src="item.img || item.coverImg" 
          alt="内容图片" 
          class="content-img"
          @click.stop="$emit('image-click', item.id)"
        >
      </div>

      <!-- 内容描述（截断） -->
      <p class="item-desc">
        {{ truncateText(item.desc, 80) }}
      </p>

      <!-- 标签（可选） -->
      <div
        v-if="item.tags && item.tags.length > 0"
        class="item-tags"
      >
        <span 
          v-for="(tag, idx) in item.tags"
          :key="idx"
          class="tag-item"
          @click.stop="$emit('tag-click', tag)"
        >
          {{ tag }}
        </span>
      </div>

      <!-- 统计信息（区分类型） -->
      <div class="item-stats">
        <span
          v-if="item.type === 'capsule'"
          class="stat-item"
        >
          <i class="fas fa-heart" /> {{ item.likes || 0 }} 点赞
        </span>
        <span
          v-if="item.type === 'capsule'"
          class="stat-item"
        >
          <i class="fas fa-eye" /> {{ item.views || 0 }} 浏览
        </span>
        <span
          v-if="item.type === 'event'"
          class="stat-item"
        >
          <i class="fas fa-users" /> {{ item.participantCount || 0 }} 人参与
        </span>
      </div>

      <!-- 操作按钮（可选，如查看详情） -->
      <button 
        class="view-btn"
        @click.stop="$emit('view', item.id)"
      >
        查看详情
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { formatRelative } from '@/utils/formatTime.js'
// 复用已有的共用组件
import EventStatusBadge from '@/components/EventStatusBadge.vue'

/**
 * 组件作用：
 * 1. 统一时间轴中单个内容的渲染逻辑，替代时间轴页中重复的内容项代码（支持胶囊/活动两种类型）
 * 2. 整合标签点击、图片点击、查看详情等事件，标准化交互逻辑
 * 3. 统一文本截断、状态展示（复用EventStatusBadge），避免重复代码
 * 
 * 组件接口（Props）：
 * @param {Object} item - 内容数据（必传，支持胶囊/活动类型）
 *   胶囊类型（type: 'capsule'）：{ id, title, time, author, authorAvatar, desc, tags, likes, views, location, img, vis }
 *   活动类型（type: 'event'）：{ id, title, time, organizer, organizerAvatar, desc, tags, participantCount, location, coverImg, status }
 * 
 * 组件事件（Emits）：
 * @emit click - 点击内容项时触发，参数为内容ID（String）
 * @emit view - 点击查看详情按钮时触发，参数为内容ID（String）
 * @emit tag-click - 点击标签时触发，参数为标签文本（String）
 * @emit image-click - 点击图片时触发，参数为内容ID（String）
 */
const props = defineProps({
  item: {
    type: Object,
    required: true,
    validator: (val) => {
      // 校验必传字段
      const requiredFields = ['id', 'title', 'time', 'type']
      return requiredFields.every(key => val[key])
    }
  }
})

const emit = defineEmits(['click', 'view', 'tag-click', 'image-click'])

/**
 * 辅助函数：根据内容类型获取节点样式
 * @param {String} type - 内容类型（capsule/event）
 * @returns {String} 节点样式类名
 */
const getDotClass = (type) => {
  return type === 'capsule' ? 'dot capsule-dot' : 'dot event-dot'
}

/**
 * 辅助函数：获取内容状态（用于EventStatusBadge）
 * @param {Object} item - 内容数据
 * @returns {String} 状态（upcoming/ongoing/ended/public/friend/private）
 */
const getItemStatus = (item) => {
  if (item.type === 'event') {
    return item.status || 'upcoming'
  }
  // 胶囊类型返回可见性
  return item.vis || 'public'
}

/**
 * 辅助函数：文本截断（替代-webkit-line-clamp）
 * @param {String} text - 待截断文本
 * @param {Number} maxLen - 最大字符长度
 * @returns {String} 截断后文本
 */
const truncateText = (text, maxLen) => {
  if (!text) return ''
  return text.length <= maxLen ? text : `${text.slice(0, maxLen)}...`
}
</script>

<style scoped>
/* 时间轴内容项基础样式 */
.timeline-item {
  position: relative;
  margin-bottom: 24px;
  padding: 16px;
  background: var(--card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  transition: all 0.2s;
  cursor: pointer;
}

.timeline-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(108, 140, 255, 0.2);
}

/* 时间轴节点 */
.item-dot {
  position: absolute;
  left: -32px;
  top: 24px;
  width: 22px;
  height: 22px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

/* 节点颜色区分类型 */
.dot.capsule-dot::after {
  content: '';
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--accent);
}

.dot.event-dot::after {
  content: '';
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--success);
}

/* 内容主体 */
.item-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 标题区域 */
.item-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.item-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 元信息 */
.item-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 13px;
  color: var(--muted);
}

.meta-author {
  display: flex;
  align-items: center;
  gap: 6px;
}

.author-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

/* 内容图片 */
.item-image {
  width: 100%;
  border-radius: var(--radius-sm);
  overflow: hidden;
  cursor: pointer;
}

.content-img {
  width: 100%;
  height: auto;
  max-height: 240px;
  object-fit: cover;
  transition: transform 0.3s;
}

.item-image:hover .content-img {
  transform: scale(1.02);
}

/* 内容描述 */
.item-desc {
  font-size: 14px;
  color: #374151;
  line-height: 1.5;
  margin: 0;
}

/* 标签 */
.item-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  padding: 4px 8px;
  border-radius: 6px;
  background: var(--accent-light);
  color: var(--accent);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-item:hover {
  background: var(--accent);
  color: white;
}

/* 统计信息 */
.item-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--muted);
  padding-top: 8px;
  border-top: 1px solid rgba(12, 18, 36, 0.06);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 查看详情按钮 */
.view-btn {
  align-self: flex-end;
  background: var(--accent);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
  margin-top: 8px;
}

.view-btn:hover {
  background: var(--accent-hover);
  box-shadow: 0 4px 8px rgba(108, 140, 255, 0.2);
}

/* 设计令牌：复用全局变量 */
:root {
  --card: #ffffff;
  --accent: #6c8cff;
  --accent-hover: #5a7cff;
  --accent-light: rgba(108, 140, 255, 0.1);
  --success: #10b981;
  --muted: #6b7280;
  --shadow: 0 6px 18px rgba(12, 18, 36, 0.06);
  --shadow-lg: 0 10px 25px rgba(12, 18, 36, 0.1);
  --radius: 12px;
  --radius-sm: 8px;
}

/* 响应式适配：小屏幕调整节点位置 */
@media (max-width: 768px) {
  .item-dot {
    left: -24px;
  }
}
</style>