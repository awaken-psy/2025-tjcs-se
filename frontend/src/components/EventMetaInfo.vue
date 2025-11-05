<template>
  <div class="detail-meta">
    <div class="meta-grid">
      <div class="meta-item">
        <div class="meta-icon">
          <i class="fas fa-user-circle" />
        </div>
        <div class="meta-content">
          <span class="meta-label">主办方</span>
          <span class="meta-value">
            <img
              v-if="event.organizerAvatar"
              :src="event.organizerAvatar"
              alt="主办方头像"
              class="org-avatar"
            >
            <span class="organizer-name">{{ event.organizer || '未知主办方' }}</span>
          </span>
        </div>
      </div>

      <div class="meta-item">
        <div class="meta-icon">
          <i class="fas fa-clock" />
        </div>
        <div class="meta-content">
          <span class="meta-label">活动时间</span>
          <span class="meta-value time-range">
            <span class="time-start">{{ formatStandard(event.time) }}</span>
            <i class="fas fa-arrow-right time-arrow" />
            <span class="time-end">{{ formatStandard(event.endTime) }}</span>
          </span>
        </div>
      </div>

      <div class="meta-item">
        <div class="meta-icon">
          <i class="fas fa-map-marker-alt" />
        </div>
        <div class="meta-content">
          <span class="meta-label">活动地点</span>
          <span class="meta-value location">
            <i class="fas fa-location-dot" />
            {{ event.location || '地点待定' }}
          </span>
        </div>
      </div>

      <div class="meta-item">
        <div class="meta-icon">
          <i class="fas fa-hourglass-end" />
        </div>
        <div class="meta-content">
          <span class="meta-label">报名截止</span>
          <span
            class="meta-value deadline"
            :class="{ 'deadline-passed': isDeadlinePassed }"
          >
            <i
              class="fas"
              :class="isDeadlinePassed ? 'fa-exclamation-triangle' : 'fa-clock'"
            />
            {{ formatStandard(event.registerDeadline) }}
            <span
              v-if="isDeadlinePassed"
              class="deadline-status"
            >（已截止）</span>
          </span>
        </div>
      </div>

      <div class="meta-item">
        <div class="meta-icon">
          <i class="fas fa-users" />
        </div>
        <div class="meta-content">
          <span class="meta-label">参与人数</span>
          <span class="meta-value participants">
            <span class="participant-count">{{ event.participantCount || 0 }}</span>
            <span class="participant-separator">/</span>
            <span class="participant-total">{{ event.maxParticipants || 0 }}</span>
            <span class="participant-unit">人</span>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: calculateProgress() + '%' }"
                :class="{ 'progress-full': calculateProgress() >= 100 }"
              />
            </div>
          </span>
        </div>
      </div>

      <div class="meta-item">
        <div class="meta-icon">
          <i class="fas fa-flag" />
        </div>
        <div class="meta-content">
          <span class="meta-label">活动状态</span>
          <span class="meta-value">
            <EventStatusBadge
              :status="event.status"
              size="small"
            />
          </span>
        </div>
      </div>
    </div>

    <div
      v-if="event.tags && event.tags.length > 0"
      class="meta-tags"
    >
      <div class="tags-header">
        <i class="fas fa-tags" />
        <span class="tags-label">活动标签</span>
      </div>
      <div class="tags-container">
        <span 
          v-for="(tag, idx) in event.tags" 
          :key="idx" 
          class="tag-item"
          :style="{ 
            backgroundColor: getTagColor(tag),
            color: getTagTextColor(tag)
          }"
        >
          <i class="fas fa-hashtag" />
          {{ tag }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import EventStatusBadge from './EventStatusBadge.vue'

const props = defineProps({
  event: { type: Object, required: true },
})

const formatStandard = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).replace(/\//g, '-')
}

const isDeadlinePassed = computed(() => {
  if (!props.event.registerDeadline) return false
  return new Date(props.event.registerDeadline) < new Date()
})

const calculateProgress = () => {
  const current = props.event.participantCount || 0
  const total = props.event.maxParticipants || 1
  return Math.min((current / total) * 100, 100)
}

