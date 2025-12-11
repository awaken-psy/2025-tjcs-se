<template>
  <!-- 统计图表：统一月度/年度统计图表样式，支持自定义数据和图例，可复用在校园活动页 -->
  <div class="stats-chart">
    <!-- 图表头部（标题+图例） -->
    <div class="chart-header">
      <span class="chart-title">{{ chartTitle }}</span>
      <span
        v-if="legendList.length > 0"
        class="chart-legend"
      >
        <span 
          v-for="(legend, idx) in legendList"
          :key="idx"
          class="legend-item"
        >
          <span
            class="legend-dot"
            :style="{ background: legend.color }"
          />
          {{ legend.label }}
        </span>
      </span>
    </div>

    <!-- 图表主体（柱状图） -->
    <div class="chart-bars">
      <div 
        v-for="(item, idx) in chartData"
        :key="idx"
        class="chart-bar-group"
        @click="$emit('bar-click', item)"
      >
        <!-- 坐标轴标签（如月份） -->
        <span class="bar-label">{{ item[labelKey] }}</span>
        
        <!-- 多柱状图（支持多个数据字段） -->
        <div class="bar-container">
          <div 
            v-for="(field, fIdx) in dataFields"
            :key="fIdx"
            class="chart-bar"
            :style="{ 
              height: `${getBarHeight(item[field.key])}%`, 
              background: field.color,
              marginLeft: fIdx > 0 ? '4px' : '0'
            }"
          >
            <!-- 数值标签 -->
            <span class="bar-value">{{ item[field.key] }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

/**
 * 组件作用：
 * 1. 统一统计图表渲染逻辑，替代校园活动页中重复的月度统计图表代码
 * 2. 支持自定义数据字段、颜色、图例、坐标轴标签，适配不同页面的统计需求
 * 3. 统一图表交互（如点击柱状图触发事件），避免重复编写交互逻辑
 * 
 * 组件接口（Props）：
 * @param {String} chartTitle - 图表标题（如"2025年度统计"，默认空）
 * @param {Array} chartData - 图表数据（必传，数组每项为一个坐标轴的数据）
 * @param {Array} dataFields - 数据字段配置（必传，定义每个柱状图的字段、颜色、图例）
 *   格式：[{ key: 'capsuleCount', color: '#6c8cff', legend: '胶囊数' }, ...]
 * @param {String} labelKey - 坐标轴标签字段（如"month"，必传）
 * @param {Array} legendList - 图例列表（可选，优先级高于dataFields的legend）
 * @param {Number} maxHeight - 柱状图最大高度占比（默认100，单位%）
 * 
 * 组件事件（Emits）：
 * @emit bar-click - 点击柱状图时触发，参数为该坐标轴的完整数据（Object）
 */
const props = defineProps({
  chartTitle: {
    type: String,
    default: ''
  },
  chartData: {
    type: Array,
    required: true,
    validator: (val) => val.length > 0
  },
  dataFields: {
    type: Array,
    required: true,
    validator: (val) => val.every(field => field.key && field.color)
  },
  labelKey: {
    type: String,
    required: true
  },
  legendList: {
    type: Array,
    default: () => []
  },
  maxHeight: {
    type: Number,
    default: 100,
    validator: (val) => val > 0 && val <= 100
  }
})

const emit = defineEmits(['bar-click'])

/**
 * 计算属性：处理图例列表（优先用props.legendList，否则从dataFields提取）
 */
const legendList = computed(() => {
  if (props.legendList.length > 0) return props.legendList
  return props.dataFields
    .filter(field => field.legend)
    .map(field => ({ label: field.legend, color: field.color }))
})

/**
 * 辅助函数：计算柱状图高度（按数据最大值比例计算）
 * @param {Number} value - 数据值
 * @returns {Number} 高度占比（%）
 */
const getBarHeight = (value) => {
  // 找到所有数据中的最大值
  const allValues = props.chartData.flatMap(item => 
    props.dataFields.map(field => item[field.key] || 0)
  )
  const maxValue = Math.max(...allValues, 1) // 避免除以0
  // 计算高度（不超过maxHeight）
  return Math.min((value / maxValue) * props.maxHeight, props.maxHeight)
}
</script>

<style scoped>
/* 统计图表基础样式 */
.stats-chart {
  margin-top: 12px;
  padding: 12px;
  background: var(--card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

/* 图表头部 */
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 14px;
  color: #374151;
  flex-wrap: wrap;
  gap: 8px;
}

.chart-title {
  font-weight: 600;
}

/* 图例 */
.chart-legend {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--muted);
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

/* 柱状图容器 */
.chart-bars {
  display: flex;
  gap: 16px;
  align-items: flex-end;
  height: 180px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(12, 18, 36, 0.08);
  overflow-x: auto;
  scrollbar-width: thin;
}

.chart-bars::-webkit-scrollbar {
  height: 6px;
}

.chart-bars::-webkit-scrollbar-thumb {
  background: rgba(108, 140, 255, 0.2);
  border-radius: 3px;
}

/* 单个坐标轴分组 */
.chart-bar-group {
  flex: 1;
  min-width: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.chart-bar-group:hover .chart-bar {
  opacity: 0.9;
}

/* 坐标轴标签 */
.bar-label {
  font-size: 12px;
  color: var(--muted);
  white-space: nowrap;
}

/* 柱状图容器 */
.bar-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: flex-end;
  gap: 4px;
}

/* 单个柱状图 */
.chart-bar {
  flex: 1;
  border-radius: 4px 4px 0 0;
  position: relative;
  transition: opacity 0.2s;
}

/* 柱状图数值标签 */
.bar-value {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  color: #374151;
  font-weight: 500;
  white-space: nowrap;
}

/* 设计令牌：复用全局变量 */
:root {
  --card: #ffffff;
  --muted: #6b7280;
  --shadow: 0 6px 18px rgba(12, 18, 36, 0.06);
  --radius: 12px;
}

/* 响应式适配：小屏幕调整间距 */
@media (max-width: 480px) {
  .chart-bars {
    gap: 8px;
  }
  
  .chart-bar-group {
    min-width: 40px;
  }
}
</style>