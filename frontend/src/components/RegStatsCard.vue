<template>
  <!-- 报名统计卡片：统一展示“已报名/待参与/已结束”统计数据，可复用在校园活动页、用户主页 -->
  <div
    class="reg-stats-card"
    :class="size === 'large' ? 'large-size' : 'default-size'"
  >
    <div
      v-if="cardTitle"
      class="card-header"
    >
      <h3 class="card-title">
        {{ cardTitle }}
      </h3>
    </div>
    <div class="stats-grid">
      <!-- 已报名统计 -->
      <div
        class="stat-item"
        @click="$emit('click-all')"
      >
        <div class="stat-value">
          {{ totalReg }}
        </div>
        <div class="stat-label">
          {{ totalLabel || '已报名' }}
        </div>
      </div>
      <!-- 待参与统计 -->
      <div
        class="stat-item"
        @click="$emit('click-upcoming')"
      >
        <div class="stat-value">
          {{ upcomingReg }}
        </div>
        <div class="stat-label">
          {{ upcomingLabel || '待参与' }}
        </div>
      </div>
      <!-- 已结束统计 -->
      <div
        class="stat-item"
        @click="$emit('click-ended')"
      >
        <div class="stat-value">
          {{ endedReg }}
        </div>
        <div class="stat-label">
          {{ endedLabel || '已结束' }}
        </div>
      </div>
    </div>
    <!-- 查看列表按钮（可选） -->
    <button 
      v-if="showViewBtn"
      class="view-list-btn"
      @click="$emit('view-list')"
    >
      {{ viewBtnText || '查看全部' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

/**
 * 组件作用：
 * 1. 统一报名统计展示逻辑，替代校园活动页中重复的“我的报名统计”代码
 * 2. 支持自定义标题、统计标签、按钮文本，适配不同页面（校园活动页、用户主页）
 * 3. 标准化统计项点击事件，避免重复编写交互逻辑
 * 
 * 组件接口（Props）：
 * @param {Number} totalReg - 已报名总数（必传）
 * @param {Number} upcomingReg - 待参与数量（必传）
 * @param {Number} endedReg - 已结束数量（必传）
 * @param {String} cardTitle - 卡片标题（可选，默认“我的报名”）
 * @param {String} size - 卡片尺寸（default/large，默认default）
 * @param {Boolean} showViewBtn - 是否显示查看列表按钮（默认true）
 * @param {String} viewBtnText - 按钮文本（默认“查看全部”）
 * @param {String} totalLabel - 已报名标签（默认“已报名”）
 * @param {String} upcomingLabel - 待参与标签（默认“待参与”）
 * @param {String} endedLabel - 已结束标签（默认“已结束”）
 * 
 * 组件事件（Emits）：
 * @emit click-all - 点击“已报名”统计项时触发
 * @emit click-upcoming - 点击“待参与”统计项时触发
 * @emit click-ended - 点击“已结束”统计项时触发
 * @emit view-list - 点击查看列表按钮时触发
 */
const props = defineProps({
  totalReg: {
    type: Number,
    required: true,
    validator: (val) => val >= 0
  },
  upcomingReg: {
    type: Number,
    required: true,
    validator: (val) => val >= 0
  },
  endedReg: {
    type: Number,
    required: true,
    validator: (val) => val >= 0
  },
  cardTitle: {
    type: String,
    default: '我的报名'
  },
  size: {
    type: String,
    default: 'default',
    validator: (val) => ['default', 'large'].includes(val)
  },
  showViewBtn: {
    type: Boolean,
    default: true
  },
  viewBtnText: {
    type: String,
    default: '查看全部'
  },
  totalLabel: {
    type: String,
    default: '已报名'
  },
  upcomingLabel: {
    type: String,
    default: '待参与'
  },
  endedLabel: {
    type: String,
    default: '已结束'
  }
})

const emit = defineEmits(['click-all', 'click-upcoming', 'click-ended', 'view-list'])
</script>

<style scoped>
/* 基础卡片样式 */
.reg-stats-card {
  background: var(--card);
  border-radius: var(--radius);
  padding: 16px;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 尺寸变体 */
.default-size {
  max-width: 300px;
}

.large-size {
  max-width: 400px;
  padding: 20px;
}

/* 卡片头部 */
.card-header {
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(12, 18, 36, 0.06);
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  color: #1e293b;
}

/* 统计网格布局 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stat-item {
  text-align: center;
  padding: 12px 8px;
  background: var(--accent-light);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
}

.stat-item:hover {
  background: rgba(108, 140, 255, 0.15);
  transform: translateY(-2px);
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--muted);
}

/* 查看列表按钮 */
.view-list-btn {
  background: var(--accent);
  color: white;
  border: none;
  padding: 8px 0;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.view-list-btn:hover {
  background: var(--accent-hover);
  box-shadow: 0 4px 8px rgba(108, 140, 255, 0.2);
}

/* 设计令牌：复用全局变量 */
:root {
  --card: #ffffff;
  --accent: #6c8cff;
  --accent-hover: #5a7cff;
  --accent-light: rgba(108, 140, 255, 0.1);
  --muted: #6b7280;
  --shadow: 0 6px 18px rgba(12, 18, 36, 0.06);
  --radius: 12px;
  --radius-sm: 8px;
}
</style>