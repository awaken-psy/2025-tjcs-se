<template>
  <!-- 地图页：地理维度的胶囊探索与管理，支持定位、热力图、胶囊标记 -->
  <div class="map-page">
    <!-- 顶部导航（复用共用组件） -->
    <AppHeader
      page-title="时光胶囊 · 地图"
      page-subtitle="探索校园内的胶囊，定位后可查看附近内容"
      :show-search="true"
      search-placeholder="搜索地点/胶囊标题/标签..."
      :actions="[
        { key: 'create', text: '创建胶囊', icon: '✚', type: 'primary' },
        { key: 'filter', text: '筛选', icon: '🔍', type: 'ghost' },
        { key: 'help', text: '帮助', icon: '❓', type: 'ghost' }
      ]"
      @go-hub="handleGoHub"
      @search="handleSearch"
      @action-click="handleHeaderAction"
    />

    <!-- 主体内容：侧边筛选栏 + 地图容器 -->
    <div class="map-main">
      <!-- 侧边筛选栏 -->
      <div class="map-sidebar">
        <div class="filter-card">
          <h3 class="filter-title">
            胶囊筛选
          </h3>
          <!-- 可见性筛选 -->
          <div class="filter-group">
            <label class="filter-label">可见性</label>
            <div class="filter-options">
              <label class="option-item">
                <input 
                  v-model="filters.vis.public" 
                  type="checkbox"
                  @change="handleFilterChange"
                >
                校园公开
              </label>
              <label class="option-item">
                <input 
                  v-model="filters.vis.friend" 
                  type="checkbox"
                  @change="handleFilterChange"
                >
                好友可见
              </label>
              <label class="option-item">
                <input 
                  v-model="filters.vis.private" 
                  type="checkbox"
                  @change="handleFilterChange"
                >
                仅自己可见
              </label>
            </div>
          </div>

          <!-- 解锁类型筛选 -->
          <div class="filter-group">
            <label class="filter-label">解锁类型</label>
            <div class="filter-options">
              <label class="option-item">
                <input 
                  v-model="filters.unlock.time" 
                  type="checkbox"
                  @change="handleFilterChange"
                >
                时间触发
              </label>
              <label class="option-item">
                <input 
                  v-model="filters.unlock.location" 
                  type="checkbox"
                  @change="handleFilterChange"
                >
                地点触发
              </label>
              <label class="option-item">
                <input 
                  v-model="filters.unlock.event" 
                  type="checkbox"
                  @change="handleFilterChange"
                >
                事件触发
              </label>
            </div>
          </div>

          <!-- 时间筛选 -->
          <div class="filter-group">
            <label class="filter-label">时间范围</label>
            <select 
              v-model="filters.timeRange"
              class="filter-select"
              @change="handleFilterChange"
            >
              <option value="all">
                全部时间
              </option>
              <option value="week">
                最近一周
              </option>
              <option value="month">
                最近一月
              </option>
              <option value="year">
                最近一年
              </option>
            </select>
          </div>

          <!-- 重置筛选 -->
          <button 
            class="btn ghost small reset-btn"
            @click="resetFilters"
          >
            重置筛选
          </button>
        </div>

        <!-- 附近胶囊探索器 -->
        <NearbyCapsulesExplorer
          @capsule-select="handleCapsuleSelect"
          @unlock-request="handleUnlockRequest"
          @view-request="handleViewRequest"
        />
      </div>

      <!-- 地图容器（复用共用组件） -->
      <div class="map-container-wrap">
        <MapContainer
          :capsule-data="allCapsules"
          map-height="calc(100vh - 140px)"
          @view-capsule="handleViewCapsule"
          @nav-capsule="handleNavCapsule"
          @map-ready="handleMapReady"
        />
      </div>
    </div>
  </div>
  <CapsuleForm
    :is-show="showCapsuleForm"
    @close="showCapsuleForm = false"
    @submit="onCapsuleCreated"
  />
</template>

<script setup>
import CapsuleForm from '@/components/CapsuleForm.vue'
import NearbyCapsulesExplorer from '@/components/NearbyCapsulesExplorer.vue'
import { computed, onMounted, ref } from 'vue'
const showCapsuleForm = ref(false)

// 引入胶囊创建API - 使用 capsuleApi.js 中的函数
import { getCapsuleDetail } from '@/api/new/capsulesApi'
import { unlockCapsule } from '@/api/new/unlockApi'

