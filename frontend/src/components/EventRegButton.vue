<template>
  <!-- 活动报名按钮：统一活动"报名/取消报名"逻辑，可复用在校园活动页 -->
  <button 
    class="event-reg-btn"
    :class="[
      { 'registered': isRegistered },
      { 'disabled': isDisabled },
      { 'loading': isLoading },
      size === 'large' ? 'large-size' : 'default-size'
    ]"
    :disabled="isDisabled || isLoading"
    @click="handleClick"
  >
    <!-- 加载动画 -->
    <span
      v-if="isLoading"
      class="loading-spinner small"
    />
    <!-- 按钮文本 -->
    <span class="btn-text">
      {{ isLoading 
        ? (isRegistered ? '取消中...' : '报名中...') 
        : (isRegistered ? cancelText : regText) 
      }}
    </span>
    <!-- 禁用提示（可选） -->
    <span
      v-if="isDisabled && disabledTip"
      class="disabled-tip"
    >
      {{ disabledTip }}
    </span>
  </button>
</template>

<script setup>
import { ref } from 'vue'

/**
 * 组件作用：
 * 1. 统一活动报名/取消报名按钮逻辑，替代校园活动页中重复的按钮代码
 * 2. 支持配置报名状态、加载状态、禁用状态，适配不同场景（未报名/已报名/已截止）
 * 3. 标准化按钮文本和禁用提示，避免重复编写状态判断逻辑
 * 
 * 组件接口（Props）：
 * @param {Boolean} isRegistered - 是否已报名（必传）
 * @param {Boolean} isLoading - 是否加载中（默认false）
 * @param {Boolean} isDisabled - 是否禁用（默认false，如活动已结束/报名截止）
 * @param {String} size - 按钮尺寸（default/large，默认default）
 * @param {String} regText - 报名文本（默认“立即报名”）
 * @param {String} cancelText - 取消报名文本（默认“取消报名”）
 * @param {String} disabledTip - 禁用提示（默认“已截止/已结束”）
 * 
 * 组件事件（Emits）：
 * @emit reg - 点击报名按钮时触发（isRegistered=false时）
 * @emit cancel - 点击取消报名按钮时触发（isRegistered=true时）
 */
const props = defineProps({
  isRegistered: {
    type: Boolean,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  isDisabled: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'default',
    validator: (val) => ['default', 'large'].includes(val)
  },
  regText: {
    type: String,
    default: '立即报名'
  },
  cancelText: {
    type: String,
    default: '取消报名'
  },
  disabledTip: {
    type: String,
    default: '已截止/已结束'
  }
})

const emit = defineEmits(['reg', 'cancel'])

/**
 * 按钮点击处理：区分报名/取消报名逻辑
 */
const handleClick = () => {
  if (props.isRegistered) {
    // 已报名：触发取消事件（需二次确认）
    if (confirm('确定要取消报名此活动吗？')) {
      emit('cancel')
    }
  } else {
    // 未报名：触发报名事件
    emit('reg')
  }
}
</script>

<style scoped>
/* 基础按钮样式 */
.event-reg-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
  position: relative;
}

/* 尺寸变体 */
.default-size {
  padding: 8px 16px;
  font-size: 14px;
}

.large-size {
  padding: 10px 20px;
  font-size: 15px;
}

/* 状态变体：未报名（主色） */
.event-reg-btn:not(.registered):not(.disabled) {
  background: var(--accent);
  color: white;
}

.event-reg-btn:not(.registered):not(.disabled):hover {
  background: var(--accent-hover);
  box-shadow: var(--shadow);
}

/* 状态变体：已报名（危险色） */
.event-reg-btn.registered:not(.disabled) {
  background: var(--danger);
  color: white;
}

.event-reg-btn.registered:not(.disabled):hover {
  background: #dc2626;
  box-shadow: 0 4px 8px rgba(239, 68, 68, 0.2);
}

/* 状态变体：禁用/加载中 */
.event-reg-btn.disabled,
.event-reg-btn.loading {
  opacity: 0.7;
  cursor: not-allowed;
  background: var(--muted-light);
  color: var(--muted);
}

/* 加载动画 */
.loading-spinner.small {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.7);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 禁用提示 */
.disabled-tip {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 4px;
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  font-size: 12px;
  border-radius: 4px;
  white-space: nowrap;
  z-index: 10;
}

/* 动画关键帧 */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 设计令牌：复用全局变量 */
:root {
  --accent: #6c8cff;
  --accent-hover: #5a7cff;
  --danger: #ef4444;
  --muted: #6b7280;
  --muted-light: rgba(107, 114, 128, 0.1);
  --shadow: 0 4px 8px rgba(108, 140, 255, 0.2);
  --radius-sm: 8px;
}
</style>