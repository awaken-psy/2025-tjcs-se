<template>
  <div 
    class="event-card"
    :class="{ 'list-view': viewMode === 'list' }"
    @click="$emit('view', event.id)"
  >
    <div class="event-content">
      <!-- 标题和状态 -->
      <div class="title-section">
        <h3 class="event-title">
          {{ event.name }}
        </h3>
        <EventStatusBadge 
          :status="getEventStatus(event)" 
          :size="viewMode === 'list' ? 'small' : 'default'" 
          show-icon 
        />
      </div>
      
      <!-- 元信息 -->
      <div class="event-meta">
        <span class="meta-item">
          <i class="fas fa-calendar"></i>
          {{ formatDate(event.date) }}
        </span>
        <span class="meta-separator">·</span>
        <span class="meta-item">
          <i class="fas fa-map-marker-alt"></i>
          {{ event.location }}
        </span>
        <span class="meta-separator">·</span>
        <span class="meta-item">
          <i class="fas fa-users"></i>
          {{ event.participant_count || 0 }}人参与
        </span>
      </div>
      
      <!-- 描述 -->
      <p class="event-description">
        {{ event.description }}
      </p>
      
      <!-- 标签 -->
      <div class="event-tags" v-if="event.tags && event.tags.length > 0">
        <span 
          v-for="tag in event.tags.slice(0, 3)" 
          :key="tag" 
          class="tag"
          @click.stop="$emit('tag-click', tag)"
        >
          #{{ tag }}
        </span>
        <span v-if="event.tags.length > 3" class="tag-more">
          +{{ event.tags.length - 3 }}
        </span>
      </div>
      
      <!-- 操作按钮区域 -->
      <div class="event-actions">
        <!-- 已报名状态显示查看状态按钮 -->
        <template v-if="event.is_registered">
          <button 
            class="btn primary status-btn"
            @click.stop="$emit('view', event.id)"
          >
            <i class="fas fa-eye"></i>
            查看状态
          </button>
        </template>
        <!-- 未报名状态显示报名按钮 -->
        <template v-else>
          <EventRegButton
            :is-registered="false"
            :is-disabled="isEventDisabled(event)"
            :disabled-tip="getDisabledTip(event)"
            size="default"
            class="action-btn"
            @reg="$emit('register', event.id)"
            @cancel="$emit('cancel-register', event.id)"
          />
        </template>
        
        <!-- 编辑和删除按钮 -->
        <div class="manage-buttons">
          <button 
            class="btn ghost small"
            @click.stop="$emit('edit', event.id)"
          >
            <i class="fas fa-edit"></i>
          </button>
          <button 
            class="btn ghost small danger"
            @click.stop="$emit('delete', event.id)"
          >
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import EventStatusBadge from './EventStatusBadge.vue'
import EventRegButton from './EventRegButton.vue'

const props = defineProps({
  event: {
    type: Object,
    required: true
  },
  viewMode: {
    type: String,
    default: 'grid',
    validator: (val) => ['grid', 'list'].includes(val)
  }
})

const emit = defineEmits([
  'view',
  'register',
  'cancel-register',
  'edit',
  'delete',
  'tag-click'
])

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getEventStatus = (event) => {
  if (!event.date) return 'upcoming'
  
  const now = new Date()
  const eventDate = new Date(event.date)
  
  // 简单判断：已过去的就是ended，未来的就是upcoming
  return eventDate < now ? 'ended' : 'upcoming'
}

const isEventDisabled = (event) => {
  if (!event.date) return true
  const now = new Date()
  const eventDate = new Date(event.date)
  return eventDate < now
}

const getDisabledTip = (event) => {
  return getEventStatus(event) === 'ended' ? '活动已结束' : ''
}

// 计算是否显示报名相关按钮
const showRegisterButton = computed(() => {
  return !props.event.is_registered && !isEventDisabled(props.event)
})
</script>

<style scoped>
.event-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 6px 20px rgba(149, 157, 165, 0.08);
  border: 1px solid rgba(230, 236, 240, 0.6);
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
  min-height: 200px;
  display: flex;
  flex-direction: column;
}

.event-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 30px rgba(149, 157, 165, 0.12);
  border-color: rgba(66, 153, 225, 0.2);
}

/* 列表视图 */
.event-card.list-view {
  flex-direction: row;
  gap: 20px;
  padding: 20px;
  min-height: 160px;
}

.event-card.list-view .event-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* 内容区域 */
.event-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

/* 标题区域 */
.title-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 12px;
}

.event-title {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
  line-height: 1.4;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 元信息 */
.event-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  color: #718096;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.meta-separator {
  color: #cbd5e0;
}

/* 描述 */
.event-description {
  color: #4a5568;
  font-size: 15px;
  line-height: 1.6;
  margin: 0 0 16px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
  min-height: 48px;
}

/* 标签 */
.event-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.tag {
  background: rgba(66, 153, 225, 0.1);
  color: #4299e1;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tag:hover {
  background: #4299e1;
  color: white;
  transform: translateY(-1px);
}

.tag-more {
  background: rgba(203, 213, 224, 0.1);
  color: #a0aec0;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

/* 操作按钮区域 */
.event-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid rgba(230, 236, 240, 0.6);
  margin-top: auto;
}

/* 报名/查看状态按钮 */
.action-btn {
  flex: 1;
}

.status-btn {
  flex: 1;
  padding: 8px 16px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 14px;
  background: linear-gradient(90deg, #4299e1, #38b2ac);
  color: white;
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.2);
}

.status-btn:hover {
  background: linear-gradient(90deg, #3182ce, #319795);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(66, 153, 225, 0.25);
}

/* 管理按钮区域 */
.manage-buttons {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 16px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 14px;
}

.btn.ghost {
  background: transparent;
  color: #718096;
  border: 1px solid #e2e8f0;
}

.btn.ghost:hover {
  background: rgba(66, 153, 225, 0.05);
  border-color: #4299e1;
  color: #4299e1;
}

.btn.small {
  padding: 6px 12px;
  font-size: 13px;
}

.btn.danger {
  color: #e53e3e;
}

.btn.danger:hover {
  background: rgba(229, 62, 62, 0.05);
  border-color: #e53e3e;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .event-card.list-view {
    flex-direction: column;
    gap: 16px;
    padding: 16px;
  }
  
  .title-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .event-title {
    font-size: 16px;
  }
  
  .event-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .meta-separator {
    display: none;
  }
  
  .event-actions {
    flex-direction: column;
    gap: 12px;
  }
  
  .action-btn, .status-btn {
    width: 100%;
  }
  
  .manage-buttons {
    width: 100%;
    justify-content: space-between;
  }
  
  .manage-buttons .btn {
    flex: 1;
  }
}

@media (max-width: 480px) {
  .event-content {
    padding: 16px;
  }
  
  .event-title {
    font-size: 15px;
  }
  
  .event-description {
    font-size: 14px;
    -webkit-line-clamp: 2;
  }
  
  .event-meta {
    font-size: 13px;
  }
  
  .btn {
    font-size: 13px;
    padding: 6px 12px;
  }
  
  .btn.small {
    padding: 5px 10px;
    font-size: 12px;
  }
}
</style>