import { formatRelative } from '@/utils/formatTime.js'
import { useRouter } from 'vue-router'
// 复用共用组件
import AppHeader from '@/components/AppHeader.vue'
import MapContainer from '@/components/MapContainer.vue'
// 引入页面专属API
import {
  getCapsuleMarkers,
  getHeatmapData,
  getUserLocation
} from '@/api/new/capsulesApi.js'

/**
 * 页面作用：
 * 1. 提供校园地图可视化，支持精确到米的用户定位
 * 2. 展示胶囊地理标记，支持筛选（可见性/解锁类型/时间）
 * 3. 提供热力图切换、胶囊导航、详情查看等交互功能
 * 
 * 依赖API：
 * 1. getCapsuleMarkers() - 获取胶囊地理标记数据
 * 2. getHeatmapData() - 获取热力图数据（用于切换热力图）
 * 3. getUserLocation() - 获取用户定位数据（精确到米）
 * 
 * 页面状态：
 * - allCapsules：所有胶囊原始数据
 * - filteredCapsules：筛选后的胶囊数据
 * - filters：筛选条件（可见性/解锁类型/时间范围/距离）
 * - userPos：用户当前位置（经纬度）
 */
const allCapsules = ref([])
const userPos = ref(null)
const filters = ref({
  // 可见性筛选
  vis: {
    public: true,
    friend: true,
    private: true
  },
  // 解锁类型筛选
  unlock: {
    time: true,
    location: true,
    event: true
  },
  // 时间范围筛选
  timeRange: 'all',
  // 距离范围（米）
  range: 1000
})


/**
 * 页面初始化：加载胶囊数据和用户定位
 */
onMounted(async() => {
  try {
    // 并行加载数据：胶囊标记 + 用户定位
    const [capsules, userLocation] = await Promise.all([
      getCapsuleMarkers(),
      getUserLocation()
    ])
    allCapsules.value = capsules
    userPos.value = userLocation
    // 加载热力图数据（暂存，地图容器需要时传入）
    const heatmapData = await getHeatmapData()
    console.log('热力图数据已加载：', heatmapData)
  } catch (error) {
    console.error('地图页初始化失败：', error)
    // 错误降级：设置空数据和默认位置
    allCapsules.value = []
    userPos.value = { lat: 39.900500, lng: 116.302000 }
  }
})

/**
 * 胶囊表单提交处理 - 使用 capsuleApi.js 中的创建函数
 */

// 只处理弹窗关闭和刷新地图，不再直接调用createCapsule，防止重复创建
const onCapsuleCreated = async() => {
  showCapsuleForm.value = false
  await refreshMapData()
}

/**
 * 刷新地图数据
 */
const refreshMapData = async() => {
  try {
    const capsules = await getCapsuleMarkers()
    allCapsules.value = capsules
  } catch (error) {
    console.error('刷新地图数据失败：', error)
  }
}

/**
 * 辅助函数：计算两点间距离（经纬度转米，Haversine公式）
 * @param {Number} lat1 - 点1纬度
 * @param {Number} lng1 - 点1经度
 * @param {Number} lat2 - 点2纬度
 * @param {Number} lng2 - 点2经度
 * @returns {Number} 距离（单位：米）
 */
