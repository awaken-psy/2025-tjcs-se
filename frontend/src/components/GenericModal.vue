<template>
  <div
    v-if="isShow"
    class="generic-modal-wrapper"
    @keydown.esc="handleClose"
    tabindex="0"
  >
    <div
      class="modal-overlay"
      @click="handleClose"
    />

    <div 
      class="modal-panel"
      :style="{ width: width }"
    >
      <div class="modal-header">
        <h3 class="modal-title">
          {{ title }}
        </h3>
        <button
          class="modal-close"
          @click="handleClose"
          aria-label="关闭弹窗"
        >
          ✕
        </button>
      </div>

      <div class="modal-body">
        <slot />
      </div>

      <div 
        v-if="$slots.actions" 
        class="modal-footer-actions"
      >
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, onMounted, onUnmounted, watch } from 'vue';

const props = defineProps({
  // 是否显示模态框
  isShow: {
    type: Boolean,
    default: false,
  },
  // 模态框标题
  title: {
    type: String,
    default: '弹窗标题',
  },
  // 模态框宽度 (可选，用于调整大小)
  width: {
    type: String,
    default: '500px',
  },
});

const emit = defineEmits(['close']);

const handleClose = () => {
  emit('close');
};

// 监听 isShow 状态变化，防止背景滚动
watch(() => props.isShow, (newValue) => {
  if (newValue) {
    document.body.style.overflow = 'hidden';
    // 确保打开时焦点在模态框上，以便 ESC 键生效
    setTimeout(() => {
      document.querySelector('.generic-modal-wrapper')?.focus();
    }, 50);
  } else {
    document.body.style.overflow = '';
  }
}, { immediate: true });

onUnmounted(() => {
  // 确保组件销毁时恢复滚动
  document.body.style.overflow = '';
});

</script>

<style scoped>
/* 模态框容器 */
.generic-modal-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000; /* 确保在其他内容之上 */
  display: flex;
  justify-content: center;
  align-items: center;
  outline: none; /* 允许 tabindex 聚焦 */
}

/* 背景遮罩 */
.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px); /* 增加现代感 */
}

/* 模态框主体面板 */
.modal-panel {
  position: relative;
  background: var(--card, #ffffff);
  border-radius: var(--radius-lg, 12px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  max-height: 90vh;
  overflow: hidden; /* 内部滚动 */
  display: flex;
  flex-direction: column;
  z-index: 1001;
  transition: transform 0.3s ease-out, opacity 0.3s ease-out;
  transform: scale(0.95);
  opacity: 0;
  animation: modal-in 0.3s forwards;
}

@keyframes modal-in {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

/* 头部样式 */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 25px;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0; /* 阻止收缩 */
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: var(--muted, #6b7280);
  padding: 0;
  line-height: 1;
  transition: color 0.2s;
}

.modal-close:hover {
  color: #374151;
}

/* 内容主体样式 */
.modal-body {
  padding: 20px 25px;
  overflow-y: auto; /* 允许内容过多时滚动 */
  flex-grow: 1;
}

/* 底部操作区样式 */
.modal-footer-actions {
  display: flex;
  justify-content: flex-end; /* 按钮靠右 */
  gap: 10px;
  padding: 15px 25px;
  border-top: 1px solid #e5e7eb;
  flex-shrink: 0;
}

/* 适应小屏幕 */
@media (max-width: 768px) {
  .modal-panel {
    width: 90vw !important; /* 强制小屏幕宽度 */
    max-width: 90vw;
  }
}
</style>