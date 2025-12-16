<template>
  <div class="my-reg-modal" :class="{ active: show }">
    <div class="modal-overlay" @click="$emit('close')"></div>
    <div class="modal-content">
      <!-- 头部 -->
      <div class="modal-header">
        <h2 class="modal-title">
          <i class="fas fa-calendar-check"></i>
          我的报名活动
        </h2>
        <button class="close-btn" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <!-- 标签页 -->
      <div class="modal-tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          class="tab-btn"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <i :class="tab.icon"></i>
          {{ tab.label }}
          <span class="tab-count">({{ getTabCount(tab.id) }})</span>
        </button>
      </div>
      
      <!-- 内容 -->
      <div class="modal-body">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>
        
        <!-- 活动列表 -->
        <div v-else class="registrations-list">
          <!-- 空状态 -->
          <div v-if="filteredEvents.length === 0" class="empty-state">
            <div class="empty-icon">
              <i class="fas fa-calendar-alt"></i>
            </div>
            <h3 class="empty-title">{{ getEmptyTitle() }}</h3>
            <p class="empty-description">{{ getEmptyDescription() }}</p>
            <button class="empty-action-btn" @click="$emit('discover')">
              <i class="fas fa-compass"></i>
              去发现活动
            </button>
          </div>
          
          <!-- 活动卡片 -->
          <div v-else class="events-grid">
            <EventCard
              v-for="event in filteredEvents"
              :key="event.id"
              :event="event"
              view-mode="list"
              :can-edit="canEdit(event)"
              :can-delete="canDelete(event)"
              class="registration-card"
              @view="$emit('view', event.id)"
              @register="$emit('register', event.id)"
              @cancel-register="$emit('cancel-register', event.id)"
              @edit="$emit('edit', event.id)"
              @delete="$emit('delete', event.id)"
            />
          </div>
        </div>
      </div>
      
      <!-- 底部 -->
      <div class="modal-footer">
        <div class="footer-info">
          共 {{ total }} 个活动，当前显示 {{ filteredEvents.length }} 个
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import EventCard from './EventCard.vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  events: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  total: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits([
  'close',
  'view',
  'register',
  'cancel-register',
  'edit',
  'delete',
  'discover'
])

// 标签页数据
const tabs = [
  { id: 'all', label: '全部报名', icon: 'fas fa-list' },
  { id: 'upcoming', label: '待参与', icon: 'fas fa-clock' },
  { id: 'ended', label: '已结束', icon: 'fas fa-check-circle' }
]

const activeTab = ref('all')

// 计算属性
const filteredEvents = computed(() => {
  if (!props.events || props.events.length === 0) return []
  
  switch (activeTab.value) {
    case 'upcoming':
      return props.events.filter(event => getEventStatus(event) === 'upcoming')
    case 'ended':
      return props.events.filter(event => getEventStatus(event) === 'ended')
    default:
      return props.events
  }
})

// 辅助函数
function getEventStatus(event) {
  if (!event.date) return 'upcoming'
  const now = new Date()
  const eventDate = new Date(event.date)
  return eventDate < now ? 'ended' : 'upcoming'
}

function getTabCount(tabId) {
  if (!props.events || props.events.length === 0) return 0
  
  switch (tabId) {
    case 'upcoming':
      return props.events.filter(event => getEventStatus(event) === 'upcoming').length
    case 'ended':
      return props.events.filter(event => getEventStatus(event) === 'ended').length
    default:
      return props.events.length
  }
}

function getEmptyTitle() {
  switch (activeTab.value) {
    case 'upcoming': return '暂无待参与活动'
    case 'ended': return '暂无已结束活动'
    default: return '暂无报名记录'
  }
}

function getEmptyDescription() {
  switch (activeTab.value) {
    case 'upcoming': return '报名活动后，待参与的活动将显示在这里'
    case 'ended': return '已结束的活动将显示在这里'
    default: return '浏览活动并报名，记录将显示在这里'
  }
}

function canEdit(event) {
  // 这里可以根据业务逻辑判断用户是否有编辑权限
  // 例如：只有活动创建者可以编辑
  return false // 暂时禁用
}

function canDelete(event) {
  // 这里可以根据业务逻辑判断用户是否有删除权限
  // 例如：只有活动创建者可以删除
  return false // 暂时禁用
}
</script>

<style scoped>
.my-reg-modal {
  position: fixed;
  inset: 0;
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 1002;
}

.my-reg-modal.active {
  display: flex;
  animation: fadeIn 0.3s ease;
}

.modal-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.modal-content {
  position: relative;
  width: 800px;
  max-width: 90vw;
  max-height: 90vh;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 30px;
  border-bottom: 1px solid rgba(230, 236, 240, 0.6);
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.close-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: #718096;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(66, 153, 225, 0.1);
  color: #4299e1;
}

.modal-tabs {
  display: flex;
  gap: 4px;
  padding: 0 30px;
  border-bottom: 1px solid rgba(230, 236, 240, 0.6);
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.tab-btn {
  flex: 1;
  padding: 16px 20px;
  border: none;
  background: transparent;
  color: #718096;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
  position: relative;
}

.tab-btn:hover:not(.active) {
  color: #4299e1;
  background: rgba(66, 153, 225, 0.05);
}

.tab-btn.active {
  color: #4299e1;
  font-weight: 600;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: #4299e1;
  border-radius: 3px 3px 0 0;
}

.tab-count {
  font-size: 12px;
  opacity: 0.8;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(66, 153, 225, 0.1);
  border-top-color: #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.loading-state p {
  color: #718096;
  font-size: 14px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(66, 153, 225, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  font-size: 32px;
  color: #4299e1;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 8px 0;
}

.empty-description {
  color: #718096;
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 24px 0;
  max-width: 300px;
}

.empty-action-btn {
  padding: 10px 20px;
  border-radius: 12px;
  background: #4299e1;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.empty-action-btn:hover {
  background: #3182ce;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.2);
}

.events-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.registration-card {
  transition: all 0.2s ease;
}

.registration-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(149, 157, 165, 0.15);
}

.modal-footer {
  padding: 16px 30px;
  border-top: 1px solid rgba(230, 236, 240, 0.6);
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.footer-info {
  font-size: 13px;
  color: #718096;
  text-align: center;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 滚动条美化 */
.modal-body::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-track {
  background: rgba(230, 236, 240, 0.3);
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

@media (max-width: 768px) {
  .modal-content {
    max-width: 95vw;
    max-height: 95vh;
    border-radius: 16px;
  }
  
  .modal-header {
    padding: 16px 20px;
  }
  
  .modal-title {
    font-size: 18px;
  }
  
  .modal-tabs {
    padding: 0 20px;
  }
  
  .tab-btn {
    padding: 12px 8px;
    font-size: 13px;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .modal-footer {
    padding: 12px 20px;
  }
}
</style>