const calculateDistance = (lat1, lng1, lat2, lng2) => {
  const R = 6371000 // 地球半径（米）
  const radLat1 = Math.PI * lat1 / 180
  const radLat2 = Math.PI * lat2 / 180
  const deltaLat = radLat2 - radLat1
  const deltaLng = Math.PI * (lng2 - lng1) / 180
  const a = Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
            Math.cos(radLat1) * Math.cos(radLat2) *
            Math.sin(deltaLng / 2) * Math.sin(deltaLng / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c // 距离（米）
}


/**
 * 顶部导航：返回中枢页
 */
const handleGoHub = () => {
  router.push({ name: 'HubViews' })
}

/**
 * 顶部导航：搜索功能
 * @param {String} keyword - 搜索关键词
 */
const handleSearch = (keyword) => {
  if (!keyword) return
  // 搜索逻辑：匹配标题/描述/标签
  const matched = allCapsules.value.filter(capsule => {
    const searchStr = `${capsule.title}${capsule.desc}${capsule.tags.join('')}`.toLowerCase()
    return searchStr.includes(keyword.toLowerCase())
  })
  if (matched.length > 0) {
    // 聚焦第一个匹配的胶囊
    handleFocusCapsule(matched[0].id)
  } else {
    alert(`未找到包含"${keyword}"的胶囊`)
  }
}

/**
 * 顶部导航：功能按钮点击
 * @param {String} key - 按钮标识
 */
const router = useRouter()
const handleHeaderAction = (key) => {
  switch (key) {
  case 'create':
    showCapsuleForm.value = true
    break
  case 'filter':
    // 切换侧边筛选栏显示/隐藏（移动端适配）
    const sidebar = document.querySelector('.map-sidebar')
    sidebar.style.display = sidebar.style.display === 'none' ? 'block' : 'none'
    break
  case 'help':
    alert('地图使用帮助：1. 点击定位按钮获取位置 2. 点击标记查看胶囊 3. 可切换热力图查看分布')
    break
  }
}

/**
 * 筛选条件变化：更新筛选后的数据
 */
const handleFilterChange = () => {
  // 计算属性会自动响应filters变化，无需额外操作
  console.log('筛选条件更新：', filters.value)
}

/**
 * 重置筛选条件
 */
const resetFilters = () => {
  filters.value = {
    vis: { public: true, friend: true, private: true },
    unlock: { time: true, location: true, event: true },
    timeRange: 'all',
    range: 1000
  }
}

/**
 * 地图容器：地图初始化完成回调
 * @param {Object} mapInstance - 真实地图实例（null为模拟模式）
 */
const handleMapReady = (mapInstance) => {
  console.log('地图初始化完成，实例：', mapInstance)
  // 可在这里添加地图加载后的额外逻辑（如添加控件、绑定事件）
}

/**
 * 查看胶囊详情
 * @param {String} capsuleId - 胶囊ID
 */
const handleViewCapsule = async (capsuleId) => {
  try {
    console.log('🔍 [地图页] 查看胶囊详情:', capsuleId)

    // 调用getCapsuleDetail获取完整详情
    const detail = await getCapsuleDetail(capsuleId)
    console.log('🔍 [地图页] 获取到的详情数据:', detail)

    if (detail) {
      // 使用alert显示胶囊详情信息
      const locationText = detail.location?.address ||
                          (detail.location?.latitude && detail.location?.longitude ?
                           `位置 (${detail.location.latitude.toFixed(6)}, ${detail.location.longitude.toFixed(6)})` :
                           '未知位置')

      const detailInfo = [
        `标题: ${detail.title}`,
        `内容: ${detail.content || '无内容'}`,
        `可见性: ${detail.visibility}`,
        `位置: ${locationText}`,
        `创建时间: ${formatRelative(detail.created_at)}`,
        `点赞数: ${detail.stats?.like_count || 0}`,
        `浏览数: ${detail.stats?.view_count || 0}`
      ].join('\n')

      alert(`📖 胶囊详情:\n\n${detailInfo}`)
    } else {
      alert('获取胶囊详情失败')
    }
  } catch (error) {
    console.error(`[地图页] 获取胶囊详情(${capsuleId})失败：`, error)
    alert('加载详情失败，请稍后重试')
  }
}

/**
 * 导航到胶囊位置
 * @param {String} capsuleId - 胶囊ID
 */
const handleNavCapsule = (capsuleId) => {
  const capsule = allCapsules.value.find(c => c.id === capsuleId)
  if (capsule) {
    alert(`导航至胶囊：${capsule.title}（经纬度：${capsule.lat}, ${capsule.lng}）`)
  }
}

/**
 * 处理NearbyCapsulesExplorer的胶囊选择事件
 */
const handleCapsuleSelect = (capsule) => {
  // 在地图上高亮显示该胶囊
  console.log('选中胶囊:', capsule)
  // 可以通知MapContainer组件聚焦到该胶囊位置
  handleViewCapsule(capsule.id)
}

/**
 * 处理胶囊解锁请求
 */
const handleUnlockRequest = async (capsule, userLocation) => {
  try {
    console.log('尝试解锁胶囊:', capsule.id, '用户位置:', userLocation)

    const result = await unlockCapsule({
      capsule_id: capsule.id,
      user_location: {
        latitude: userLocation.latitude,
        longitude: userLocation.longitude
      }
    })

    // 根据request拦截器逻辑，成功时直接返回data，失败时抛出异常
    if (result) {
      alert(`🎉 胶囊 "${capsule.title}" 解锁成功！`)
      // 刷新胶囊数据
      await refreshMapData()
    }
  } catch (error) {
    console.error('解锁胶囊失败:', error)
    // 安全地获取错误信息，避免undefined
    const errorMessage = error?.message || error?.data?.message || error?.response?.data?.message || '未知错误'
    alert(`❌ 解锁失败: ${errorMessage}`)
  }
}

/**
 * 处理查看胶囊请求
 */
const handleViewRequest = async (capsule) => {
  try {
    console.log('查看胶囊详情:', capsule.id)

    const result = await getCapsuleDetail(capsule.id)

    if (result.success) {
      // 显示胶囊详情（这里可以打开一个详情弹窗）
      console.log('胶囊详情:', result.data)
      alert(`📖 胶囊内容: ${result.data.content || '内容为空'}`)
    } else {
      alert(`❌ 获取胶囊详情失败: ${result.message}`)
    }
  } catch (error) {
    console.error('获取胶囊详情失败:', error)
    alert(`❌ 获取胶囊详情失败: ${error.message}`)
  }
}

/**
 * 聚焦胶囊（地图中心移至胶囊位置）
 * @param {String} capsuleId - 胶囊ID
 */
const handleFocusCapsule = (capsuleId) => {
  const capsule = allCapsules.value.find(c => c.id === capsuleId)
  if (capsule) {
    // 通知地图容器聚焦到该胶囊（后续通过组件事件实现）
    alert(`地图聚焦至胶囊：${capsule.title}`)
  }
}

</script>

<style scoped>
/* 页面整体样式 */
.map-page {
  background-color: var(--bg);
  min-height: 100vh;
}

/* 主体内容布局 */
.map-main {
  display: flex;
  flex-direction: row;
  height: calc(100vh - 80px);
  min-height: 400px;
  gap: 20px;
  padding: 0 20px 20px;
}

/* 侧边筛选栏 */
.map-sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 320px;
  flex-shrink: 0;
}

