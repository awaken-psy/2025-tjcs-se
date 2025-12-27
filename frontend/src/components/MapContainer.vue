<template>
  <div class="map-container">
    <!-- 高德地图容器 -->
    <div ref="mapRef" class="amap-container" :style="{ height: mapHeight }">
      <!-- 通知栏 -->
      <div v-if="showNotification" class="notification-bar">
        <div class="notification-content">
          <i class="fas" :class="notificationIcon" />
          <span>{{ notificationText }}</span>
        </div>
        <button class="notification-close" @click="hideNotification">✕</button>
      </div>
    </div>

    <!-- 地图控制栏 -->
    <div v-if="showControls" class="map-controls">
      <button
        class="control-btn"
        :disabled="isLocating"
        :title="locationPermission === 'granted' ? '重新定位' : '请求位置权限'"
        @click="handleLocate">
        <i
          class="fas"
          :class="
            locationPermission === 'granted'
              ? 'fa-location-arrow'
              : 'fa-location-crosshairs'
          " />
        {{ isLocating ? '定位中...' : '定位' }}
      </button>
    </div>

    <!-- 实时追踪状态指示器 -->
    <div
      v-if="realTimeTracking && locationPermission === 'granted'"
      class="tracking-indicator">
      <div class="tracking-pulse" />
      <span>实时追踪中</span>
      <small>最后更新: {{ lastLocationUpdate }}</small>
    </div>

    <!-- 用户位置信息面板 -->
    <div
      v-if="userLocation && userLocation.lat !== 39.90923"
      class="location-panel">
      <div class="location-header">
        <i class="fas fa-map-marker-alt location-icon" />
        <h4 class="location-title">我的位置</h4>
        <button class="location-close" @click="clearUserLocation">✕</button>
      </div>
      <div class="location-body">
        <div class="location-coords">
          <span>经度: {{ userLocation.lng.toFixed(6) }}</span>
          <span>纬度: {{ userLocation.lat.toFixed(6) }}</span>
        </div>
        <div v-if="userLocation.accuracy" class="location-accuracy">
          <i class="fas fa-bullseye" /> 精度: ±{{
            Math.round(userLocation.accuracy)
          }}米
        </div>
      </div>
    </div>

    <!-- 胶囊信息面板 -->
    <div v-if="activeMarker" class="marker-panel">
      <div class="panel-header">
        <h4 class="panel-title">
          {{ activeMarker.title }}
        </h4>
        <button class="panel-close" @click="closeMarkerPanel">✕</button>
      </div>
      <div class="panel-body">
        <p class="panel-desc">
          {{ truncateText(activeMarker.desc, 50) }}
        </p>
        <div class="panel-meta">
          <span
            ><i class="fas fa-clock" />
            {{ formatTime(activeMarker.time) }}</span
          >
          <span><i class="fas fa-eye" /> {{ activeMarker.views }} 浏览</span>
          <span
            ><i class="fas fa-lock" /> {{ getVisText(activeMarker.vis) }}</span
          >
        </div>
        <div v-if="activeMarker.distance" class="panel-distance">
          <i class="fas fa-ruler" /> 距离: {{ activeMarker.distance }}米
        </div>
        <div class="panel-tags">
          <span
            v-for="(tag, idx) in activeMarker.tags"
            :key="idx"
            class="tag-item">
            {{ tag }}
          </span>
        </div>
      </div>
      <div class="panel-actions">
        <button class="btn small" @click="handleViewCapsule(activeMarker.id)">
          查看详情
        </button>
        <button
          class="btn small ghost"
          @click="handleUnlockCapsule(activeMarker.id)"
          :disabled="activeMarker.is_unlocked"
          :style="
            activeMarker.is_unlocked ? 'opacity: 0.6; cursor: not-allowed;' : ''
          ">
          <i
            class="fas"
            :class="activeMarker.is_unlocked ? 'fa-lock-open' : 'fa-lock'"></i>
          {{ activeMarker.is_unlocked ? '已解锁' : '解锁' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { getCurrentLocation } from '@/utils/locationService'

const props = defineProps({
  capsuleData: {
    type: Array,
    required: true,
    default: () => [],
  },
  mapHeight: {
    type: String,
    default: '1200px',
  },
  showControls: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits([
  'view-capsule',
  'unlock-capsule',
  'map-ready',
  'location-updated',
])

// 地图引用
const mapRef = ref(null)
let map = null

// 状态管理
const isMapLoaded = ref(false)
const isLoading = ref(false)
const isLocating = ref(false)
const userLocation = ref(null)
const activeMarker = ref(null)
const locationPermission = ref('prompt')
const realTimeTracking = ref(false)
const lastLocationUpdate = ref(null)
const locationTimer = ref(null)
const showNotification = ref(false)
const notificationText = ref('')
const notificationIcon = ref('')

// 标记管理
const markers = ref([])
let userLocationMarker = null
let locationPulseLayer = null

// 显示通知
const showStatusNotification = (text, icon = 'fa-info-circle') => {
  notificationText.value = text
  notificationIcon.value = icon
  showNotification.value = true

  setTimeout(() => {
    showNotification.value = false
  }, 5000)
}

const hideNotification = () => {
  showNotification.value = false
}

// 初始化地图
const initMap = () => {
  // 等待高德地图API加载完成
  if (typeof AMap === 'undefined') {
    console.error('高德地图API未加载')
    showStatusNotification('地图加载失败，请刷新页面', 'fa-exclamation-circle')
    return
  }

  isLoading.value = true

  try {
    // 1. 创建地图实例
    map = new AMap.Map(mapRef.value, {
      zoom: 15,
      center: [120.529881, 31.026362],
      mapStyle: 'amap://styles/blue',
    })

    // 【核心修复】：强制地图重绘
    // 延迟执行确保地图容器 DOM 元素已经获得了最终的像素高度
    setTimeout(() => {
      if (map) {
        map.setFitView()
      }
    }, 100) // 给予 100ms 足够的时间让浏览器计算布局

    // 添加地图控件
    if (AMap.Scale) {
      map.addControl(new AMap.Scale())
    }
    if (AMap.ToolBar) {
      map.addControl(new AMap.ToolBar())
    }

    // 检查位置权限并尝试定位
    checkPermissionStatus()

    // 初始定位
    locateUser()

    isMapLoaded.value = true
    emit('map-ready', map)
    showStatusNotification('地图加载成功', 'fa-check-circle')
  } catch (error) {
    console.error('地图初始化失败:', error)
    showStatusNotification('地图初始化失败', 'fa-exclamation-circle')
  } finally {
    isLoading.value = false
  }
}

// 检查位置权限状态
const checkPermissionStatus = async () => {
  if (!navigator.permissions) {
    locationPermission.value = 'prompt'
    return
  }

  try {
    const result = await navigator.permissions.query({ name: 'geolocation' })
    locationPermission.value = result.state

    result.onchange = () => {
      locationPermission.value = result.state
      if (result.state === 'granted') {
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

// 定位用户
const handleLocate = () => {
  if (locationPermission.value === 'denied') {
    showStatusNotification(
      '位置权限已被拒绝，请在浏览器设置中启用位置权限',
      'fa-exclamation-triangle'
    )
    return
  }

  locateUser()
}

// 执行定位 - 使用新的定位服务
// 执行定位 - 直接使用高德地图定位
// MapContainer.vue - locateUser 函数
const locateUser = async () => {
  isLocating.value = true

  try {
    const location = await getCurrentLocation()

    // 关键修改：不再严格依赖 location.success，而是检查是否有坐标，
    // 且精度在可接受范围内。
    // 假设：我们接受精度在 100 米以内的结果
    const ACCEPTABLE_ACCURACY = 400 // 设定一个可接受的精度阈值

    if (
      location.longitude &&
      location.latitude &&
      location.accuracy <= ACCEPTABLE_ACCURACY
    ) {
      // 成功获取到坐标且精度合格 (即使 location.success 可能为 false)
      userLocation.value = {
        lng: location.longitude,
        lat: location.latitude,
        accuracy: location.accuracy,
        source: location.source,
      }

      // 【修改点】：发送给父组件时，构造标准格式对象
      const locationPayload = {
        longitude: location.longitude, // 全拼
        latitude: location.latitude, // 全拼
        lng: location.longitude, // 兼容保留
        lat: location.latitude, // 兼容保留
      }

      emit('location-updated', locationPayload) // 发送标准对象

      updateUserLocationMarker()
      renderCapsuleMarkers()
      updateLastLocationTime()

      // 显示通知：如果是失败后抢救的定位，可能需要不同的通知
      if (!location.success) {
        showStatusNotification(
          `定位成功，精度 ${location.accuracy} 米`,
          'fa-crosshairs'
        )
      } else {
        showStatusNotification('定位成功！', 'fa-crosshairs')
      }

      if (locationPermission.value === 'granted' && !realTimeTracking.value) {
        realTimeTracking.value = true
        startRealTimeTracking()
      }
    } else {
      // 定位失败 (无坐标、或精度过差、或 getCurrentLocation 彻底失败)
      // 如果定位失败，且提供了错误信息，则抛出它
      if (location.error) {
        throw new Error(location.error)
      } else if (location.accuracy > ACCEPTABLE_ACCURACY) {
        // 如果有坐标但精度不满足要求，明确抛出精度不足的错误
        throw new Error(
          `定位精度不足（${location.accuracy}米），已设置阈值为 ${ACCEPTABLE_ACCURACY} 米。`
        )
      } else {
        // 彻底的未知失败
        throw new Error('定位失败')
      }
    }
  } catch (error) {
    console.error('定位失败:', error)

    // 定位失败后，使用默认位置并继续渲染地图和胶囊
    userLocation.value = { lng: 116.397428, lat: 39.90923, source: '默认位置' }

    // 【步骤一完成】：定位失败，但仍需将默认位置信息发射给 MapView.vue
    // 这样 MapView.vue 才能触发 fetchCapsules()
    emit('location-updated', userLocation.value)

    updateUserLocationMarker()
    renderCapsuleMarkers()

    showStatusNotification('定位失败，使用默认位置', 'fa-map-marker-alt')
  } finally {
    isLocating.value = false
  }
}

// 清除用户位置
const clearUserLocation = () => {
  userLocation.value = null
  removeUserLocationMarker()
}

// 移除用户位置标记
const removeUserLocationMarker = () => {
  if (userLocationMarker) {
    map.remove(userLocationMarker)
    userLocationMarker = null
  }
  if (locationPulseLayer) {
    map.remove(locationPulseLayer)
    locationPulseLayer = null
  }
}

// 更新用户位置标记 - 显著显示
const updateUserLocationMarker = () => {
  // 清除现有用户位置标记
  removeUserLocationMarker()

  if (userLocation.value && map) {
    // 创建显著的脉冲圆环效果
    locationPulseLayer = new AMap.Circle({
      center: [userLocation.value.lng, userLocation.value.lat],
      radius: userLocation.value.accuracy || 50, // 使用定位精度作为半径
      strokeColor: '#1890ff',
      strokeWeight: 2,
      strokeOpacity: 0.6,
      fillColor: '#1890ff',
      fillOpacity: 0.2,
      zIndex: 50,
    })
    map.add(locationPulseLayer)

    // 创建显著的用户位置标记
    userLocationMarker = new AMap.Marker({
      position: [userLocation.value.lng, userLocation.value.lat],
      // 使用自定义图标 - 更显著的定位图标
      content: createUserLocationIcon(),
      offset: new AMap.Pixel(-20, -20),
      zIndex: 100,
    })

    userLocationMarker.isUserLocation = true
    map.add(userLocationMarker)

    // 创建精度圆（如果精度信息可用）
    if (userLocation.value.accuracy) {
      const accuracyCircle = new AMap.Circle({
        center: [userLocation.value.lng, userLocation.value.lat],
        radius: userLocation.value.accuracy,
        strokeColor: '#52c41a',
        strokeWeight: 1,
        strokeOpacity: 0.4,
        fillColor: '#52c41a',
        fillOpacity: 0.1,
        zIndex: 30,
      })
      map.add(accuracyCircle)
      markers.value.push(accuracyCircle)
    }

    // 定位到用户位置并适当缩放
    map.setCenter([userLocation.value.lng, userLocation.value.lat])
    map.setZoom(15) // 放大到更近的级别

    // 添加脉冲动画
    startPulseAnimation()
  }
}
// 创建美观且中心对齐的用户位置图标
const createUserLocationIcon = () => {
  // 优化点：箭头完全居中、添加渐变质感、增强视觉层次
  return `
    <div class="user-location-marker">
      <div class="location-pulse-1"></div>
      <div class="location-pulse-2"></div>
      <div class="location-center-arrow">
        <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <!-- 外层渐变圆环：增强立体感 -->
          <circle cx="12" cy="12" r="10" stroke="white" stroke-width="3" fill="none" />
          <!-- 内层渐变圆：从深蓝到浅蓝，更有质感 -->
          <defs>
            <radialGradient id="locationGradient" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
              <stop offset="0%" stop-color="#3b82f6" />
              <stop offset="100%" stop-color="#1890ff" />
            </radialGradient>
          </defs>
          <circle cx="12" cy="12" r="8" fill="url(#locationGradient)" />
          <!-- 完全居中的箭头：顶点、中心点、底边均对齐圆心（12,12） -->
          <polygon 
            points="12,8 15,14 13,14 13,17 11,17 11,14 9,14" 
            fill="#fff" 
            stroke="#2563eb" 
            stroke-width="1"
            stroke-linejoin="round"
          />
          <!-- 中心亮点：提升精致感 -->
          <circle cx="12" cy="12" r="1.5" fill="white" opacity="0.8" />
        </svg>
      </div>
    </div>
  `
}

// 开始脉冲动画
const startPulseAnimation = () => {
  // 动画通过CSS实现
}

// 渲染胶囊标记
const renderCapsuleMarkers = () => {
  if (!map) return

  // 清除现有胶囊标记
  markers.value
    .filter((m) => !m.isUserLocation)
    .forEach((marker) => {
      map.remove(marker)
    })

  // 只使用传入的胶囊数据，不使用默认数据
  const capsules = props.capsuleData

  capsules.forEach((capsule) => {
    const marker = createCapsuleMarker(capsule)
    if (marker) {
      map.add(marker)
      markers.value.push(marker)
    }
  })
}

// 创建胶囊标记
const createCapsuleMarker = (capsule) => {
  if (typeof AMap === 'undefined') return null

  // 根据可见性设置不同的图标
  let iconUrl = 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png' // 默认蓝色

  // 检查可见性字段，支持多种可能的字段名
  const visibility = capsule.visibility || capsule.vis || 'public'

  if (visibility === 'friends' || visibility === 'friend') {
    iconUrl = 'https://webapi.amap.com/theme/v1.3/markers/n/mark_g.png' // 绿色 - 好友可见
  } else if (visibility === 'private') {
    iconUrl = 'https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png' // 红色 - 私有
  } else {
    // public/campus 保持默认蓝色
    iconUrl = 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png' // 蓝色 - 公开
  }

  // 过滤掉无效坐标的胶囊不在地图显示
  if (
    capsule.lng < 73 ||
    capsule.lng > 135 ||
    capsule.lat < 18 ||
    capsule.lat > 54
  ) {
    console.warn(
      `跳过无效坐标的胶囊: [${capsule.lng}, ${capsule.lat}] (超出中国范围)`
    )
    return null
  }

  // 创建自定义图标，调整图标大小
  const icon = new AMap.Icon({
    size: new AMap.Size(20, 20), // 减小图标大小
    image: iconUrl,
    imageSize: new AMap.Size(16, 16), // 减小图片大小
    imageOffset: new AMap.Pixel(-2, -2), // 图片偏移，使图标居中
  })

  const marker = new AMap.Marker({
    position: [capsule.lng, capsule.lat],
    icon: icon,
    offset: new AMap.Pixel(-10, -10), // 调整偏移以匹配新的图标大小
    extData: capsule, // 将胶囊数据存储在标记中
    zIndex: 100, // 设置层级，确保标记在上层
    cursor: 'pointer', // 鼠标样式
    // 移除动画参数，避免 API 兼容性问题
  })

  // 添加鼠标悬停效果（适度放大）
  marker.on('mouseover', () => {
    marker.setIcon(
      new AMap.Icon({
        size: new AMap.Size(24, 24), // 适度放大图标
        image: iconUrl,
        imageSize: new AMap.Size(20, 20),
        imageOffset: new AMap.Pixel(-2, -2),
      })
    )
  })

  marker.on('mouseout', () => {
    marker.setIcon(icon) // 恢复原始图标
  })

  // 创建信息窗内容
  const infoWindowContent = `
    <div style="padding: 10px; min-width: 200px;">
      <h3 style="margin: 0 0 8px 0; font-size: 14px; font-weight: bold; color: #333;">${
        capsule.title || '未命名胶囊'
      }</h3>
      <p style="margin: 4px 0; font-size: 12px; color: #666;">${
        capsule.content_preview || '暂无描述'
      }</p>
      <div style="margin-top: 8px; font-size: 11px; color: #999;">
        <span>🔒 ${getVisibilityText(capsule.visibility || 'public')}</span>
        <span style="margin-left: 8px;">👍 ${capsule.like_count || 0}</span>
        <span style="margin-left: 8px;">💬 ${capsule.comment_count || 0}</span>
      </div>
      <div style="margin-top: 8px;">
        <button id="view-detail-${
          capsule.id
        }" style="background: #6c8cff; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">查看详情</button>
      </div>
    </div>
  `

  // 创建信息窗
  const infoWindow = new AMap.InfoWindow({
    content: infoWindowContent,
    offset: new AMap.Pixel(0, -35),
  })

  // 添加点击事件
  marker.on('click', (e) => {
    // 打开信息窗
    infoWindow.open(map, marker.getPosition())

    // 为查看详情按钮绑定事件
    setTimeout(() => {
      const detailBtn = document.getElementById(`view-detail-${capsule.id}`)
      if (detailBtn) {
        detailBtn.onclick = () => {
          infoWindow.close()
          handleMarkerClick(capsule)
        }
      }
    }, 100)
  })

  // 辅助函数：获取可见性文字
  function getVisibilityText(visibility) {
    switch (visibility) {
      case 'private':
        return '仅自己可见'
      case 'friends':
        return '好友可见'
      case 'campus':
      case 'public':
        return '校园公开'
      default:
        return '公开'
    }
  }

  return marker
}

// 开始实时位置追踪
const startRealTimeTracking = () => {
  stopRealTimeTracking() // 先停止之前的定时器

  // 每10秒更新一次位置
  locationTimer.value = setInterval(async () => {
    if (locationPermission.value === 'granted') {
      try {
        const location = await getCurrentLocation()
        if (location.success) {
          userLocation.value = {
            lng: location.longitude,
            lat: location.latitude,
          }
          updateUserLocationMarker()
          updateLastLocationTime()

          // 【修改点】：同样构造标准格式
          const locationPayload = {
            longitude: location.longitude,
            latitude: location.latitude,
            lng: location.longitude,
            lat: location.latitude,
          }
          emit('location-updated', locationPayload)
        }
      } catch (error) {
        console.error('实时位置更新失败:', error)
      }
    }
  }, 10000) // 10秒

  realTimeTracking.value = true
  showStatusNotification('实时追踪已开启', 'fa-satellite-dish')
}

// 停止实时位置追踪
const stopRealTimeTracking = () => {
  if (locationTimer.value) {
    clearInterval(locationTimer.value)
    locationTimer.value = null
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

// 地图缩放
const zoomIn = () => {
  if (map) {
    map.zoomIn()
  }
}

const zoomOut = () => {
  if (map) {
    map.zoomOut()
  }
}

// 标记点击处理
const handleMarkerClick = (capsule) => {
  activeMarker.value = capsule

  // 计算距离（如果用户位置存在）
  if (userLocation.value) {
    const distance = calculateDistance(
      userLocation.value.lng,
      userLocation.value.lat,
      capsule.lng,
      capsule.lat
    )
    activeMarker.value.distance = Math.round(distance)
  }
}

// 计算两点间距离（米）
const calculateDistance = (lng1, lat1, lng2, lat2) => {
  const R = 6371000
  const toRad = (deg) => (deg * Math.PI) / 180
  const dLat = toRad(lat2 - lat1)
  const dLng = toRad(lng2 - lng1)
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2
  return 2 * R * Math.asin(Math.sqrt(a))
}

// 关闭标记面板
const closeMarkerPanel = () => {
  activeMarker.value = null
}

// 辅助函数
const getVisText = (vis) => {
  switch (vis) {
    case 'public':
      return '校园公开'
    case 'friend':
      return '好友可见'
    case 'private':
      return '仅自己可见'
    default:
      return '未知'
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

const handleUnlockCapsule = (capsuleId) => {
  // 触发解锁事件，传给父组件处理
  emit('unlock-capsule', capsuleId)

  // 可选：点击解锁后是否关闭小窗？
  // 如果父组件会弹出解锁弹窗，建议这里保持小窗或关闭均可。
  //closeMarkerPanel()
}

// 监听胶囊数据变化
watch(
  () => props.capsuleData,
  (newVal) => {
    //console.log('MapContainer Watch: 接收到新胶囊数据，长度:', newVal.length)
    if (isMapLoaded.value) {
      renderCapsuleMarkers()
    }
  },
  { deep: true }
)

// 组件挂载和卸载
onMounted(() => {
  // 假设 AMap 库已加载
  if (window.AMap) {
    initMap()
  } else {
    // 如果 AMap 是异步加载的，这里需要添加一个延迟或监听机制
    console.warn('等待 AMap 库加载...')
    // 实际项目中应监听 AMap Ready 事件，此处简化为 setTimeout
    setTimeout(() => {
      if (window.AMap) initMap()
    }, 500)
  }
})

onUnmounted(() => {
  stopRealTimeTracking()
  if (map) {
    map.destroy()
  }
})
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: 100%; /* 【关键修复】：确保根容器继承父组件的 100% 高度 */
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
}

.amap-container {
  width: 100%;
  height: 100%;
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

/* 地图控制栏 */
.map-controls {
  position: absolute;
  bottom: 20px;
  right: 20px;
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
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.2);
  }
}

.tracking-indicator small {
  color: #64748b;
  font-weight: normal;
  margin-left: 8px;
}

/* 用户位置信息面板 */
.location-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  width: 280px;
  background: white;
  border-radius: var(--radius);
  box-shadow: var(--shadow-xl);
  padding: 16px;
  z-index: 20;
  border: 1px solid rgba(24, 144, 255, 0.3);
  backdrop-filter: blur(8px);
  animation: slideInLeft 0.3s ease-out;
}

.location-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.location-icon {
  color: #1890ff;
  font-size: 16px;
}

.location-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #1890ff;
  flex: 1;
}

.location-close {
  background: transparent;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: var(--muted);
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.location-close:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #1e293b;
}

.location-body {
  font-size: 13px;
}

.location-coords {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;
  color: #475569;
}

.location-accuracy {
  color: #52c41a;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

@keyframes slideInLeft {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 标记信息面板 */
.marker-panel {
  position: absolute;
  top: 20px;
  right: 20px;
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
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
    0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
  --radius: 12px;
  --radius-sm: 8px;
}

/* 用户位置标记样式 */
.user-location-marker {
  position: relative;
  width: 40px;
  height: 40px;
}

.location-center-arrow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.location-pulse-1,
.location-pulse-2 {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border: 2px solid #1890ff;
  border-radius: 50%;
  animation: locationPulse 2s ease-out infinite;
}

.location-pulse-1 {
  width: 40px;
  height: 40px;
  animation-delay: 0s;
}

.location-pulse-2 {
  width: 60px;
  height: 60px;
  animation-delay: 1s;
}

@keyframes locationPulse {
  0% {
    transform: translate(-50%, -50%) scale(0.8);
    opacity: 0.8;
  }
  70% {
    transform: translate(-50%, -50%) scale(1.4);
    opacity: 0;
  }
  100% {
    transform: translate(-50%, -50%) scale(1.4);
    opacity: 0;
  }
}
/* 用户位置标记样式 - 确保中心对齐+美化 */
.user-location-marker {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center; /* 外层容器居中 */
}

.location-center-arrow {
  position: relative;
  z-index: 10;
  /* 确保SVG本身无偏移 */
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 优化脉冲动画与图标协调 */
.location-pulse-1,
.location-pulse-2 {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border: 2px solid #3b82f6;
  border-radius: 50%;
  animation: locationPulse 2s ease-out infinite;
  background: rgba(59, 130, 246, 0.1);
}

.location-pulse-1 {
  width: 40px;
  height: 40px;
  animation-delay: 0s;
}

.location-pulse-2 {
  width: 60px;
  height: 60px;
  animation-delay: 1s;
}

@keyframes locationPulse {
  0% {
    transform: translate(-50%, -50%) scale(0.8);
    opacity: 0.8;
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4);
  }
  70% {
    transform: translate(-50%, -50%) scale(1.6);
    opacity: 0;
    box-shadow: 0 0 0 15px rgba(59, 130, 246, 0);
  }
  100% {
    transform: translate(-50%, -50%) scale(1.6);
    opacity: 0;
  }
}
</style>
