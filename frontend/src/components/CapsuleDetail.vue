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
          <span v-if="detailData.time" class="meta-item">
            <i class="fas fa-clock" /> **投递时间：**
            {{ formatStandard(detailData.time) }}
          </span>
          <span v-if="detailData.vis" class="meta-item">
            <i class="fas fa-eye" /> **可见性：**
            {{ getVisText(detailData.vis) }}
          </span>
          <span class="meta-item">
            <i :class="getUnlockIcon(detailData.unlockType)" />
            **解锁条件：**
            {{ getUnlockText(detailData.unlockType, detailData.unlockValue) }}
          </span>
          <span class="meta-item">
            <i class="fas fa-map-marker-alt" /> **投递位置：**
            {{ detailData.location || '未知位置' }}
          </span>
        </div>

        <div
          v-if="
            detailData.media_files && detailData.media_files.length > 0
          "
          class="detail-media-preview">
          <img
            :src="detailData.media_files[0].url"
            :alt="detailData.title + '媒体预览'"
            class="detail-img-preview"
            @click="handleOpenMediaViewer(detailData.media_files)" />
          <div
            v-if="detailData.media_files.length > 1"
            class="media-count">
            <i class="fas fa-images" /> +{{ detailData.media_files.length - 1 }}
          </div>
          <div class="media-tip">**点击图片查看所有媒体文件**</div>
        </div>

        <div class="detail-desc">
          **内容描述：**
          {{ detailData.desc || '无内容描述' }}
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

        <div class="detail-stats">
          <span class="stat-item">
            <i
              class="fas fa-heart"
              :class="{ liked: detailData.liked }" />
            {{ detailData.likes || 0 }} 点赞
          </span>
          <span class="stat-item">
            <i class="fas fa-eye" />
            {{ detailData.views || 0 }} 浏览
          </span>
          <span class="stat-item">
            <i
              class="fas fa-bookmark"
              :class="{ collected: detailData.collected }" />
            {{ detailData.collected ? '已收藏' : '未收藏' }}
          </span>
        </div>
      </div>

      <div class="modal-actions">
        <button class="btn ghost" @click="handleClose">关闭</button>
        <button
          class="btn primary"
          v-if="detailData.is_mine"
          @click="handleEdit(detailData.id)">
          编辑胶囊
        </button>
        <button
          class="btn ghost"
          @click="handleShare(detailData)">
          <i class="fas fa-share-alt" /> 分享
        </button>
        </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

// 假设这些辅助函数从外部导入或在组件内定义
// 实际项目中，如果这些函数是通用的，应放在 utilities 文件中。

// ❗️ 示例：请用您项目中的实际辅助函数替换这些占位符
const formatStandard = (isoStr) => isoStr ? new Date(isoStr).toLocaleString() : 'N/A';
const getVisText = (vis) => {
  switch (vis) {
    case 'private': return '仅自己可见';
    case 'friends': return '好友可见';
    default: return '校园公开';
  }
};
const getUnlockIcon = (type) => {
  switch (type) {
    case 'time': return 'fas fa-hourglass-half';
    case 'location': return 'fas fa-map-pin';
    case 'event': return 'fas fa-calendar-alt';
    default: return 'fas fa-lock-open';
  }
};
const getUnlockText = (type, value) => {
  if (!type) return '无限制';
  // 复杂的逻辑可能需要完整的辅助函数
  return `类型: ${type}，值: ${value || 'N/A'}`;
};
// ❗️ 示例辅助函数结束

/**
 * 属性定义
 * @param {Boolean} isShow - 是否显示模态框
 * @param {Object} detailData - 胶囊详情数据
 */
const props = defineProps({
  showModal: {
    type: Boolean,
    required: true
  },
  detailData: {
    type: Object,
    required: true,
    // 基础校验，确保传入的对象包含必要字段
    default: () => ({ 
      title: '', 
      is_mine: false,
      media_files: [],
      tags: [],
      // 必须包含用于映射的字段
      unlockType: 'none', 
      unlockValue: ''
    })
  }
});

/**
 * 事件定义
 * @emit close - 关闭模态框
 * @emit edit - 编辑胶囊 (参数: id)
 * @emit share - 分享胶囊 (参数: 完整数据对象)
 * @emit openMedia - 打开媒体查看器 (参数: 媒体文件列表)
 */
const emit = defineEmits(['close', 'edit', 'share', 'openMedia']);

// --- 事件处理函数 ---

const handleClose = () => {
  emit('close');
};

const handleEdit = (id) => {
  emit('edit', id);
};

const handleShare = (data) => {
  emit('share', data);
};

const handleOpenMediaViewer = (mediaFiles) => {
  emit('openMedia', mediaFiles);
};

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

.detail-desc {
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
  border-top: 1px solid #eee;
  padding-top: 15px;
  display: flex;
  gap: 20px;
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
</style>