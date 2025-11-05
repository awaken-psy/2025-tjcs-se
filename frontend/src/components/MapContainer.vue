<template>
  <div class="map-container">
    <!-- 地图主体 -->
    <div 
      ref="mapRef" 
      class="map-dom"
      :style="{ height: mapHeight }"
    >
      <!-- 通知栏 -->
      <div
        v-if="showNotification"
        class="notification-bar"
      >
        <div class="notification-content">
          <i
            class="fas"
            :class="notificationIcon"
          />
          <span>{{ notificationText }}</span>
        </div>
        <button
          class="notification-close"
          @click="hideNotification"
        >
          ✕
        </button>
      </div>

      <!-- 地图SVG -->
      <svg
        class="map-svg"
        :viewBox="svgViewBox"
        xmlns="http://www.w3.org/2000/svg"
      >
        <!-- 渐变背景 -->
        <defs>
          <linearGradient
            id="map-bg"
            x1="0%"
            y1="0%"
            x2="100%"
            y2="100%"
          >
            <stop
              offset="0%"
              stop-color="#e6f2ff"
            />
            <stop
              offset="50%"
              stop-color="#f0f7ff"
            />
            <stop
              offset="100%"
              stop-color="#e6f2ff"
            />
          </linearGradient>
          
          <!-- 道路网格 -->
          <pattern
            id="road-grid"
            width="80"
            height="80"
            patternUnits="userSpaceOnUse"
          >
            <rect
              width="80"
              height="80"
              fill="#f8fafc"
            />
            <path
              d="M40 0 L40 80"
              stroke="#e2e8f0"
              stroke-width="1.5"
            />
            <path
              d="M0 40 L80 40"
              stroke="#e2e8f0"
              stroke-width="1.5"
            />
          </pattern>
          
          <!-- 标记样式 -->
          <filter
            id="marker-shadow"
            x="-50%"
            y="-50%"
            width="200%"
            height="200%"
          >
            <feDropShadow
              dx="0"
              dy="2"
              stdDeviation="3"
              flood-color="rgba(0,0,0,0.2)"
            />
          </filter>
        </defs>

        <!-- 地图背景 -->
        <rect
          width="1200"
          height="800"
          fill="url(#map-bg)"
        />
        
        <!-- 道路网格 -->
        <rect
          width="1200"
          height="800"
          fill="url(#road-grid)"
          opacity="0.4"
        />
        
        <!-- 胶囊标记 -->
        <g v-if="mapMarkers.length > 0">
          <g
            v-for="(marker, idx) in mapMarkers"
            :key="idx"
          >
            <!-- 标记连接线 -->
            <line 
              v-if="userLocation && marker.distance"
              :x1="userLocation.x" 
              :y1="userLocation.y" 
              :x2="marker.x" 
              :y2="marker.y" 
              stroke="#94a3b8" 
              stroke-width="1" 
              stroke-dasharray="4 4"
              opacity="0.4"
            />
            
            <!-- 标记主体 -->
            <circle 
              :cx="marker.x" 
              :cy="marker.y" 
              :r="marker.isActive ? 14 : 10"
              :fill="getMarkerColor(marker.vis)"
              stroke="#fff"
              stroke-width="2"
              filter="url(#marker-shadow)"
              class="marker-circle"
              @click="handleMarkerClick(marker.id)"
            />
            
            <!-- 活跃标记光环 -->
            <circle 
              v-if="marker.isActive"
              :cx="marker.x" 
              :cy="marker.y" 
              r="18"
              :fill="getMarkerColor(marker.vis)"
              opacity="0.3"
              class="marker-halo"
            />
            
            <!-- 距离标签 -->
            <text 
              v-if="marker.distance && marker.isActive"
              :x="marker.x" 
              :y="marker.y - 25" 
              text-anchor="middle" 
              fill="#475569" 
              font-size="12" 
              font-weight="500"
              class="distance-label"
            >
              {{ marker.distance }}米
            </text>
            
            <title>{{ marker.title }}</title>
          </g>
        </g>
        <g v-else>
          <text
            x="600"
            y="400"
            text-anchor="middle"
            fill="#64748b"
            font-size="20"
            font-weight="500"
          >
            暂无胶囊数据
          </text>
        </g>

        <!-- 用户位置标记 -->
        <g v-if="userLocation">
          <!-- 位置脉冲效果 -->
          <circle 
            :cx="userLocation.x" 
            :cy="userLocation.y" 
            r="24"
            fill="rgba(16, 185, 129, 0.15)"
            class="user-pulse-1"
          />
          <circle 
            :cx="userLocation.x" 
            :cy="userLocation.y" 
            r="18"
            fill="rgba(16, 185, 129, 0.25)"
            class="user-pulse-2"
          />
          
          <!-- 用户位置主体 -->
          <circle 
            :cx="userLocation.x" 
            :cy="userLocation.y" 
            r="10"
            fill="#10b981"
            stroke="#fff"
            stroke-width="3"
            class="user-marker"
          />
          
          <!-- 位置指示器 -->
          <polygon 
            :points="getUserPointerPoints(userLocation.x, userLocation.y)"
            fill="#10b981"
            class="user-pointer"
          />
        </g>

        <!-- 比例尺 -->
        <g
          v-if="scaleInfo"
          class="map-scale"
        >
          <rect 
            :x="scaleInfo.x" 
            :y="scaleInfo.y" 
            :width="scaleInfo.width" 
            :height="scaleInfo.height" 
            rx="6" 
            fill="#fff" 
            fill-opacity="0.9"
            stroke="#cbd5e1"
            stroke-width="1"
          />
          <line 
            :x1="scaleInfo.x+15" 
            :y1="scaleInfo.y+scaleInfo.height-20" 
            :x2="scaleInfo.x+15+scaleInfo.scalePx" 
            :y2="scaleInfo.y+scaleInfo.height-20" 
            stroke="#3b82f6" 
            stroke-width="3" 
            stroke-linecap="round"
          />
          <text 
            :x="scaleInfo.x+15+scaleInfo.scalePx/2" 
            :y="scaleInfo.y+scaleInfo.height-25" 
            text-anchor="middle" 
            fill="#3b82f6" 
            font-size="12" 
            font-weight="600"
          >
            {{ scaleInfo.label }}
          </text>
        </g>

        <!-- 指南针 -->
        <g
          class="compass"
          transform="translate(50, 50)"
        >
          <circle
            cx="0"
            cy="0"
            r="25"
            fill="#fff"
            fill-opacity="0.9"
            stroke="#cbd5e1"
            stroke-width="1"
          />
          <path
            d="M0 -15 L-5 10 L0 5 L5 10 Z"
            fill="#ef4444"
          />
          <text
            x="0"
            y="25"
            text-anchor="middle"
            fill="#64748b"
            font-size="12"
            font-weight="600"
          >N</text>
        </g>
      </svg>
    </div>

    <!-- 地图控制栏 -->
    <div
      v-if="showControls"
      class="map-controls"
    >
      <button 
        class="control-btn" 
        :disabled="isLocating"
        :title="locationPermission === 'granted' ? '重新定位' : '请求位置权限'"
        @click="handleLocate"
      >
        <i
          class="fas"
          :class="locationPermission === 'granted' ? 'fa-location-arrow' : 'fa-location-crosshairs'"
        />
        {{ isLocating ? '定位中...' : '定位' }}
      </button>
      <button 
        class="control-btn" 
        :title="realTimeTracking ? '关闭实时追踪' : '开启实时追踪'"
        @click="toggleRealTimeTracking"
      >
        <i
          class="fas"
          :class="realTimeTracking ? 'fa-satellite-dish' : 'fa-satellite'"
        />
      </button>
      <button 
        class="control-btn" 
        title="放大"
        @click="zoomIn"
      >
        <i class="fas fa-plus" />
      </button>
      <button 
        class="control-btn" 
        title="缩小"
        @click="zoomOut"
      >
        <i class="fas fa-minus" />
      </button>
    </div>

    <!-- 实时追踪状态指示器 -->
    <div
      v-if="realTimeTracking && locationPermission === 'granted'"
      class="tracking-indicator"
    >
      <div class="tracking-pulse" />
      <span>实时追踪中</span>
      <small>最后更新: {{ lastLocationUpdate }}</small>
    </div>

    <!-- 胶囊信息面板 -->
    <div 
      v-if="activeMarker"
      class="marker-panel"
      :style="getPanelPosition(activeMarker)"
    >
      <div class="panel-header">
        <h4 class="panel-title">
          {{ activeMarker.title }}
        </h4>
        <button
          class="panel-close"
          @click="closeMarkerPanel"
        >
          ✕
        </button>
      </div>
      <div class="panel-body">
        <p class="panel-desc">
          {{ truncateText(activeMarker.desc, 50) }}
        </p>
        <div class="panel-meta">
          <span><i class="fas fa-clock" /> {{ formatTime(activeMarker.time) }}</span>
          <span><i class="fas fa-eye" /> {{ activeMarker.views }} 浏览</span>
          <span><i class="fas fa-lock" /> {{ getVisText(activeMarker.vis) }}</span>
        </div>
        <div
          v-if="activeMarker.distance"
          class="panel-distance"
        >
          <i class="fas fa-ruler" /> 距离: {{ activeMarker.distance }}米
        </div>
        <div class="panel-tags">
          <span 
            v-for="(tag, idx) in activeMarker.tags"
            :key="idx"
            class="tag-item"
          >
            {{ tag }}
          </span>
        </div>
      </div>
      <div class="panel-actions">
        <button
          class="btn small"
          @click="handleViewCapsule(activeMarker.id)"
        >
          查看详情
        </button>
        <button
          class="btn small ghost"
          @click="handleNavToCapsule(activeMarker.id)"
        >
          导航到此
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'

