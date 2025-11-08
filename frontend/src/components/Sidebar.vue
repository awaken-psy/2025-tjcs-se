<template>
  <!-- 侧边导航栏：多个页面（中枢/地图/我的胶囊等）共用的导航入口 -->
  <aside class="sidebar">
    <!-- 导航列表：通过props动态渲染导航项 -->
    <nav
      class="nav"
      aria-label="主导航"
    >
      <button
        v-for="(item, idx) in navItems"
        :key="idx"
        class="nav-item"
        :class="{ active: currentActive === item.key }"
        @click="$emit('nav-change', item.key)"
      >
        <div class="nav-icon">
          {{ item.icon }}
        </div>
        <span class="nav-text">{{ item.label }}</span>
        <!-- 导航项徽章（如待审核数量） -->
        <span
          v-if="item.badge && item.badge.count > 0"
          class="nav-badge"
          :style="{ backgroundColor: item.badge.color }"
        >
          {{ item.badge.count }}
        </span>
      </button>
    </nav>

    <!-- 导航提示（可选） -->
    <div
      v-if="tipText"
      class="nav-tip"
    >
      {{ tipText }}
    </div>
  </aside>
</template>

<script setup>
/**
 * 组件作用：
 * 1. 统一多页面的侧边导航样式，支持动态配置导航项
 * 2. 提供导航选中状态管理、徽章提示（如待审核数量）
 * 3. 触发导航切换事件，由父页面处理路由跳转逻辑
 * 
 * 组件接口（Props）：
 * @param {Array} navItems - 导航项列表，每一项格式：
 *   {
 *     key: String, // 导航项唯一标识（如"dashboard"、"map"）
 *     label: String, // 导航项文字（如"仪表盘"、"地图"）
 *     icon: String, // 导航项图标（如"🗺️"、"✚"）
 *     badge: Object // 徽章配置（可选）：{ count: Number, color: String }
 *   }
 * @param {String} currentActive - 当前选中的导航项key（用于回显选中状态）
 * @param {String} tipText - 导航底部提示文字（可选，如"点击创建胶囊前往编辑页"）
 * 
 * 组件事件（Emits）：
 * @emit nav-change - 点击导航项时触发，参数为选中导航项的key（String）
 */
const props = defineProps({
  navItems: {
    type: Array,
    required: true,
    validator: (value) => {
      // 校验导航项必须包含key、label、icon
      return value.every(item => item.key && item.label && item.icon)
    }
  },
  currentActive: {
    type: String,
    required: true
  },
  tipText: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['nav-change'])
</script>

<style scoped>
/* 样式说明：复用原HTML的sidebar样式，scoped隔离作用域 */
.sidebar {
  background: var(--card);
  padding: 20px 0;
  box-shadow: var(--shadow);
  border-right: 1px solid rgba(12, 18, 36, 0.05);
  overflow-y: auto;
  min-width: 220px;
  position: sticky;
  top: 0;
  height: 100vh;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0 16px;
}

.nav-item {
  background: transparent;
  border: none;
  text-align: left;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #64748b;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-item:hover {
  background: var(--accent-light);
  color: var(--accent);
}

.nav-item.active {
  background: var(--accent);
  color: white;
  box-shadow: 0 4px 12px rgba(108, 140, 255, 0.2);
}

.nav-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.nav-text {
  flex: 1;
  white-space: nowrap;
}

.nav-badge {
  margin-left: auto;
  color: white;
  border-radius: 10px;
  padding: 2px 6px;
  font-size: 11px;
  font-weight: 500;
}

.nav-tip {
  margin: 20px 16px 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.4;
}

/* 设计令牌：复用全局样式变量 */
:root {
  --bg: #f5f8ff;
  --card: #ffffff;
  --muted: #6b7280;
  --accent: #6c8cff;
  --accent-light: rgba(108, 140, 255, 0.1);
  --shadow: 0 6px 18px rgba(12, 18, 36, 0.06);
}
</style>