<template>
  <div class="capsule-detail-modal" :class="{ active: showModal }">
    <div class="modal-overlay" @click="handleClose" />
    <div class="modal-panel">
      <div class="modal-header">
        <h3 class="modal-title">
          {{ detailData.title || '胶囊详情' }}
        </h3>
        <button class="modal-close" @click="handleClose">✕</button>
      </div>

      <div class="modal-body">
        <div class="detail-meta">
          <span v-if="detailData.created_at" class="meta-item">
            <i class="fas fa-clock" /> 投递时间：
            {{ formatStandard(detailData.created_at) }}
          </span>
          <span v-if="detailData.visibility" class="meta-item">
            <i class="fas fa-eye" /> 可见性：
            {{ getVisText(detailData.visibility) }}
          </span>
          <span class="meta-item">
            <i class="fas fa-map-marker-alt" /> 投递位置：
            {{ detailData.address || '未知位置' }}
          </span>
          <span class="meta-item">
            <i :class="getStatusIcon(detailData.status)" /> 状态：
            {{ getStatusText(detailData.status) }}
          </span>
        </div>

        <div class="detail-unlock-condition">
          <i :class="getUnlockIcon(detailData.unlock_conditions_type)" />
          解锁条件：
          {{ getUnlockText(detailData) }}
          <span
            v-if="detailData.unlock_conditions_is_unlocked"
            class="unlocked-status">
            (已解锁)
          </span>
          <span v-else class="locked-status"> (待解锁) </span>
        </div>

        <hr class="divider" />

        <div
          v-if="detailData.media_files && detailData.media_files.length > 0"
          class="detail-media-preview"
          @click="activeMediaIndex = 0">
          <img
            :src="
              detailData.media_files[0].thumbnail ||
              (detailData.media_files[0].type === 'image'
                ? detailData.media_files[0].url
                : '')
            "
            :alt="detailData.title"
            class="detail-img-preview" />

          <div
            v-if="detailData.media_files[0].type !== 'image'"
            class="media-type-badge">
            <i
              :class="
                detailData.media_files[0].type === 'video'
                  ? 'fas fa-play-circle'
                  : 'fas fa-volume-up'
              "></i>
          </div>

          <div v-if="detailData.media_files.length > 1" class="media-count">
            <i class="fas fa-images" /> +{{ detailData.media_files.length - 1 }}
          </div>
          <div class="media-tip">点击查看详情</div>
        </div>

        <Transition name="fade">
          <div v-if="activeMediaIndex !== null" class="internal-media-viewer">
            <div class="viewer-overlay" @click="activeMediaIndex = null"></div>

            <div class="viewer-content">
              <button class="viewer-close" @click="activeMediaIndex = null">
                ✕
              </button>

              <button
                v-if="activeMediaIndex > 0"
                class="nav-btn prev"
                @click.stop="activeMediaIndex--">
                ◀
              </button>
              <button
                v-if="activeMediaIndex < detailData.media_files.length - 1"
                class="nav-btn next"
                @click.stop="activeMediaIndex++">
                ▶
              </button>

              <div class="media-container">
                <img
                  v-if="currentMedia.type === 'image'"
                  :src="currentMedia.url"
                  class="full-media" />

                <video
                  v-else-if="currentMedia.type === 'video'"
                  :src="currentMedia.url"
                  :poster="currentMedia.thumbnail"
                  controls
                  autoplay
                  class="full-media"></video>

                <div
                  v-else-if="currentMedia.type === 'audio'"
                  class="audio-player-container">
                  <div class="audio-card">
                    <div
                      class="audio-visualizer"
                      :class="{ 'is-playing': isPlaying }">
                      <div
                        class="disc"
                        :style="
                          currentMedia.thumbnail
                            ? `background-image: url(${currentMedia.thumbnail}); background-size: cover;`
                            : ''
                        ">
                        <i
                          v-if="!currentMedia.thumbnail"
                          class="fas fa-music"></i>
                      </div>
                    </div>
                    ...
                    <audio
                      :src="currentMedia.url"
                      controls
                      @play="isPlaying = true"
                      @pause="isPlaying = false"></audio>
                  </div>
                </div>
              </div>

              <div class="viewer-footer">
                {{ activeMediaIndex + 1 }} / {{ detailData.media_files.length }}
              </div>
            </div>
          </div>
        </Transition>

        <div class="detail-content-section">
          <label class="section-label">内容描述：</label>
          <div class="detail-content">
            {{ detailData.content || '暂无描述' }}
          </div>
        </div>

        <div
          v-if="detailData.tags && detailData.tags.length > 0"
          class="detail-tags">
          <span
            v-for="(tag, idx) in detailData.tags"
            :key="idx"
            class="tag-item">
            # {{ tag }}
          </span>
        </div>

        <hr class="divider" />

        <div class="detail-stats">
          <span class="stat-item">
            <i class="fas fa-eye" /> {{ detailData.view_count || 0 }} 浏览
          </span>
          <span class="stat-item" :class="{ active: detailData.is_liked }">
            <i class="fas fa-heart" /> {{ detailData.like_count || 0 }} 点赞
          </span>
          <span class="stat-item">
            <i class="fas fa-comment-dots" />
            {{ detailData.comment_count || 0 }} 评论
          </span>
          <span class="stat-item">
            <i class="fas fa-unlock" /> {{ detailData.unlock_count || 0 }} 解锁
          </span>
        </div>
      </div>

      <div class="modal-actions">
        <button class="btn ghost" @click="handleClose">关闭</button>
        <button
          v-if="detailData.is_mine"
          class="btn primary"
          @click="$emit('edit', detailData.id)">
          编辑内容
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, computed, watch } from 'vue'