const props = defineProps({
  capsuleData: {
    type: Array,
    required: true,
    default: () => []
  },
  mapHeight: {
    type: String,
    default: '600px'
  },
  showControls: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['view-capsule', 'nav-capsule', 'map-ready'])

// 地图DOM引用
const mapRef = ref(null)

// 状态管理
const isMapLoaded = ref(false)
const isLoading = ref(false)
const isLocating = ref(false)
const mapMarkers = ref([])
const userLocation = ref(null)
const svgViewBox = ref('0 0 1200 800')
const scaleInfo = ref(null)
const activeMarker = ref(null)
const locationPermission = ref('prompt') // 'granted', 'denied', 'prompt'
const realTimeTracking = ref(false)
const lastLocationUpdate = ref(null)
const watchId = ref(null)
const showNotification = ref(false)
const notificationText = ref('')
const notificationIcon = ref('')

// 改进的位置获取函数
const getCurrentPosition = () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('浏览器不支持地理位置API'))
      return
    }

    navigator.geolocation.getCurrentPosition(
      resolve,
      reject,
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    )
  })
}

// 显示通知
const showStatusNotification = (text, icon = 'fa-info-circle') => {
  notificationText.value = text
  notificationIcon.value = icon
  showNotification.value = true
  
  // 5秒后自动隐藏
  setTimeout(() => {
    showNotification.value = false
  }, 5000)
}

