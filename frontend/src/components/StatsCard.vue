<template>
  <div class="stats-card">
    <!-- 图标占位（可后续替换为 Icon 组件） -->
    <div
      class="stats-icon"
      :style="{ backgroundColor: iconBgColor }"
    >
      {{ icon }}
    </div>
    <!-- 统计内容 -->
    <div class="stats-content">
      <div class="stats-label">
        {{ label }}
      </div>
      <div class="stats-value">
        {{ value }}
      </div>
      <!-- 趋势提示（可选） -->
      <div
        v-if="trend"
        class="stats-trend"
        :class="trendType"
      >
        {{ trend }}
      </div>
    </div>
  </div>
</template>

<script setup>

// 组件Props：支持外部传入自定义内容
const props = defineProps({
  label: {
    type: String,
    required: true, // 统计项名称（如“已创建胶囊”）
  },
  value: {
    type: [String, Number],
    required: true, // 统计数值（如“12”）
  },
  icon: {
    type: String,
    default: '📊', // 默认图标（可替换为 SVG/Icon 组件）
  },
  iconBgColor: {
    type: String,
    default: '#e6f7ff', // 图标背景色
  },
  trend: {
    type: String,
    default: '', // 趋势文本（如“+2 今日”）
  },
  trendType: {
    type: String,
    default: 'up', // 趋势类型：up（上升）/ down（下降）
    validator: (val) => ['up', 'down'].includes(val),
  },
})
</script>

<style scoped>
.stats-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  gap: 12px;
}

.stats-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.stats-content {
  flex: 1;
}

.stats-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
}

.stats-value {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.stats-trend {
  font-size: 12px;
  margin-top: 4px;
}

.stats-trend.up {
  color: #52c41a; 
}

.stats-trend.down {
  color: #ff4d4f; 
}
</style>