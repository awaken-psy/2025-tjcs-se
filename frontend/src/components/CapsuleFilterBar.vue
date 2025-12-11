<template>
  <!-- 胶囊筛选控制栏：统一胶囊列表的筛选（可见性、搜索）、排序、视图切换逻辑，支持扩展筛选项 -->
  <div class="capsule-filter-bar">
    <!-- 左侧筛选区（可见性+搜索） -->
    <div class="filter-left">
      <!-- 可见性筛选（支持传入选项，适配不同页面） -->
      <select 
        v-if="showVisibilityFilter"
        v-model="currentVis"
        class="filter-select vis-select"
        @change="$emit('filter-change', { type: 'vis', value: currentVis })"
      >
        <option value="public">
          公开可见
        </option>
        <option value="friends">
          好友可见
        </option>
        <option value="private">
          仅自己可见
        </option>
      </select>

      <!-- 搜索框（可选显示） -->
      <input
        v-if="showSearch"
        v-model="searchValue"
        class="filter-search"
        :placeholder="searchPlaceholder"
        @keydown.enter="$emit('search', searchValue)"
        @input="$emit('search-input', searchValue)"
      >
    </div>

    <!-- 右侧控制区（排序+视图切换） -->
    <div class="filter-right">
      <!-- 排序下拉 -->
      <select 
        v-model="currentSort"
        class="filter-select sort-select"
        @change="$emit('sort-change', currentSort)"
      >
        <option value="newest">
          最新创建
        </option>
        <option value="oldest">
          最早创建
        </option>
        <option value="popular">
          最多点赞
        </option>
      </select>

      <!-- 视图切换按钮 -->
      <div class="view-buttons">
        <button 
          class="view-btn" 
          :class="{ active: currentViewMode === 'grid' }"
          @click="$emit('view-mode-change', 'grid')"
        >
          <i class="fas fa-th" /> 网格
        </button>
        <button 
          class="view-btn" 
          :class="{ active: currentViewMode === 'list' }"
          @click="$emit('view-mode-change', 'list')"
        >
          <i class="fas fa-list" /> 列表
        </button>
      </div>

      <!-- 重置筛选按钮（可选显示） -->
      <button 
        v-if="showResetBtn"
        class="reset-btn"
        @click="$emit('reset-filter')"
      >
        <i class="fas fa-redo" /> 重置
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

/**
 * 组件作用：
 * 1. 统一胶囊列表的筛选、排序、视图切换逻辑，替代MyCapsuleView等页面的重复控制栏代码
 * 2. 支持配置化：控制是否显示可见性筛选、搜索框、重置按钮，适配不同页面需求
 * 3. 标准化事件：筛选、排序、视图切换事件统一命名，降低页面适配成本
 * 
 * 组件接口（Props）：
 * @param {String} currentVis - 当前可见性筛选值（public/friends/private）
 * @param {String} currentSort - 当前排序值（newest/oldest/popular，默认newest）
 * @param {String} currentViewMode - 当前视图模式（grid/list，默认grid）
 * @param {Boolean} showVisibilityFilter - 是否显示可见性筛选（默认true）
 * @param {Boolean} showSearch - 是否显示搜索框（默认true）
 * @param {Boolean} showResetBtn - 是否显示重置按钮（默认true）
 * @param {String} searchPlaceholder - 搜索框提示文字（默认"搜索胶囊..."）
 * 
 * 组件事件（Emits）：
 * @emit filter-change - 可见性筛选变化时触发，参数{ type: 'vis', value: 选中值 }
 * @emit sort-change - 排序变化时触发，参数为选中排序值（String）
 * @emit view-mode-change - 视图模式变化时触发，参数为选中模式（grid/list）
 * @emit search - 搜索框按回车时触发，参数为搜索关键词（String）
 * @emit search-input - 搜索框输入时实时触发，参数为当前输入值（String）
 * @emit reset-filter - 点击重置按钮时触发，无参数
 */
const props = defineProps({
  currentVis: {
    type: String,
    default: 'public',
    validator: (val) => ['public', 'friends', 'private'].includes(val)
  },
  currentSort: {
    type: String,
    default: 'newest',
    validator: (val) => ['newest', 'oldest', 'popular'].includes(val)
  },
  currentViewMode: {
    type: String,
    default: 'grid',
    validator: (val) => ['grid', 'list'].includes(val)
  },
  showVisibilityFilter: {
    type: Boolean,
    default: true
  },
  showSearch: {
    type: Boolean,
    default: true
  },
  showResetBtn: {
    type: Boolean,
    default: true
  },
  searchPlaceholder: {
    type: String,
    default: '搜索胶囊标题/标签...'
  }
})

const emit = defineEmits(['filter-change', 'sort-change', 'view-mode-change', 'search', 'search-input', 'reset-filter'])

// 内部状态：确保props变化时同步内部值
const currentVis = ref(props.currentVis)
const currentSort = ref(props.currentSort)
const currentViewMode = ref(props.currentViewMode)
const searchValue = ref('')

// 监听props变化，同步内部状态
watch(() => props.currentVis, (newVal) => {
  currentVis.value = newVal
}, { immediate: true })

watch(() => props.currentSort, (newVal) => {
  currentSort.value = newVal
}, { immediate: true })

watch(() => props.currentViewMode, (newVal) => {
  currentViewMode.value = newVal
}, { immediate: true })

// 重置筛选：清空搜索框+触发父页面重置
const handleReset = () => {
  searchValue.value = ''
  emit('reset-filter')
}
</script>

<style scoped>
/* 控制栏整体样式 */
.capsule-filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  gap: 16px;
  flex-wrap: wrap;
}

/* 左侧筛选区（可见性+搜索） */
.filter-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 240px;
}

/* 筛选下拉框 */
.filter-select {
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(12, 18, 36, 0.08);
  background: white;
  font-size: 14px;
  cursor: pointer;
  min-width: 140px;
}

.vis-select {
  min-width: 160px;
}

/* 搜索框 */
.filter-search {
  flex: 1;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(12, 18, 36, 0.08);
  background: white;
  font-size: 14px;
  min-width: 200px;
}

.filter-search:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(108, 140, 255, 0.1);
}

/* 右侧控制区（排序+视图切换+重置） */
.filter-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 视图切换按钮 */
.view-buttons {
  display: flex;
  gap: 8px;
}

.view-btn {
  background: transparent;
  border: 1px solid rgba(108, 140, 255, 0.2);
  color: var(--muted);
  padding: 6px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  transition: all 0.2s;
}

.view-btn:hover {
  background: var(--accent-light);
  color: var(--accent);
  border-color: var(--accent);
}

.view-btn.active {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}

/* 重置按钮 */
.reset-btn {
  background: transparent;
  border: 1px solid rgba(108, 140, 255, 0.2);
  color: var(--accent);
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  transition: all 0.2s;
}

.reset-btn:hover {
  background: var(--accent-light);
  border-color: var(--accent);
}

/* 设计令牌：复用全局变量 */
:root {
  --card: #ffffff;
  --accent: #6c8cff;
  --accent-light: rgba(108, 140, 255, 0.1);
  --muted: #6b7280;
  --shadow: 0 6px 18px rgba(12, 18, 36, 0.06);
  --radius: 12px;
  --radius-sm: 8px;
}

/* 响应式适配：小屏幕下换行 */
@media (max-width: 768px) {
  .filter-left {
    min-width: 100%;
  }
  
  .filter-right {
    min-width: 100%;
    justify-content: space-between;
  }
}
</style>