// 隐藏通知
const hideNotification = () => {
  showNotification.value = false
}

// 初始化地图
const initMap = async() => {
  isLoading.value = true
  try {
    // 检查位置权限状态
    await checkPermissionStatus()
    
    // 尝试获取当前位置
    if (locationPermission.value === 'granted') {
      await locateAndRender()
      showStatusNotification('位置权限已授权', 'fa-check-circle')
    } else {
      // 使用默认位置
      userLocation.value = { lat: 39.9042, lng: 116.4074, x: 600, y: 400 } // 北京中心
      renderMapMarkers()
      showStatusNotification('使用默认位置', 'fa-map-marker-alt')
    }
    
    isMapLoaded.value = true
    emit('map-ready', null)
  } catch (error) {
    console.error('地图初始化失败:', error)
    // 使用默认位置
    userLocation.value = { lat: 39.9042, lng: 116.4074, x: 600, y: 400 }
    renderMapMarkers()
    showStatusNotification('地图加载完成', 'fa-map')
  } finally {
    isLoading.value = false
  }
}

// 检查位置权限状态
const checkPermissionStatus = async() => {
  if (!navigator.permissions) {
    locationPermission.value = 'prompt'
    return
  }

  try {
    const result = await navigator.permissions.query({ name: 'geolocation' })
    locationPermission.value = result.state
    
    result.onchange = () => {
      locationPermission.value = result.state
      if (result.state === 'granted' && !realTimeTracking.value) {
        startRealTimeTracking()
        showStatusNotification('位置权限已授权', 'fa-check-circle')
      } else if (result.state === 'denied') {
        stopRealTimeTracking()
        showStatusNotification('位置权限被拒绝', 'fa-exclamation-circle')
      }
    }
  } catch (error) {
    console.warn('权限检查失败:', error)
    locationPermission.value = 'prompt'
  }
}