/* 筛选卡片 */
.filter-card {
  background: var(--card);
  border-radius: var(--radius);
  padding: 16px;
  box-shadow: var(--shadow);
}

.filter-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 16px 0;
  color: #1e293b;
}

.filter-group {
  margin-bottom: 16px;
}

.filter-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  color: #374151;
}

.filter-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #4b5563;
  cursor: pointer;
}

.option-item input {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.filter-select {
  width: 100%;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(12, 18, 36, 0.08);
  background: white;
  font-size: 13px;
  cursor: pointer;
}

.reset-btn {
  width: 100%;
  margin-top: 8px;
  color: var(--muted);
}

.reset-btn:hover {
  color: var(--danger);
  background: rgba(239, 68, 68, 0.05);
  border-color: rgba(239, 68, 68, 0.2);
}


/* 地图容器包裹层 */
.map-container-wrap {
  flex: 1 1 0%;
  min-width: 0;
  min-height: 400px;
  position: relative;
  z-index: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 按钮样式（复用全局设计） */
.btn {
  background: var(--accent);
  color: white;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  font-size: 14px;
}

.btn:hover {
  background: var(--accent-hover);
  box-shadow: var(--shadow);
}

.btn.ghost {
  background: transparent;
  color: var(--accent);
  border: 1px solid rgba(108, 140, 255, 0.2);
}

.btn.ghost:hover {
  background: var(--accent-light);
  border-color: var(--accent);
}

.btn.small {
  padding: 6px 10px;
  font-size: 12px;
}

/* 设计令牌 */
:root {
  --bg: #f5f8ff;
  --card: #ffffff;
  --muted: #6b7280;
  --accent: #6c8cff;
  --accent-hover: #5a7cff;
  --accent-light: rgba(108, 140, 255, 0.1);
  --danger: #ef4444;
  --shadow: 0 6px 18px rgba(12, 18, 36, 0.06);
  --radius: 12px;
  --radius-sm: 8px;
}

/* 响应式适配 */
@media (max-width: 1024px) {
  .map-main {
    grid-template-columns: 280px 1fr;
  }
}

@media (max-width: 768px) {
  .map-main {
    grid-template-columns: 1fr;
  }

  .map-sidebar {
    display: none;
    position: fixed;
    top: 70px;
    left: 20px;
    right: 20px;
    z-index: 90;
    background: var(--bg);
    padding: 20px;
    border-radius: var(--radius);
    box-shadow: var(--shadow-lg);
  }

  .map-sidebar.show {
    display: flex;
  }

  .map-container-wrap {
    order: -1;
  }

}
</style>

