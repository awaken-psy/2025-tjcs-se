<template>
  <!-- 顶部导航栏：所有页面共用的顶部导航，包含品牌标识、搜索框、功能按钮 -->
  <header class="topbar">
    <!-- 品牌区域：点击跳转中央中枢页 -->
    <div
      class="brand"
      @click="$emit('go-hub')"
    >
      <div class="mark">
        时光
      </div>
      <div class="brand-text">
        <div class="title">
          {{ pageTitle }}
        </div>
        <div class="subtitle">
          {{ pageSubtitle }}
        </div>
      </div>
    </div>

    <!-- 工具区域：搜索框 + 功能按钮 -->
    <div class="toolbar">
      <!-- 搜索框：按需显示（部分页面不需要搜索） -->
      <input 
        v-if="showSearch" 
        v-model="searchValue" 
        class="search" 
        :placeholder="searchPlaceholder"
        @keydown.enter="$emit('search', searchValue)"
      >

      <!-- 右侧功能按钮：通过props传入，支持自定义 -->
      <div
        v-if="actions.length > 0"
        class="toolbar-actions"
      >
        <button 
          v-for="(action, idx) in actions" 
          :key="idx"
          :class="['btn', action.type === 'ghost' ? 'ghost' : '', action.size === 'small' ? 'small' : '']"
          @click="$emit('action-click', action.key)"
        >
          <span
            v-if="action.icon"
            class="action-icon"
          >{{ action.icon }}</span>
          <span>{{ action.text }}</span>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'

/**
 * 组件作用：
 * 1. 统一所有页面的顶部导航样式，避免重复开发
 * 2. 提供品牌标识、搜索框、自定义功能按钮的通用接口
 * 3. 触发通用事件（跳转中枢页、搜索、按钮点击），由父页面处理具体逻辑
 * 
 * 组件接口（Props）：
 * @param {String} pageTitle - 页面主标题（如"我的胶囊"、"地图"）
 * @param {String} pageSubtitle - 页面副标题（如"管理你创建的胶囊"）
 * @param {Boolean} showSearch - 是否显示搜索框（默认false）
 * @param {String} searchPlaceholder - 搜索框提示文字（默认"搜索..."）
 * @param {Array} actions - 右侧功能按钮列表，每一项格式：
 *   {
 *     key: String, // 按钮唯一标识（用于父页面区分点击事件）
 *     text: String, // 按钮文字
 *     type: String, // 按钮类型（"primary"或"ghost"，默认"primary"）
 *     size: String, // 按钮尺寸（"small"或"default"，默认"default"）
 *     icon: String // 按钮图标（可选，如"🔍"、"✚"）
 *   }
 * 
 * 组件事件（Emits）：
 * @emit go-hub - 点击品牌区域时触发，用于跳转中央中枢页
 * @emit search - 搜索框按回车时触发，参数为搜索内容（String）
 * @emit action-click - 点击右侧功能按钮时触发，参数为按钮key（String）
 */
const props = defineProps({
  pageTitle: {
    type: String,
    required: true
  },
  pageSubtitle: {
    type: String,
    default: ''
  },
  showSearch: {
    type: Boolean,
    default: false
  },
  searchPlaceholder: {
    type: String,
    default: '搜索...'
  },
  actions: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['go-hub', 'search', 'action-click'])

// 搜索框绑定值
const searchValue = ref('')
</script>

<style scoped>
/* 样式说明：复用原HTML的topbar样式，通过scoped隔离作用域 */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: transparent;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid rgba(12, 18, 36, 0.05);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.mark {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #7aa2ff, #6c8cff);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  box-shadow: 0 6px 18px rgba(12, 18, 36, 0.06);
  transition: transform 0.2s;
}

.mark:hover {
  transform: scale(1.05);
}

.brand-text .title {
  font-weight: 700;
  font-size: 1.2rem;
  color: #1e293b;
}

.brand-text .subtitle {
  font-size: 13px;
  color: var(--muted);
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search {
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid rgba(15, 23, 42, 0.1);
  min-width: 260px;
  background: white;
  transition: all 0.2s;
}

.search:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(108, 140, 255, 0.1);
}

.btn {
  background: var(--accent);
  color: white;
  padding: 10px 16px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 14px;
}

.btn:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(12, 18, 36, 0.06);
}

.btn.ghost {
  background: transparent;
  color: var(--accent);
  border: 1px solid rgba(108, 140, 255, 0.2);
}

.btn.ghost:hover {
  background: rgba(108, 140, 255, 0.05);
  border-color: var(--accent);
}

.btn.small {
  padding: 8px 12px;
  font-size: 13px;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
}

.action-icon {
  font-size: 16px;
}

/* 设计令牌：复用原HTML的全局变量，确保样式统一 */
:root {
  --bg: #f5f8ff;
  --card: #ffffff;
  --muted: #6b7280;
  --accent: #6c8cff;
  --accent-hover: #5a7cff;
  --shadow: 0 6px 18px rgba(12, 18, 36, 0.06);
}
</style>