// 定位并渲染地图
const locateAndRender = async() => {
  isLocating.value = true
  try {
    const position = await getCurrentPosition()
    const lat = position.coords.latitude
    const lng = position.coords.longitude
    
    userLocation.value = {
      lat,
      lng,
      x: 600,
      y: 400
    }
    
    renderMapMarkers()
    updateLastLocationTime()
    
    // 如果权限已授予但未开启实时追踪，自动开启
    if (locationPermission.value === 'granted' && !realTimeTracking.value) {
      realTimeTracking.value = true
      startRealTimeTracking()
    }
    
    showStatusNotification('定位成功', 'fa-check-circle')
  } catch (error) {
    console.error('定位失败:', error)
    // 使用默认位置
    userLocation.value = { lat: 39.9042, lng: 116.4074, x: 600, y: 400 }
    renderMapMarkers()
    
    if (error.code === 1) {
      locationPermission.value = 'denied'
      showStatusNotification('位置权限被拒绝', 'fa-exclamation-circle')
    } else {
      showStatusNotification('定位失败，使用默认位置', 'fa-map-marker-alt')
    }
  } finally {
    isLocating.value = false
  }
}

// 开始实时位置追踪
const startRealTimeTracking = () => {
  if (!navigator.geolocation || locationPermission.value !== 'granted') {
    return
  }

  stopRealTimeTracking() // 先停止之前的监听

  watchId.value = navigator.geolocation.watchPosition(
    (position) => {
      const lat = position.coords.latitude
      const lng = position.coords.longitude
      
      userLocation.value = {
        lat,
        lng,
        x: 600,
        y: 400
      }
      
      renderMapMarkers()
      updateLastLocationTime()
    },
    (error) => {
      console.error('实时位置更新失败:', error)
      if (error.code === 1) {
        locationPermission.value = 'denied'
        stopRealTimeTracking()
        showStatusNotification('位置权限被拒绝', 'fa-exclamation-circle')
      }
    },
    {
      enableHighAccuracy: true,
      timeout: 5000,
      maximumAge: 1000 // 1秒更新一次
    }
  )

  realTimeTracking.value = true
  showStatusNotification('实时追踪已开启', 'fa-satellite-dish')
}

// 停止实时位置追踪
const stopRealTimeTracking = () => {
  if (watchId.value !== null) {
    navigator.geolocation.clearWatch(watchId.value)
    watchId.value = null
  }
  realTimeTracking.value = false
  showStatusNotification('实时追踪已关闭', 'fa-satellite')
}

