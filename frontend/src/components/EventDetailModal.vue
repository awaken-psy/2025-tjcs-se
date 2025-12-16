<template>
  <div class="event-detail-modal" :class="{ active: show }">
    <div class="modal-overlay" @click="$emit('close')"></div>
    <div class="modal-content">
      <!-- 头部 -->
      <div class="modal-header">
        <div class="header-content">
          <h2 class="modal-title">{{ displayEvent.name }}</h2>
          <div class="event-id">ID: {{ displayEvent.id }}</div>
        </div>
        <button class="close-btn" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <!-- 内容 -->
      <div class="modal-body">
        <!-- 封面 -->
        <div class="event-cover" v-if="displayEvent.cover_img">
          <img :src="displayEvent.cover_img" :alt="displayEvent.name" class="cover-img" />
        </div>
        
        <!-- 元信息 -->
        <EventMetaInfo :event="displayEvent" />
        
        <!-- 详细描述 -->
        <div class="event-detail">
          <h3 class="detail-title">
            <i class="fas fa-info-circle"></i>
            活动详情
          </h3>
          <div class="detail-content">
            {{ displayEvent.description }}
          </div>
        </div>
        
        <!-- 我的报名信息 -->
        <div class="my-registration" v-if="displayEvent.is_registered">
          <h3 class="registration-title">
            <i class="fas fa-check-circle"></i>
            我的报名状态
          </h3>
          <div class="registration-info">
            <div class="info-item">
              <i class="fas fa-calendar-check"></i>
              报名时间：{{ formatDate(displayEvent.created_at) }}
            </div>
            <div class="info-item">
              <i class="fas fa-check"></i>
              已成功报名
            </div>
          </div>
        </div>
      </div>
      
      <!-- 底部操作 -->
      <div class="modal-footer">
        <button class="btn secondary" @click="$emit('close')">
          关闭
        </button>
        <EventRegButton
          :is-registered="displayEvent.is_registered || false"
          :is-loading="isProcessing"
          :is-disabled="isEventDisabled(displayEvent)"
          :disabled-tip="getDisabledTip(displayEvent)"
          size="large"
          class="action-btn"
          @reg="$emit('register', displayEvent.id)"
          @cancel="$emit('cancel-register', displayEvent.id)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import EventMetaInfo from './EventMetaInfo.vue'
import EventRegButton from './EventRegButton.vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  event: {
    type: Object,
    required: true
  },
  isProcessing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'register', 'cancel-register'])

// 创建计算属性，优化显示数据
const displayEvent = computed(() => {
  if (!props.event) return {}
  
  return {
    ...props.event,
    location: props.event.location || '学校大礼堂',
    participant_count: props.event.participant_count || 0,
    tags: props.event.tags || []
  }
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }).replace(/\//g, '-')
  } catch (e) {
    return ''
  }
}

const isEventDisabled = (event) => {
  if (!event.date) return true
  try {
    const now = new Date()
    const eventDate = new Date(event.date)
    return eventDate < now
  } catch (e) {
    return true
  }
}

const getDisabledTip = (event) => {
  if (!event.date) return '活动时间未设置'
  
  try {
    const now = new Date()
    const eventDate = new Date(event.date)
    if (eventDate < now) {
      return '活动已结束'
    }
    return ''
  } catch (e) {
    return '时间格式错误'
  }
}
</script>

<style scoped>
.event-detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.event-detail-modal.active {
  display: flex;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
}

.modal-content {
  position: relative;
  width: 700px;
  max-width: 100%;
  max-height: 90vh;
  background: white;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.header-content {
  flex: 1;
}

.modal-title {
  font-size: 24px;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 8px 0;
  line-height: 1.3;
}

.event-id {
  font-size: 14px;
  color: #718096;
  font-family: monospace;
}

.close-btn {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: none;
  background: white;
  color: #718096;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  transition: all 0.2s ease;
  border: 1px solid #e2e8f0;
}

.close-btn:hover {
  background: #f1f5f9;
  color: #4299e1;
  border-color: #cbd5e1;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* 封面 */
.event-cover {
  width: 100%;
  height: 300px;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 24px;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 详情 */
.event-detail {
  margin-top: 24px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.detail-title {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-title i {
  color: #4299e1;
}

.detail-content {
  color: #4a5568;
  font-size: 16px;
  line-height: 1.6;
  white-space: pre-line;
}

/* 我的报名信息 */
.my-registration {
  margin-top: 24px;
  padding: 20px;
  background: #f0fff4;
  border-radius: 12px;
  border: 1px solid #c6f6d5;
}

.registration-title {
  font-size: 18px;
  font-weight: 600;
  color: #22543d;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.registration-title i {
  color: #38a169;
}

.registration-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  color: #2d3748;
}

.info-item i {
  color: #38a169;
}

/* 底部操作 */
.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-top: 1px solid #e2e8f0;
  background: white;
}

.btn {
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  transition: all 0.2s ease;
}

.btn.secondary {
  background: #e2e8f0;
  color: #4a5568;
}

.btn.secondary:hover {
  background: #cbd5e1;
}

.action-btn {
  min-width: 140px;
}

/* 滚动条 */
.modal-body::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.modal-body::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .event-detail-modal {
    padding: 10px;
  }
  
  .modal-content {
    max-height: 95vh;
  }
  
  .modal-header {
    padding: 20px;
  }
  
  .modal-title {
    font-size: 20px;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .event-cover {
    height: 200px;
  }
  
  .modal-footer {
    padding: 16px 20px;
  }
  
  .btn {
    padding: 10px 20px;
  }
}
</style>