<template>
  <div class="nearby-capsules-explorer">
    <!-- 控制面板 -->
    <div class="explorer-controls">
      <div class="location-section">
        <div class="location-status">
          <div class="location-info">
            <span class="location-icon" :class="locationStatusClass">📍</span>
            <span class="location-text">{{ locationText }}</span>
          </div>
          <button
            class="location-btn"
            @click="getCurrentLocationAndSearch"
            :disabled="isGettingLocation"
          >
            {{ isGettingLocation ? '定位中...' : '重新定位' }}
          </button>
        </div>

        <!-- 搜索范围控制 -->
        <div class="range-control">
          <label>搜索半径:</label>
          <select v-model="searchRadius" @change="searchNearbyCapsules">
            <option value="100">100米</option>
            <option value="500">500米</option>
            <option value="1000">1公里</option>
            <option value="2000">2公里</option>
            <option value="5000">5公里</option>
          </select>
        </div>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div class="search-results">
      <div class="results-header">
        <h3>
          附近胶囊
          <span class="results-count" v-if="capsules.length > 0">
            ({{ capsules.length }} 个)
          </span>
        </h3>
        <button
          class="refresh-btn"
          @click="searchNearbyCapsules"
          :disabled="isSearching || !currentLocation"
          title="刷新搜索结果"
        >
          🔄
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="isSearching" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在搜索附近的胶囊...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <div class="error-icon">⚠️</div>
        <p>{{ error }}</p>
        <button @click="retrySearch" class="retry-btn">重试</button>
      </div>

      <!-- 空状态 -->
      <div v-else-if="capsules.length === 0 && hasSearched" class="empty-state">
        <div class="empty-icon">🔍</div>
        <p>附近{{ searchRadius }}米范围内没有发现胶囊</p>
        <p class="empty-hint">尝试扩大搜索范围或者去其他地方探索吧！</p>
      </div>

      <!-- 胶囊列表 -->
      <div v-else class="capsules-list">
        <div
          v-for="capsule in capsules"
          :key="capsule.id"
          class="capsule-item"
          @click="handleCapsuleClick(capsule)"
        >
          <div class="capsule-header">
            <h4 class="capsule-title">{{ capsule.title }}</h4>
            <span class="distance-badge">{{ formatDistance(capsule.location.distance) }}</span>
          </div>

          <div class="capsule-meta">
            <span class="creator">by {{ capsule.creator_nickname }}</span>
            <span class="created-time">{{ formatTime(capsule.created_at) }}</span>
          </div>

          <div class="capsule-actions">
            <span class="visibility-badge" :class="`visibility-${capsule.visibility}`">
              {{ getVisibilityText(capsule.visibility) }}
            </span>

            <button
              v-if="capsule.can_unlock"
              class="unlock-btn"
              @click.stop="handleUnlock(capsule)"
            >
              🔓 解锁
            </button>

            <button
              v-else-if="capsule.is_unlocked"
              class="view-btn"
              @click.stop="handleView(capsule)"
            >
              👁️ 查看
            </button>

            <span v-else class="locked-indicator">🔒 已锁定</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { getCurrentLocation } from '@/utils/locationService'
import { getNearbyCapsules } from '@/api/new/hubApi'

