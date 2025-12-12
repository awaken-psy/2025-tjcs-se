<template>
  <!-- 胶囊操作按钮组：统一胶囊的查看、点赞、编辑、删除、分享操作，支持根据权限显示不同按钮 -->
  <div
    class="capsule-actions"
    :class="viewMode === 'list' ? 'list-mode' : 'grid-mode'">
    <!-- 查看详情（所有页面通用） -->
    <button
      class="action-btn view-btn"
      :disabled="isProcessing.view"
      @click.stop="$emit('view', capsule.id)">
      <span v-if="isProcessing.view" class="loading-spinner small" />
      <span class="icon">👁️</span>
      详情
    </button>

    <!-- 点赞（所有页面通用） -->
    <button
      class="action-btn like-btn"
      :class="{ liked: capsule.liked }"
      :disabled="isProcessing.like"
      @click.stop="$emit('like', capsule.id)">
      <span v-if="isProcessing.like" class="loading-spinner small" />
      <span class="icon">{{ capsule.liked ? '❤️' : '🤍' }}</span>
      {{ capsule.like_count || 0 }}
    </button>

    <!-- 编辑（仅胶囊所有者可见，如我的胶囊页） -->
    <button
      v-if="isOwner"
      class="action-btn edit-btn"
      :disabled="isProcessing.edit"
      @click.stop="$emit('edit', capsule.id)">
      <span v-if="isProcessing.edit" class="loading-spinner small" />
      <span class="icon">✏️</span>
      编辑
    </button>

    <!-- 删除（仅胶囊所有者可见，如我的胶囊页） -->
    <button
      v-if="isOwner"
      class="action-btn delete-btn"
      :disabled="isProcessing.delete"
      @click.stop="$emit('delete', capsule.id)">
      <span v-if="isProcessing.delete" class="loading-spinner small" />
      <span class="icon">🗑️</span>
      删除
    </button>

    <!-- 分享（所有页面通用） -->
    <button
      class="action-btn share-btn"
      :disabled="isProcessing.share"
      @click.stop="$emit('share', capsule)">
      <span v-if="isProcessing.share" class="loading-spinner small" />
      <span class="icon">📤</span>
      分享
    </button>

    <!-- 收藏（所有页面通用，可选显示） -->
    <button
      v-if="showCollect"
      class="action-btn collect-btn"
      :class="{ collected: capsule.collected }"
      :disabled="isProcessing.collect || !isUnlocked"
      :title="!isUnlocked ? '您还未解锁此胶囊，无法收藏' : ''"
      @click.stop="$emit('collect', capsule.id)">
      <span v-if="isProcessing.collect" class="loading-spinner small" />
      <span class="icon">{{ capsule.collected ? '⭐' : '☆' }}</span>
      收藏
    </button>
  </div>
</template>

<script setup>
/**
 * 组件作用：
 * 1. 统一所有页面的胶囊操作逻辑，替代各页面中重复的按钮组代码
 * 2. 支持根据权限（isOwner）显示/隐藏编辑/删除按钮（仅所有者可见）
 * 3. 支持控制是否显示收藏按钮（showCollect），适配不同页面需求
 * 4. 统一处理按钮加载状态（isProcessing），避免重复的加载逻辑
 *
 * 组件接口（Props）：
 * @param {Object} capsule - 胶囊基础数据（必传）
 *   {
 *     id: String, // 胶囊ID
 *     like_count: Number, // 点赞数
 *     liked: Boolean, // 是否已点赞（前端状态）
 *     collected: Boolean, // 是否已收藏（前端状态）
 *     visibility: String // 可见性（用于权限判断）
 *   }
 * @param {Boolean} isOwner - 是否为胶囊所有者（控制编辑/删除显示，默认false）
 * @param {String} viewMode - 视图模式（grid/list，控制按钮布局，默认grid）
 * @param {Boolean} showCollect - 是否显示收藏按钮（默认true）
 * @param {Object} isProcessing - 按钮加载状态（key: 操作类型，value: 布尔值，默认空对象）
 *
 * 组件事件（Emits）：
 * @emit view - 点击查看详情时触发，参数为胶囊ID（String）
 * @emit like - 点击点赞时触发，参数为胶囊ID（String）
 * @emit edit - 点击编辑时触发，参数为胶囊ID（String）
 * @emit delete - 点击删除时触发，参数为胶囊ID（String）
 * @emit share - 点击分享时触发，参数为胶囊完整数据（Object）
 * @emit collect - 点击收藏时触发，参数为胶囊ID（String）
 */