// 切换实时追踪
const toggleRealTimeTracking = () => {
  if (realTimeTracking.value) {
    stopRealTimeTracking()
  } else {
    if (locationPermission.value === 'granted') {
      startRealTimeTracking()
    } else {
      handleLocate() // 先请求位置权限
    }
  }
}

// 更新最后位置更新时间
const updateLastLocationTime = () => {
  const now = new Date()
  lastLocationUpdate.value = now.toLocaleTimeString('zh-CN')
}

// 渲染地图标记
const renderMapMarkers = () => {
  if (!userLocation.value) return

  const userLat = userLocation.value.lat
  const userLng = userLocation.value.lng
  
  // 计算所有胶囊到用户的最大距离
  let maxD = 1000
  const dists = props.capsuleData.map(c => getDistance(userLat, userLng, c.lat, c.lng))
  if (dists.length > 0) {
    maxD = Math.max(...dists, 100)
  }

  // 画布参数
  const centerX = 600, centerY = 400, maxRadius = 280
  
  // 计算比例尺
  const pxPerMeter = maxRadius / maxD
  let scaleLen = 100
  if (maxD > 500) scaleLen = 500
  else if (maxD > 200) scaleLen = 200
  
  const scalePx = Math.round(scaleLen * pxPerMeter)
  scaleInfo.value = {
    x: 950, y: 720, width: 200, height: 40,
    scalePx,
    label: `${scaleLen}米`
  }

  // 标记渲染
  const markers = props.capsuleData.map(capsule => {
    const d = getDistance(userLat, userLng, capsule.lat, capsule.lng)
    const angle = getBearing(userLat, userLng, capsule.lat, capsule.lng)
    const r = Math.min(d, maxD) / maxD * maxRadius
    const rad = (angle - 90) * Math.PI / 180
    const x = centerX + r * Math.cos(rad)
    const y = centerY + r * Math.sin(rad)
    
    return {
      id: capsule.id,
      title: capsule.title,
      desc: capsule.desc,
      time: capsule.time,
      vis: capsule.vis,
      views: capsule.views,
      tags: capsule.tags,
      x,
      y,
      isActive: false,
      distance: Math.round(d),
      angle: Math.round(angle)
    }
  })
  
  mapMarkers.value = markers
}

// 计算两点间距离（米）
const getDistance = (lat1, lng1, lat2, lng2) => {
  const R = 6371000
  const toRad = deg => deg * Math.PI / 180
  const dLat = toRad(lat2 - lat1)
  const dLng = toRad(lng2 - lng1)
  const a = Math.sin(dLat/2)**2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng/2)**2
  return 2 * R * Math.asin(Math.sqrt(a))
}

