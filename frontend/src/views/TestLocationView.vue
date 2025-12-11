<template>
  <div class="test-location-page">
    <div class="test-container">
      <h1>📍 地理位置胶囊查找测试</h1>

      <div class="test-section">
        <h2>1. 地理位置获取测试</h2>
        <button @click="testGetLocation" :disabled="locationLoading">
          {{ locationLoading ? '定位中...' : '🎯 测试获取位置' }}
        </button>

        <div v-if="locationResult" class="result-box">
          <h3>📌 定位结果:</h3>
          <pre>{{ JSON.stringify(locationResult, null, 2) }}</pre>
        </div>

        <div v-if="locationError" class="error-box">
          <h3>❌ 定位错误:</h3>
          <p>{{ locationError }}</p>
        </div>
      </div>

      <div class="test-section">
        <h2>2. 附近胶囊查找测试</h2>
        <button @click="testSearchCapsules" :disabled="searchLoading || !locationResult">
          {{ searchLoading ? '搜索中...' : '🔍 测试查找胶囊' }}
        </button>

        <div class="search-params">
          <label>
            搜索半径:
            <select v-model="testRadius">
              <option value="100">100米</option>
              <option value="500">500米</option>
              <option value="1000">1公里</option>
              <option value="5000">5公里</option>
            </select>
          </label>
        </div>

        <div v-if="searchResult" class="result-box">
          <h3>🎯 搜索结果:</h3>
          <p><strong>找到 {{ searchResult.capsules?.length || 0 }} 个胶囊</strong></p>
          <pre>{{ JSON.stringify(searchResult, null, 2) }}</pre>
        </div>

        <div v-if="searchError" class="error-box">
          <h3>❌ 搜索错误:</h3>
          <p>{{ searchError }}</p>
        </div>
      </div>

      <div class="test-section">
        <h2>3. NearbyCapsulesExplorer 组件测试</h2>
        <NearbyCapsulesExplorer
          @capsule-select="handleCapsuleSelect"
          @unlock-request="handleUnlockRequest"
          @view-request="handleViewRequest"
        />
      </div>

      <div class="test-section">
        <h2>4. 测试日志</h2>
        <div class="log-box">
          <div v-for="(log, index) in logs" :key="index" class="log-item">
            <span class="log-time">{{ log.time }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
        <button @click="clearLogs">清空日志</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { getCurrentLocation } from '@/utils/locationService'
import { getNearbyCapsules } from '@/api/new/hubApi'
import NearbyCapsulesExplorer from '@/components/NearbyCapsulesExplorer.vue'

export default {
  name: 'TestLocationView',
  components: {
    NearbyCapsulesExplorer
  },

  setup() {
    // 状态管理
    const locationLoading = ref(false)
    const locationResult = ref(null)
    const locationError = ref(null)

    const searchLoading = ref(false)
    const searchResult = ref(null)
    const searchError = ref(null)
    const testRadius = ref(1000)

    const logs = ref([])

    // 添加日志
    const addLog = (message) => {
      logs.value.push({
        time: new Date().toLocaleTimeString(),
        message
      })
    }

    // 清空日志
    const clearLogs = () => {
      logs.value = []
    }

    // 测试获取位置
    const testGetLocation = async () => {
      locationLoading.value = true
      locationError.value = null
      locationResult.value = null

      addLog('开始获取地理位置...')

      try {
        const result = await getCurrentLocation()
        locationResult.value = result

        if (result.success) {
          addLog(`✅ 定位成功: ${result.latitude}, ${result.longitude} (精度: ${result.accuracy}m)`)
        } else {
          locationError.value = result.message || '定位失败'
          addLog(`❌ 定位失败: ${locationError.value}`)
        }
      } catch (error) {
        locationError.value = error.message
        addLog(`❌ 定位异常: ${error.message}`)
      } finally {
        locationLoading.value = false
      }
    }

    // 测试查找胶囊
    const testSearchCapsules = async () => {
      if (!locationResult.value || !locationResult.value.success) {
        addLog('❌ 请先获取位置信息')
        return
      }

      searchLoading.value = true
      searchError.value = null
      searchResult.value = null

      addLog(`🔍 开始搜索半径${testRadius.value}米内的胶囊...`)

      try {
        const result = await getNearbyCapsules({
          lat: locationResult.value.latitude,
          lng: locationResult.value.longitude,
          range: testRadius.value,
          page: 1,
          size: 20
        })

        searchResult.value = result

        if (result.success) {
          const count = result.data?.capsules?.length || 0
          addLog(`✅ 搜索完成: 找到 ${count} 个胶囊`)
        } else {
          searchError.value = result.message || '搜索失败'
          addLog(`❌ 搜索失败: ${searchError.value}`)
        }
      } catch (error) {
        searchError.value = error.message
        addLog(`❌ 搜索异常: ${error.message}`)
      } finally {
        searchLoading.value = false
      }
    }

    // 组件事件处理
    const handleCapsuleSelect = (capsule) => {
      addLog(`📍 选择胶囊: ${capsule.title} (${capsule.id})`)
    }

    const handleUnlockRequest = (capsule, location) => {
      addLog(`🔓 尝试解锁胶囊: ${capsule.title} 位置: ${location.latitude}, ${location.longitude}`)
    }

    const handleViewRequest = (capsule) => {
      addLog(`👁️ 查看胶囊: ${capsule.title} (${capsule.id})`)
    }

    // 生命周期
    onMounted(() => {
      addLog('🚀 测试页面加载完成')
    })

    return {
      // 数据
      locationLoading,
      locationResult,
      locationError,
      searchLoading,
      searchResult,
      searchError,
      testRadius,
      logs,

      // 方法
      testGetLocation,
      testSearchCapsules,
      clearLogs,
      handleCapsuleSelect,
      handleUnlockRequest,
      handleViewRequest
    }
  }
}
</script>

<style scoped>
.test-location-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.test-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.test-section {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
}

.test-section h2 {
  margin: 0 0 16px 0;
  color: #333;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 8px;
}

.search-params {
  margin: 12px 0;
}

.search-params label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
}

.search-params select {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  padding: 10px 20px;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  margin-bottom: 16px;
}

button:hover:not(:disabled) {
  background: #1976D2;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.result-box {
  background: #E8F5E8;
  border: 1px solid #4CAF50;
  border-radius: 6px;
  padding: 16px;
  margin-top: 16px;
}

.result-box h3 {
  margin: 0 0 12px 0;
  color: #2E7D32;
}

.result-box pre {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.error-box {
  background: #FFEBEE;
  border: 1px solid #F44336;
  border-radius: 6px;
  padding: 16px;
  margin-top: 16px;
}

.error-box h3 {
  margin: 0 0 8px 0;
  color: #C62828;
}

.error-box p {
  margin: 0;
  color: #D32F2F;
}

.log-box {
  background: #f8f8f8;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 12px;
  max-height: 400px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  margin-bottom: 12px;
}

.log-item {
  display: flex;
  gap: 8px;
  padding: 2px 0;
  border-bottom: 1px solid #eee;
}

.log-time {
  color: #666;
  font-size: 12px;
  min-width: 80px;
}

.log-message {
  color: #333;
  font-size: 12px;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}
</style>