const props = defineProps({
  capsule: {
    type: Object,
    required: true,
    // 优化：修改 validator 以包含 collected 字段
    validator: (val) => val.id && typeof val.like_count === 'number',
  },
  // 🌟 新增 prop
  isUnlocked: {
    type: Boolean,
    default: true, // 默认解锁，以防数据缺失
  },
  isOwner: {
    type: Boolean,
    default: false,
  },
  viewMode: {
    type: String,
    default: 'grid',
    validator: (val) => ['grid', 'list'].includes(val),
  },
  showCollect: {
    type: Boolean,
    default: true,
  },
  isProcessing: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['view', 'like', 'edit', 'delete', 'share', 'collect'])
</script>

<style scoped>
/* 基础按钮组布局 */
.capsule-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(12, 18, 36, 0.05);
}

/* 网格视图布局：按钮均分宽度 */
.capsule-actions.grid-mode {
  flex-wrap: wrap;
}

.grid-mode .action-btn {
  flex: 1;
  min-width: 80px;
}

/* 列表视图布局：按钮紧凑排列 */
.capsule-actions.list-mode {
  flex-wrap: nowrap;
}

.list-mode .action-btn {
  flex: none;
  padding: 6px 10px;
  font-size: 12px;
}

/* 单个按钮样式 */
.action-btn {
  background: transparent;
  border: 1px solid rgba(108, 140, 255, 0.2);
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s;
}

/* 图标样式 */
.icon {
  font-size: 14px;
  line-height: 1;
}

/* 按钮颜色区分 */
.view-btn {
  color: var(--accent);
  border-color: rgba(108, 140, 255, 0.3);
}

.view-btn:hover {
  background: var(--accent-light);
  border-color: var(--accent);
}

.like-btn {
  color: var(--muted);
}

.like-btn.liked {
  color: var(--danger);
  border-color: rgba(239, 68, 68, 0.3);
}

.like-btn:hover:not(.liked) {
  color: var(--danger);
  background: rgba(239, 68, 68, 0.05);
  border-color: rgba(239, 68, 68, 0.2);
}

.edit-btn {
  color: var(--warning);
  border-color: rgba(245, 158, 11, 0.3);
}

.edit-btn:hover {
  background: rgba(245, 158, 11, 0.05);
  border-color: var(--warning);
}

.delete-btn {
  color: var(--danger);
  border-color: rgba(239, 68, 68, 0.3);
}

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.05);
  border-color: var(--danger);
}

.share-btn {
  color: var(--success);
  border-color: rgba(16, 185, 129, 0.3);
}

.share-btn:hover {
  background: rgba(16, 185, 129, 0.05);
  border-color: var(--success);
}

.collect-btn {
  color: var(--accent);
  border-color: rgba(108, 140, 255, 0.3);
}

.collect-btn.collected {
  color: var(--accent-hover);
  border-color: var(--accent);
}

.collect-btn:hover:not(.collected) {
  background: var(--accent-light);
  border-color: var(--accent);
}

/* 加载动画（复用全局样式，适配小尺寸） */
.loading-spinner.small {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(108, 140, 255, 0.2);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 设计令牌：复用全局变量 */
:root {
  --accent: #6c8cff;
  --accent-hover: #5a7cff;
  --accent-light: rgba(108, 140, 255, 0.1);
  --danger: #ef4444;
  --warning: #f59e0b;
  --success: #10b981;
  --muted: #6b7280;
  --radius-sm: 8px;
}

/* 响应式适配：小屏幕下网格视图按钮换行 */
@media (max-width: 480px) {
  .grid-mode .action-btn {
    flex: 1 1 45%; /* 小屏幕每行2个按钮 */
  }
}
</style>