// 计算方位角
const getBearing = (lat1, lng1, lat2, lng2) => {
  const toRad = deg => deg * Math.PI / 180
  const toDeg = rad => rad * 180 / Math.PI
  const dLng = toRad(lng2 - lng1)
  const y = Math.sin(dLng) * Math.cos(toRad(lat2))
  const x = Math.cos(toRad(lat1)) * Math.sin(toRad(lat2)) - Math.sin(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.cos(dLng)
  let brng = Math.atan2(y, x)
  brng = toDeg(brng)
  return (brng + 360) % 360
}

// 获取用户位置指示器三角形点
const getUserPointerPoints = (x, y) => {
  return `${x},${y-12} ${x-6},${y+8} ${x+6},${y+8}`
}

// 获取面板位置（避免超出边界）
const getPanelPosition = (marker) => {
  const panelWidth = 280
  const panelHeight = 180
  let left = marker.x + 20
  let top = marker.y
  
  // 检查右边界
  if (left + panelWidth > 1200) {
    left = marker.x - panelWidth - 20
  }
  
  // 检查下边界
  if (top + panelHeight > 800) {
    top = marker.y - panelHeight
  }
  
  return { left: `${left}px`, top: `${top}px` }
}

// 标记点击处理
const handleMarkerClick = (markerId) => {
  const marker = mapMarkers.value.find(m => m.id === markerId)
  if (!marker) return
  
  mapMarkers.value = mapMarkers.value.map(m => ({
    ...m,
    isActive: m.id === markerId
  }))
  activeMarker.value = marker
}

// 关闭标记面板
const closeMarkerPanel = () => {
  activeMarker.value = null
  mapMarkers.value = mapMarkers.value.map(m => ({ ...m, isActive: false }))
}

// 用户定位
const handleLocate = async() => {
  if (locationPermission.value === 'denied') {
    showStatusNotification('位置权限已被拒绝，请在浏览器设置中启用位置权限', 'fa-exclamation-triangle')
    return
  }
  
  await locateAndRender()
}

// 地图缩放
const zoomIn = () => {
  const svg = mapRef.value?.querySelector('.map-svg')
  if (svg) {
    const currentScale = parseFloat(svg.style.transform.replace('scale(', '')) || 1
    if (currentScale < 2) {
      svg.style.transform = `scale(${currentScale + 0.2})`
      svg.style.transformOrigin = 'center'
    }
  }
}

const zoomOut = () => {
  const svg = mapRef.value?.querySelector('.map-svg')
  if (svg) {
    const currentScale = parseFloat(svg.style.transform.replace('scale(', '')) || 1
    if (currentScale > 0.5) {
      svg.style.transform = `scale(${currentScale - 0.2})`
      svg.style.transformOrigin = 'center'
    }
  }
}

// 辅助函数
const getMarkerColor = (vis) => {
  switch (vis) {
  case 'public': return '#4ade80'
  case 'friend': return '#60a5fa'
  case 'private': return '#f97316'
  default: return '#94a3b8'
  }
}

const getVisText = (vis) => {
  switch (vis) {
  case 'public': return '校园公开'
  case 'friend': return '好友可见'
  case 'private': return '仅自己可见'
  default: return '未知'
  }
}

const truncateText = (text, maxLen) => {
  if (!text) return ''
  if (text.length <= maxLen) return text
  return text.slice(0, maxLen) + '...'
}

const formatTime = (timeStr) => {
  if (!timeStr) return '未知时间'
  try {
    const date = new Date(timeStr)
    return date.toLocaleDateString('zh-CN')
  } catch {
    return timeStr
  }
}

const handleViewCapsule = (capsuleId) => {
  emit('view-capsule', capsuleId)
  closeMarkerPanel()
}

const handleNavToCapsule = (capsuleId) => {
  emit('nav-capsule', capsuleId)
  const marker = mapMarkers.value.find(m => m.id === capsuleId)
  if (marker) {
    const svg = mapRef.value?.querySelector('.map-svg')
    if (svg) {
      svg.style.transform = `translate(${(600 - marker.x)}px, ${(400 - marker.y)}px)`
    }
  }
}

// 监听胶囊数据变化
watch(() => props.capsuleData, (newVal) => {
  if (isMapLoaded.value) {
    renderMapMarkers()
  }
}, { deep: true })

// 组件挂载和卸载
onMounted(() => {
  initMap()
})

onUnmounted(() => {
  stopRealTimeTracking()
})
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
}

.map-dom {
  width: 100%;
  height: 100%;
  background: #f8fafc;
  display: flex;
  align-items: stretch;
  justify-content: stretch;
}

.map-svg {
  width: 100%;
  height: 100%;
  display: block;
  transition: all 0.3s ease;
}

/* 通知栏 */
.notification-bar {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.95);
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow);
  z-index: 10;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(203, 213, 225, 0.3);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  max-width: 300px;
  animation: slideIn 0.3s ease-out;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #475569;
  font-size: 14px;
  font-weight: 500;
}

.notification-close {
  background: transparent;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #94a3b8;
  padding: 2px;
  border-radius: 4px;
  transition: all 0.2s;
}