// #region 辅助函数

/** 格式化 ISO 时间字符串为本地标准时间 */
const formatStandard = (isoStr) =>
  isoStr ? new Date(isoStr).toLocaleString() : 'N/A'

/** 获取可见性文本 */
const getVisText = (vis) => {
  switch (vis) {
    case 'private':
      return '仅自己可见'
    case 'friends':
      return '好友可见'
    case 'public':
      return '所有人可见'
  }
}

/** 获取胶囊状态文本 */
const getStatusText = (status) => {
  switch (status) {
    case 'draft':
      return '草稿'
    case 'published':
      return '已发布'
    case 'all':
      return '全部' // 通常不会在详情页显示'all'
    default:
      return '未知状态'
  }
}

/** 获取胶囊状态图标 */
const getStatusIcon = (status) => {
  switch (status) {
    case 'draft':
      return 'fas fa-pencil-alt'
    case 'published':
      return 'fas fa-check-circle'
    default:
      return 'fas fa-question-circle'
  }
}

/** 获取解锁条件图标 */
const getUnlockIcon = (type) => {
  switch (type) {
    case 'time':
      return 'fas fa-hourglass-half'
    case 'location':
      return 'fas fa-map-pin'
    case 'password':
      return 'fas fa-key'
    default:
      return 'fas fa-lock-open'
  }
}

/** 获取解锁条件描述文本 */
const getUnlockText = (detailData) => {
  if (
    !detailData.unlock_conditions_type ||
    detailData.unlock_conditions_type === 'none'
  )
    return '无限制'

  switch (detailData.unlock_conditions_type) {
    case 'time':
      const unlockTime = detailData.unlock_conditions_unlockable_time
        ? formatStandard(detailData.unlock_conditions_unlockable_time)
        : '未知时间'
      return `需在 ${unlockTime} 之后`
    case 'location':
      const radius = detailData.unlock_conditions_unlockable_radius || 50
      return `需到达投递位置 ${radius} 米范围内`
    case 'password':
      return detailData.unlock_conditions_is_unlocked
        ? '密码已通过'
        : '需要输入密码'
  }
}
// #endregion

// #region props & emits
/**
 * 属性定义
 * @param {Boolean} showModal - 是否显示模态框
 * @param {Object} detailData - 胶囊详情数据 (新结构)
 */
const props = defineProps({
  showModal: {
    type: Boolean,
    required: true,
  },
  detailData: {
    type: Object,
    required: true,
    default: () => ({
      id: null,
      title: '',
      visibility: 'school',
      content: '',
      created_at: null,
      status: 'draft',
      tags: [],
      // location
      latitude: null,
      longitude: null,
      address: '未知位置',
      // unlock_conditions
      unlock_conditions_type: 'none',
      unlock_conditions_password: '',
      unlock_conditions_radius: 50,
      unlock_conditions_is_unlocked: false,
      unlock_conditions_unlockable_time: null,
      // stats
      view_count: 0,
      like_count: 0,
      comment_count: 0,
      unlock_count: 0,
      is_liked: false,
      is_collected: false,
      // media_files
      media_files: [],
      // other
      is_mine: false,
    }),
  },
})

/**
 * 事件定义
 * @emit close - 关闭模态框
 * @emit edit - 编辑胶囊 (参数: id)
 * @emit share - 分享胶囊 (参数: 完整数据对象)
 */
const emit = defineEmits(['close', 'edit', 'share'])

// --- 事件处理函数 ---
const handleClose = () => {
  activeMediaIndex.value = null // 关闭大弹窗时重置媒体索引
  emit('close')
}

const handleEdit = (id) => {
  emit('edit', id)
}

const handleShare = (data) => {
  emit('share', data)
}
// #endregion

const activeMediaIndex = ref(null)

const currentMedia = computed(() => {
  if (activeMediaIndex.value === null) return null
  return props.detailData.media_files[activeMediaIndex.value]
})

// 在 script setup 中增加
const isPlaying = ref(false)
const audioPlayer = ref(null)

// 当切换媒体时，重置播放状态
watch(activeMediaIndex, () => {
  isPlaying.value = false
})
</script>

