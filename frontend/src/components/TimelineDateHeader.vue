<template>
  <!-- 时间轴日期分组头部：统一按日期分组的标题样式，含日期文本和内容数量，可复用在时间轴页、我的胶囊页 -->
  <div
    class="timeline-date-header"
    @click="$emit('click', date)"
  >
    <h3 class="date-title">
      {{ formatDate(date) }}
    </h3>
    <span class="item-count">{{ itemCount }} 条内容</span>
    <!-- 扩展操作（可选，如折叠/展开） -->
    <button 
      v-if="showToggle"
      class="toggle-btn"
      @click.stop="$emit('toggle', date)"
    >
      <i
        class="fas"
        :class="isExpanded ? 'fa-chevron-up' : 'fa-chevron-down'"
      />
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

/**
 * 组件作用：
 * 1. 统一时间轴日期分组的头部样式，替代各页面中重复的日期标题代码（时间轴页、我的胶囊页按日期分组时）
 * 2. 支持显示内容数量、折叠/展开按钮（可选），适配不同页面的分组需求
 * 3. 标准化日期格式化逻辑，避免重复编写日期转换代码
 * 
 * 组件接口（Props）：
 * @param {String} date - 日期字符串（YYYY-MM-DD，必传）
 * @param {Number} itemCount - 该日期下的内容数量（必传）
 * @param {Boolean} showToggle - 是否显示折叠/展开按钮（默认false）
 * @param {Boolean} isExpanded - 是否展开状态（配合showToggle使用，默认true）
 * 
 * 组件事件（Emits）：
 * @emit click - 点击头部时触发，参数为日期（String）
 * @emit toggle - 点击折叠/展开按钮时触发，参数为日期（String）
 */
const props = defineProps({
  date: {
    type: String,
    required: true,
    validator: (val) => /^\d{4}-\d{2}-\d{2}$/.test(val) // 校验YYYY-MM-DD格式
  },
  itemCount: {
    type: Number,
    required: true,
    validator: (val) => val >= 0
  },
  showToggle: {
    type: Boolean,
    default: false
  },
  isExpanded: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click', 'toggle'])

/**
 * 辅助函数：格式化日期（YYYY-MM-DD → YYYY年MM月DD日）
 * @param {String} dateStr - 日期字符串
 * @returns {String} 格式化后日期
 */
const formatDate = (dateStr) => {
  const [year, month, day] = dateStr.split('-')
  return `${year}年${month}月${day}日`
}
</script>

<style scoped>
/* 日期分组头部样式 */
.timeline-date-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(12, 18, 36, 0.08);
  cursor: pointer;
  transition: all 0.2s;
}

.timeline-date-header:hover {
  border-bottom-color: rgba(108, 140, 255, 0.2);
}

/* 日期标题 */
.date-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: #1e293b;
}

/* 内容数量 */
.item-count {
  font-size: 13px;
  color: var(--muted);
  margin-right: 8px;
}

/* 折叠/展开按钮 */
.toggle-btn {
  background: transparent;
  border: none;
  color: var(--accent);
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  transition: all 0.2s;
}

.toggle-btn:hover {
  background: var(--accent-light);
}

/* 设计令牌：复用全局变量 */
:root {
  --accent: #6c8cff;
  --accent-light: rgba(108, 140, 255, 0.1);
  --muted: #6b7280;
}
</style>