.notification-close:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #475569;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 标记样式 */
.marker-circle {
  cursor: pointer;
  transition: all 0.3s ease;
}

.marker-circle:hover {
  r: 12;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
}

.marker-halo {
  animation: haloPulse 2s ease-in-out infinite;
}

@keyframes haloPulse {
  0%, 100% { r: 18; opacity: 0.3; }
  50% { r: 22; opacity: 0.1; }
}

.distance-label {
  font-size: 12px;
  font-weight: 500;
  fill: #475569;
}

/* 用户位置标记 */
.user-marker {
  z-index: 5;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.user-pulse-1 {
  animation: userPulse1 3s ease-in-out infinite;
}

.user-pulse-2 {
  animation: userPulse2 3s ease-in-out infinite;
}

.user-pointer {
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
}

@keyframes userPulse1 {
  0%, 100% { r: 24; opacity: 0.15; }
  50% { r: 28; opacity: 0.1; }
}

@keyframes userPulse2 {
  0%, 100% { r: 18; opacity: 0.25; }
  50% { r: 22; opacity: 0.15; }
}

/* 地图控制栏 */
.map-controls {
  position: absolute;
  bottom: 20px;
  left: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 10;
}

.control-btn {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: white;
  border: none;
  box-shadow: var(--shadow-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #374151;
  font-size: 16px;
}

.control-btn:hover {
  background: var(--accent-light);
  color: var(--accent);
  transform: translateY(-2px);
  box-shadow: var(--shadow-xl);
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 实时追踪指示器 */
.tracking-indicator {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(255, 255, 255, 0.95);
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow);
  z-index: 10;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(34, 197, 94, 0.2);
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #16a34a;
  font-weight: 500;
}

.tracking-pulse {
  width: 12px;
  height: 12px;
  background: #22c55e;
  border-radius: 50%;
  animation: trackingPulse 1.5s ease-in-out infinite;
}

@keyframes trackingPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.2); }
}

.tracking-indicator small {
  color: #64748b;
  font-weight: normal;
  margin-left: 8px;
}

/* 标记信息面板 */
.marker-panel {
  position: absolute;
  width: 300px;
  background: white;
  border-radius: var(--radius);
  box-shadow: var(--shadow-xl);
  padding: 16px;
  z-index: 20;
  border: 1px solid rgba(203, 213, 225, 0.3);
  backdrop-filter: blur(8px);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
  line-height: 1.4;
}

.panel-close {
  background: transparent;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--muted);
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.panel-close:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #1e293b;
}

.panel-body {
  margin-bottom: 16px;
}

.panel-desc {
  color: var(--muted);
  font-size: 14px;
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.panel-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 8px;
}

.panel-distance {
  font-size: 13px;
  color: #3b82f6;
  font-weight: 500;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.panel-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-item {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 12px;
  background: var(--accent-light);
  color: var(--accent);
  font-weight: 500;
}

.panel-actions {
  display: flex;
  gap: 10px;
}

.btn {
  background: var(--accent);
  color: white;
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  font-size: 13px;
  flex: 1;
}

.btn:hover {
  background: var(--accent-hover);
  box-shadow: var(--shadow);
  transform: translateY(-1px);
}

.btn.ghost {
  background: transparent;
  color: var(--accent);
  border: 1px solid rgba(108, 140, 255, 0.3);
}

.btn.ghost:hover {
  background: var(--accent-light);
  border-color: var(--accent);
}

.btn.small {
  padding: 6px 12px;
  font-size: 12px;
}

/* 设计令牌 */
:root {
  --bg: #f5f8ff;
  --card: #ffffff;
  --muted: #64748b;
  --accent: #3b82f6;
  --accent-hover: #2563eb;
  --accent-light: rgba(59, 130, 246, 0.1);
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  --radius: 12px;
  --radius-sm: 8px;
}
</style>