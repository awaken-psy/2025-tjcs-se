<template>
  <!-- 活动状态标签组件：统一展示活动状态（未开始/进行中/已结束），支持自定义颜色和尺寸 -->
  <span 
    class="event-status-badge"
    :class="[status, size, { 'with-icon': showIcon }]"
    @click="$emit('click', status)"
  >
    <i
      v-if="showIcon"
      class="status-icon"
    >{{ getStatusIcon() }}</i>
    <span class="status-text">{{ getStatusText() }}</span>
  </span>
</template>

<script setup>
import { computed } from 'vue'

/**
 * 组件作用：
 * 1. 统一活动状态展示逻辑，替代各页面中重复的状态标签代码（如校园活动页、时间轴页）
 * 2. 支持自定义状态、尺寸、是否显示图标，适配不同页面场景
 * 3. 减少页面级文件中重复的样式和逻辑代码
 * 
 * 组件接口（Props）：
 * @param {String} status - 活动状态（必传，支持"upcoming"/"ongoing"/"ended"）
 * @param {String} size - 标签尺寸（可选，"small"/"default"/"large"，默认"default"）
 * @param {Boolean} showIcon - 是否显示状态图标（可选，默认true）
 * 
 * 组件事件（Emits）：
 * @emit click - 点击标签时触发，参数为当前状态（String）
 */
const props = defineProps({
  status: {
    type: String,
    required: true,
    validator: (val) => ['upcoming', 'ongoing', 'ended'].includes(val)
  },
  size: {
    type: String,
    default: 'default',
    validator: (val) => ['small', 'default', 'large'].includes(val)
  },
  showIcon: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click'])

/**
 * 辅助函数：根据状态获取图标
 * @returns {String} 图标字符（如"⏳"/"▶️"/"✅"）
 */
const getStatusIcon = () => {
  switch (props.status) {
  case 'upcoming': return '⏳'
  case 'ongoing': return '▶️'
  case 'ended': return '✅'
  default: return '❓'
  }
}

/**
 * 辅助函数：根据状态获取文本描述
 * @returns {String} 状态文本（如"未开始"/"进行中"/"已结束"）
 */
const getStatusText = () => {
  switch (props.status) {
  case 'upcoming': return '未开始'
  case 'ongoing': return '进行中'
  case 'ended': return '已结束'
  default: return '未知状态'
  }
}
</script>

<style scoped>
/* 基础标签样式 */
.event-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
}

/* 状态颜色：未开始（蓝色）、进行中（绿色）、已结束（灰色） */
.event-status-badge.upcoming {
  background: rgba(108, 140, 255, 0.1);
  color: var(--accent);
}

.event-status-badge.ongoing {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success);
}

.event-status-badge.ended {
  background: rgba(107, 114, 128, 0.1);
  color: var(--muted);
}

/* 尺寸控制 */
.event-status-badge.small {
  font-size: 12px;
  padding: 1px 6px;
  gap: 4px;
}

.event-status-badge.default {
  font-size: 13px;
  padding: 2px 8px;
}

.event-status-badge.large {
  font-size: 14px;
  padding: 3px 10px;
  gap: 8px;
}

/* 图标样式 */
.status-icon {
  font-size: 1em; /* 跟随文本尺寸 */
}

/* 无图标时隐藏间隙 */
.event-status-badge:not(.with-icon) {
  gap: 0;
}

/*  hover效果 */
.event-status-badge:hover.upcoming {
  background: rgba(108, 140, 255, 0.2);
}

.event-status-badge:hover.ongoing {
  background: rgba(16, 185, 129, 0.2);
}

.event-status-badge:hover.ended {
  background: rgba(107, 114, 128, 0.2);
}

/* 设计令牌：复用全局变量 */
:root {
  --accent: #6c8cff;
  --success: #10b981;
  --muted: #6b7280;
}
</style>