const getTagColor = (tag) => {
  const colors = [
    'rgba(66, 153, 225, 0.1)',
    'rgba(72, 187, 120, 0.1)',
    'rgba(246, 173, 85, 0.1)',
    'rgba(237, 100, 166, 0.1)',
    'rgba(159, 122, 234, 0.1)',
    'rgba(102, 126, 234, 0.1)'
  ]
  const index = tag.length % colors.length
  return colors[index]
}

const getTagTextColor = (tag) => {
  const colors = [
    '#4299e1',
    '#48bb78',
    '#f6ad55',
    '#ed64a6',
    '#9f7aea',
    '#667eea'
  ]
  const index = tag.length % colors.length
  return colors[index]
}
</script>

<style scoped>
.detail-meta {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 20px;
  padding: 28px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 4px 20px rgba(149, 157, 165, 0.08);
  backdrop-filter: blur(10px);
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 28px;
}

.meta-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 16px;
  border: 1px solid rgba(226, 232, 240, 0.6);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  overflow: hidden;
}

.meta-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(180deg, #4299e1, #667eea);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.meta-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(149, 157, 165, 0.12);
  border-color: rgba(102, 126, 234, 0.2);
}

.meta-item:hover::before {
  opacity: 1;
}

.meta-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #4299e1, #667eea);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.meta-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-label {
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.meta-value {
  font-size: 16px;
  font-weight: 500;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.org-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.organizer-name {
  font-weight: 600;
  color: #334155;
}

.time-range {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.time-start, .time-end {
  background: rgba(102, 126, 234, 0.05);
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
}

.time-arrow {
  color: #94a3b8;
  font-size: 12px;
}

.location {
  background: rgba(72, 187, 120, 0.05);
  padding: 6px 12px;
  border-radius: 8px;
  font-weight: 500;
}

.location i {
  color: #48bb78;
}

.deadline {
  background: rgba(246, 173, 85, 0.05);
  padding: 6px 12px;
  border-radius: 8px;
  font-weight: 500;
}

.deadline i {
  color: #f6ad55;
}

.deadline-passed {
  background: rgba(248, 113, 113, 0.05);
  color: #ef4444;
}

.deadline-passed i {
  color: #ef4444;
}

.deadline-status {
  font-size: 13px;
  font-weight: 600;
}

.participants {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.participant-count {
  font-size: 18px;
  font-weight: 700;
  color: #4299e1;
}

.participant-total {
  font-size: 16px;
  font-weight: 600;
  color: #64748b;
}

.participant-separator {
  color: #cbd5e1;
  font-weight: 500;
}

.participant-unit {
  color: #64748b;
  font-size: 14px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(226, 232, 240, 0.8);
  border-radius: 3px;
  overflow: hidden;
  margin-top: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4299e1, #667eea);
  border-radius: 3px;
  transition: width 0.5s ease;
}

.progress-full {
  background: linear-gradient(90deg, #48bb78, #38a169);
}

/* 标签样式 */
.meta-tags {
  background: white;
  padding: 24px;
  border-radius: 16px;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.tags-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.tags-header i {
  color: #667eea;
  font-size: 18px;
}

.tags-label {
  font-size: 16px;
  font-weight: 600;
  color: #334155;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-item {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid transparent;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tag-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: currentColor;
}

.tag-item i {
  font-size: 11px;
  opacity: 0.8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .detail-meta {
    padding: 20px;
  }
  
  .meta-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .meta-item {
    padding: 16px;
    gap: 12px;
  }
  
  .meta-icon {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }
  
  .time-range {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }
  
  .time-arrow {
    transform: rotate(90deg);
  }
}

@media (max-width: 480px) {
  .detail-meta {
    padding: 16px;
    border-radius: 16px;
  }
  
  .meta-item {
    padding: 12px;
  }
  
  .meta-value {
    font-size: 14px;
  }
  
  .tags-container {
    gap: 8px;
  }
  
  .tag-item {
    padding: 6px 12px;
    font-size: 12px;
  }
}
</style>