<style scoped>
/* 模态框基础样式，与您原有样式保持一致 */
.capsule-detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
  visibility: hidden;
  opacity: 0;
  transition: opacity 0.3s, visibility 0.3s;
}

.capsule-detail-modal.active {
  visibility: visible;
  opacity: 1;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
}

.modal-panel {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  z-index: 1001;
  transform: translateY(20px);
  transition: transform 0.3s ease-out;
}

.capsule-detail-modal.active .modal-panel {
  transform: translateY(0);
}

.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: #888;
}

.modal-body {
  padding: 20px;
  overflow-y: auto; /* 允许内容区滚动 */
  flex-grow: 1;
}

.divider {
  border: 0;
  height: 1px;
  background: #eee;
  margin: 15px 0;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 20px;
  margin-bottom: 20px;
  font-size: 14px;
  color: #555;
}

.meta-item i {
  margin-right: 5px;
  color: #6c8cff;
}

.detail-unlock-condition {
  font-size: 15px;
  color: #333;
  display: flex;
  align-items: center;
}

.detail-unlock-condition i {
  margin-right: 5px;
  color: #ff9800; /* 解锁条件用不同的颜色区分 */
}

.unlocked-status {
  color: #4caf50; /* 绿色 */
  margin-left: 10px;
  font-weight: bold;
}

.locked-status {
  color: #f44336; /* 红色 */
  margin-left: 10px;
  font-weight: bold;
}

.detail-media-preview {
  position: relative;
  margin-bottom: 20px;
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  max-height: 300px; /* 限制预览高度 */
}

.detail-img-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.media-count {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.media-tip {
  position: absolute;
  top: 10px;
  left: 10px;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.8);
  padding: 4px 8px;
  border-radius: 4px;
  color: #333;
}

.detail-content {
  line-height: 1.6;
  color: #333;
  margin-bottom: 20px;
  white-space: pre-wrap; /* 保持换行和空格 */
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.tag-item {
  background: #f0f4ff;
  color: #6c8cff;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 12px;
}

.detail-stats {
  /* border-top: 1px solid #eee; */
  padding-top: 5px; /* 调整为更紧凑 */
  display: flex;
  flex-wrap: wrap; /* 允许换行 */
  gap: 10px 20px;
  font-size: 14px;
  color: #555;
}

.stat-item i {
  margin-right: 5px;
}

.fa-heart.liked {
  color: #ff4d4f;
}
.fa-bookmark.collected {
  color: #ffc107;
}

.modal-actions {
  padding: 16px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 按钮基础样式 (简化) */
.btn {
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
  border: 1px solid transparent;
}

.btn.ghost {
  background: none;
  border-color: #ccc;
  color: #555;
}

.btn.primary {
  background: #6c8cff;
  color: white;
}
.btn.primary:hover {
  background: #5a7cff;
}
/* 内部媒体查看器样式 */
.internal-media-viewer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1001; /* 高于 modal-body */
  display: flex;
  justify-content: center;
  align-items: center;
}

.viewer-overlay {
  position: absolute;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.9);
}

.viewer-content {
  position: relative;
  z-index: 2;
  width: 90%;
  max-height: 80%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.media-container {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.full-media {
  max-width: 100%;
  max-height: 70vh;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.audio-wrapper {
  background: white;
  padding: 30px;
  border-radius: 12px;
  text-align: center;
}

.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  padding: 15px;
  cursor: pointer;
  border-radius: 50%;
}
.nav-btn.prev {
  left: -20px;
}
.nav-btn.next {
  right: -20px;
}

.viewer-close {
  position: absolute;
  top: -40px;
  right: 0;
  color: white;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}

.viewer-footer {
  margin-top: 15px;
  color: white;
  font-size: 14px;
}

/* 音频特有容器 */
.audio-player-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.audio-card {
  background: #ffffff;
  border-radius: 20px;
  padding: 30px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.audio-visualizer {
  width: 120px;
  height: 120px;
  background: #333;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
  border: 8px solid #f0f0f0;
  position: relative;
}

.audio-visualizer .disc {
  color: #6c8cff;
  font-size: 40px;
}

/* 播放时的旋转动画 */
.is-playing .disc {
  animation: rotateDisc 3s linear infinite;
}

@keyframes rotateDisc {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.audio-info {
  text-align: center;
  margin-bottom: 25px;
}

.audio-title {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.audio-subtitle {
  margin: 5px 0 0;
  font-size: 13px;
  color: #999;
}

/* 让原生控制条宽度自适应 */
.custom-audio-element {
  width: 100%;
  height: 40px;
  border-radius: 8px;
}
/* 预览图上的类型标识 */
.media-type-badge {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.4);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  pointer-events: none; /* 不干扰点击 */
}

/* 音频光盘封面样式优化 */
.audio-visualizer .disc {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 4px solid #333;
  overflow: hidden; /* 确保缩略图不溢出圆圈 */
}

/* 播放时的旋转动画 */
.is-playing .disc {
  animation: rotateDisc 5s linear infinite;
}
</style>