export default {
  name: 'NearbyCapsulesExplorer',
  emits: ['capsule-select', 'unlock-request', 'view-request'],

  setup(props, { emit }) {
    // 响应式数据
    const currentLocation = ref(null)
    const isGettingLocation = ref(false)
    const isSearching = ref(false)
    const capsules = ref([])
    const error = ref(null)
    const hasSearched = ref(false)
    const searchRadius = ref(1000) // 默认1公里

    // 计算属性
    const locationText = computed(() => {
      if (!currentLocation.value) return '点击获取当前位置'

      const loc = currentLocation.value
      return `当前位置 (${loc.latitude.toFixed(4)}, ${loc.longitude.toFixed(4)})`
    })

    const locationStatusClass = computed(() => {
      if (!currentLocation.value) return 'location-inactive'
      return 'location-active'
    })

    // 方法
    const getCurrentLocationAndSearch = async () => {
      isGettingLocation.value = true
      error.value = null

      try {
        const location = await getCurrentLocation()

        if (location.success) {
          currentLocation.value = {
            latitude: location.latitude,
            longitude: location.longitude,
            accuracy: location.accuracy
          }

          // 自动搜索附近胶囊
          await searchNearbyCapsules()
        } else {
          throw new Error(location.message || '定位失败')
        }
      } catch (err) {
        error.value = `定位失败: ${err.message}`
        console.error('定位错误:', err)
      } finally {
        isGettingLocation.value = false
      }
    }

    const searchNearbyCapsules = async () => {
      if (!currentLocation.value) {
        error.value = '请先获取当前位置'
        return
      }

      isSearching.value = true
      error.value = null

      try {
        const result = await getNearbyCapsules({
          lat: currentLocation.value.latitude,
          lng: currentLocation.value.longitude,
          range: searchRadius.value,
          page: 1,
          size: 20
        })

        // 请求拦截器已经处理了响应，直接获取data
        if (result && result.capsules) {
          capsules.value = result.capsules || []
        } else {
          capsules.value = []
        }
        hasSearched.value = true
      } catch (err) {
        // 安全地获取错误信息，避免undefined
        const errorMessage = err?.message || err?.data?.message || err?.response?.data?.message || '未知错误'
        error.value = `搜索失败: ${errorMessage}`
        console.error('搜索错误:', err)
      } finally {
        isSearching.value = false
      }
    }

    const retrySearch = () => {
      if (currentLocation.value) {
        searchNearbyCapsules()
      } else {
        getCurrentLocationAndSearch()
      }
    }

    const handleCapsuleClick = (capsule) => {
      emit('capsule-select', capsule)
    }

    const handleUnlock = (capsule) => {
      emit('unlock-request', capsule, currentLocation.value)
    }

    const handleView = (capsule) => {
      emit('view-request', capsule)
    }

    // 格式化函数
    const formatDistance = (distance) => {
      if (distance < 1000) {
        return `${Math.round(distance)}m`
      } else {
        return `${(distance / 1000).toFixed(1)}km`
      }
    }

    const formatTime = (timeString) => {
      const date = new Date(timeString)
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const getVisibilityText = (visibility) => {
      const map = {
        'public': '校园公开',
        'campus': '校园公开',  // 处理后端返回的campus
        'friends': '好友可见',
        'private': '仅自己可见'
      }
      return map[visibility] || visibility
    }

    // 生命周期
    onMounted(() => {
      // 组件加载时自动获取位置并搜索
      getCurrentLocationAndSearch()
    })

    return {
      // 数据
      currentLocation,
      isGettingLocation,
      isSearching,
      capsules,
      error,
      hasSearched,
      searchRadius,

      // 计算属性
      locationText,
      locationStatusClass,

      // 方法
      getCurrentLocationAndSearch,
      searchNearbyCapsules,
      retrySearch,
      handleCapsuleClick,
      handleUnlock,
      handleView,
      formatDistance,
      formatTime,
      getVisibilityText
    }
  }
}
</script>

<style scoped>
.nearby-capsules-explorer {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.explorer-controls {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.location-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.location-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.location-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.location-icon {
  font-size: 18px;
  transition: all 0.3s ease;
}

.location-icon.location-active {
  color: #4CAF50;
}

.location-icon.location-inactive {
  color: #999;
}

.location-text {
  font-size: 14px;
  color: #666;
}

.location-btn {
  padding: 6px 12px;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.location-btn:hover {
  background: #1976D2;
}

.location-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.range-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.range-control label {
  font-size: 14px;
  color: #666;
}

.range-control select {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.results-header h3 {
  margin: 0;
  color: #333;
}

.results-count {
  color: #666;
  font-weight: normal;
  font-size: 14px;
}

.refresh-btn {
  background: none;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 6px;
  cursor: pointer;
  font-size: 14px;
}

.refresh-btn:hover:not(:disabled) {
  background: #f5f5f5;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #2196F3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon, .empty-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.retry-btn {
  margin-top: 12px;
  padding: 8px 16px;
  background: #FF5722;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.empty-hint {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

.capsules-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.capsule-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.capsule-item:hover {
  border-color: #2196F3;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.capsule-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.capsule-title {
  margin: 0;
  color: #333;
  font-size: 16px;
  flex: 1;
}

.distance-badge {
  background: #E3F2FD;
  color: #1976D2;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.capsule-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 12px;
  color: #666;
}

.capsule-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.visibility-badge {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
  text-transform: uppercase;
}

.visibility-public {
  background: #E8F5E8;
  color: #4CAF50;
}

.visibility-campus {
  background: #FFF3E0;
  color: #FF9800;
}

.visibility-private {
  background: #FFEBEE;
  color: #F44336;
}

.unlock-btn, .view-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.unlock-btn {
  background: #4CAF50;
  color: white;
}

.unlock-btn:hover {
  background: #388E3C;
}

.view-btn {
  background: #2196F3;
  color: white;
}

.view-btn:hover {
  background: #1976D2;
}

.locked-indicator {
  font-size: 12px;
  color: #999;
}
</style>