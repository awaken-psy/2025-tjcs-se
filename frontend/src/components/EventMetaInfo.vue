<template>
  <div class="detail-meta">
    <div class="meta-grid">
      <!-- 活动时间 -->
      <div class="meta-item">
        <div class="meta-icon">
          <i class="fas fa-calendar-alt"></i>
        </div>
        <div class="meta-content">
          <span class="meta-label">活动时间</span>
          <span class="meta-value">
            <i class="fas fa-clock time-icon"></i>
            {{ formatDate(event.date) }}
          </span>
        </div>
      </div>

      <!-- 活动地点 -->
      <div class="meta-item">
        <div class="meta-icon">
          <i class="fas fa-map-marker-alt"></i>
        </div>
        <div class="meta-content">
          <span class="meta-label">活动地点</span>
          <span class="meta-value">
            <i class="fas fa-location-dot location-icon"></i>
            {{ event.location || '学校大礼堂' }}
          </span>
        </div>
      </div>

      <!-- 报名截止（与活动时间相同） -->
      <div class="meta-item">
        <div class="meta-icon">
          <i class="fas fa-hourglass-end"></i>
        </div>
        <div class="meta-content">
          <span class="meta-label">报名截止</span>
          <span class="meta-value">
            <i class="fas fa-clock deadline-icon"></i>
            {{ formatDate(event.date) }}
            <span v-if="isDeadlinePassed" class="deadline-tag">已截止</span>
          </span>
        </div>
      </div>

      <!-- 参与人数 -->
      <div class="meta-item">
        <div class="meta-icon">
          <i class="fas fa-users"></i>
        </div>
        <div class="meta-content">
          <span class="meta-label">参与人数</span>
          <span class="meta-value">
            <i class="fas fa-user-check user-icon"></i>
            {{ event.participant_count || 0 }} 人已报名
          </span>
        </div>
      </div>
    </div>

    <!-- 活动标签 -->
    <div v-if="event.tags && event.tags.length > 0" class="meta-tags">
      <div class="tags-header">
        <i class="fas fa-tags"></i>
        <span>活动标签</span>
      </div>
      <div class="tags-container">
        <span 
          v-for="(tag, idx) in event.tags" 
          :key="idx" 
          class="tag-item"
        >
          #{{ tag }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  event: { type: Object, required: true },
})

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '时间待定'
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
    return '时间待定'
  }
}

// 是否截止
const isDeadlinePassed = computed(() => {
  if (!props.event.date) return false
  try {
    return new Date(props.event.date) < new Date()
  } catch (e) {
    return false
  }
})
</script>

<style scoped>
.detail-meta {
  background: white;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.meta-item:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateY(-2px);
}

.meta-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: linear-gradient(135deg, #4299e1, #3182ce);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  flex-shrink: 0;
}

.meta-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.meta-label {
  font-size: 13px;
  font-weight: 600;
  color: #718096;
  text-transform: uppercase;
}

.meta-value {
  font-size: 16px;
  font-weight: 500;
  color: #2d3748;
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-icon {
  color: #4299e1;
  font-size: 14px;
}

.location-icon {
  color: #48bb78;
  font-size: 14px;
}

.deadline-icon {
  color: #f6ad55;
  font-size: 14px;
}

.user-icon {
  color: #9f7aea;
  font-size: 14px;
}

.deadline-tag {
  margin-left: 8px;
  padding: 2px 8px;
  background: #fed7d7;
  color: #c53030;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

/* 标签样式 */
.meta-tags {
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.tags-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
}

.tags-header i {
  color: #4299e1;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  padding: 6px 12px;
  background: #edf2f7;
  border-radius: 8px;
  font-size: 14px;
  color: #4a5568;
  font-weight: 500;
  transition: all 0.2s ease;
}

.tag-item:hover {
  background: #e2e8f0;
  color: #2d3748;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .meta-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .detail-meta {
    padding: 20px;
  }
  
  .meta-item {
    padding: 14px;
    gap: 12px;
  }
  
  .meta-icon {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }
}
</style>