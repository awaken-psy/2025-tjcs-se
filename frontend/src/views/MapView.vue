<template>
  <AppHeader
    page-title="时光胶囊 · 地图"
    page-subtitle="探索校园内的胶囊，定位后可查看附近内容"
    :show-search="true"
    search-placeholder="搜索地点/胶囊标题/标签..."
    :actions="[
      { key: 'create', text: '创建胶囊', icon: '✚', type: 'primary' },
      { key: 'filter', text: '筛选', icon: '🔍', type: 'ghost' },
      { key: 'help', text: '帮助', icon: '❓', type: 'ghost' },
    ]"
    @go-hub="handleGoHub"
    @search="handleSearch"
    @action-click="handleHeaderAction" />

  <div class="map-main">
    <div class="map-sidebar">
      <div class="filter-card">
        <h3 class="filter-title">胶囊筛选</h3>
        <div class="filter-group">
          <label class="filter-label">可见性</label>
          <div class="filter-options">
            <label class="option-item"
              ><input type="radio" name="visibility" value="all" checked />
              所有胶囊</label
            >
            <label class="option-item"
              ><input type="radio" name="visibility" value="unlocked" />
              已解锁</label
            >
            <label class="option-item"
              ><input type="radio" name="visibility" value="mine" />
              我的胶囊</label
            >
          </div>
        </div>
        <div class="filter-group">
          <label class="filter-label">时间范围</label>
          <div class="filter-options">
            <label class="option-item"
              ><input type="radio" name="time" value="all" checked />
              不限</label
            >
            <label class="option-item"
              ><input type="radio" name="time" value="today" /> 今日</label
            >
            <label class="option-item"
              ><input type="radio" name="time" value="week" /> 一周内</label
            >
          </div>
        </div>
        <button class="btn small" @click="applyFilters">应用筛选</button>

        <!-- 筛选结果统计 -->
        <div class="filter-stats" v-if="capsules.length >= 0">
          <p class="stats-text">
            找到 <span class="stats-number">{{ capsules.length }}</span> 个胶囊
          </p>
          <p class="stats-detail" v-if="capsules.length === 0">
            没有找到符合条件的胶囊，请调整筛选条件
          </p>
        </div>
      </div>
    </div>

    <div class="map-container-wrapper">
      <MapContainer
        :capsule-data="capsules"
        :map-height="'1200px'"
        :is-loading-data="isLoading"
        @location-updated="handleLocationUpdate"
        @marker-clicked="handleCapsuleClick" />

      <div v-if="isLoading" class="loading-overlay">
        {{ loadingMessage }}
      </div>

      <!-- 左下角胶囊列表 -->
      <div
        class="capsules-list-panel"
        :class="{ minimized: !showCapsuleList }"
        v-if="capsules.length > 0"
      >
        <div class="panel-header" @click="toggleCapsuleList" style="cursor: pointer;">
          <h4>附近胶囊 ({{ capsules.length }})</h4>
          <button
            class="close-btn"
            @click.stop="toggleCapsuleList"
            :title="showCapsuleList ? '最小化' : '展开'"
          >
            {{ showCapsuleList ? '−' : '+' }}
          </button>
        </div>
        <div class="capsules-list" v-show="showCapsuleList">
          <div v-for="capsule in capsules.slice(0, 3)" :key="capsule.id" class="capsule-item">
            <div class="capsule-info">
              <h5 :title="capsule.title || '未命名胶囊'">{{ capsule.title || '未命名胶囊' }}</h5>
              <p>{{ capsule.content_preview || '暂无描述' }}</p>
              <div class="capsule-meta">
                <span class="visibility-badge">{{ getVisibilityText(capsule.visibility) }}</span>
                <span class="distance">{{ formatDistance(capsule.distance || 0) }}</span>
              </div>
            </div>
            <div class="capsule-actions">
              <button class="btn small" @click.stop="handleCapsuleClick(capsule.id)">查看</button>
              <button
                class="btn small primary"
                @click.stop="handleUnlockCapsule(capsule.id)"
                :disabled="capsule.is_unlocked || isUnlocking"
              >
                {{ capsule.is_unlocked ? '已解锁' : '解锁' }}
              </button>
            </div>
          </div>
          <div v-if="capsules.length > 3" class="more-indicator">
            还有 {{ capsules.length - 3 }} 个胶囊...
          </div>
        </div>
      </div>
    </div>
  </div>

  <CapsuleForm
    :is-show="showFormModal"
    :is-edit="isEditMode"
    :initial-data="currentEditData"
    @close="handleCloseForm"
    @submit="onCapsuleSubmitted" />
</template>

<script setup>
// #region import
import { ref, onMounted } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import CapsuleForm from '@/components/CapsuleForm.vue'
import MapContainer from '@/components/MapContainer.vue'
import { routeJump } from '@/utils/routeUtils'

// 引入用户提供的 API 函数
// 仅使用创建、获取列表、获取详情、更新、删除这几个api函数
import { getMyCapsules, getCapsuleDetail } from '@/api/new/capsulesApi'
import { getNearbyCapsules } from '@/api/new/hubApi'
import { unlockCapsule } from '@/api/new/unlockApi'

// #endregion

// #region 状态定义
// --- 1. 状态定义 ---
const defaultCenter = [120.529881, 31.026362]
const isLoading = ref(false) 
const loadingMessage = ref('')

// --- 2. 胶囊数据状态 ---
const capsules = ref([]) // 存储用于地图的胶囊列表 (用于 MapContainer:capsule-data)
const capsuleTotal = ref(0) // 新增：存储胶囊总数
const userLocation = ref({
  longitude: defaultCenter[0],
  latitude: defaultCenter[1],
})

// --- 2.1 新增状态 ---
const showCapsuleList = ref(true) // 控制胶囊列表显示
const isUnlocking = ref(false) // 解锁状态

// --- 3. 模态框/详情状态 ---
const showFormModal = ref(false)
const isEditMode = ref(false)
const currentEditData = ref(null)

// --- 3.1 筛选状态 ---
const filters = ref({
  visibility: 'all',
  time: 'all'
})

// #endregion

// --- 4. 地理定位更新函数 (对应步骤一) ---
/**
 * 接收 MapContainer 报告的最新定位
 * @param {Object} coords - { longitude: number, latitude: number }
 */
const handleLocationUpdate = (coords) => {
  userLocation.value = coords
  fetchCapsules()
}

// 胶囊 API 调用函数
const fetchCapsules = async () => {
  loadingMessage.value = '正在加载胶囊数据...'
  isLoading.value = true
  try {
    let res

    // 根据可见性筛选条件选择不同的API
    if (filters.value.visibility === 'mine') {
      // 获取我的胶囊
      res = await getMyCapsules({
        page: 1,
        size: 100,
        status: 'all'
      })
    } else {
      // 获取附近胶囊（默认情况）
      const requestParams = {
        lat: userLocation.value.latitude || 31.026362,  // 同济大学默认坐标
        lng: userLocation.value.longitude || 120.529881,
        range: 500000, // 5公里范围
        page: 1,
        size: 100
      }
      console.log('使用请求参数:', requestParams)
      console.log('当前userLocation:', userLocation.value)
      res = await getNearbyCapsules(requestParams)
    }

    console.log('API返回的原始数据:', res)
    console.log('请求参数:', {
      lat: userLocation.value.latitude || 31.026362,
      lng: userLocation.value.longitude || 120.529881,
      range: 5000,
      page: 1,
      size: 100
    })

    // 检查并处理返回的数据结构
    // 支持多种可能的API响应格式
    let capsuleList = []
    if (res && Array.isArray(res.capsules)) {
      capsuleList = res.capsules
    } else if (res && res.data && Array.isArray(res.data.capsules)) {
      capsuleList = res.data.capsules
    } else if (res && Array.isArray(res.data)) {
      capsuleList = res.data
    } else if (res && Array.isArray(res)) {
      capsuleList = res
    }

    if (capsuleList.length > 0) {
      console.log(`从附近API获取到 ${capsuleList.length} 个胶囊`)
      // 1. 映射数据结构，增加地图所需属性 (lng/lat)
      let processedCapsules = capsuleList.map((capsule) => {
        // 处理胶囊数据，支持不同的数据结构
        const capsuleData = capsule.capsule || capsule // 如果是{capsule: {...}, distance: ...}的结构

        return {
          ...capsuleData,
          // 保持原有的distance字段，如果有
          distance: capsule.distance || capsuleData.distance || 0,
          is_mine: filters.value.visibility === 'mine', // 只有在"我的胶囊"筛选时才标记为自己的
          liked: capsuleData.is_liked ?? false,
          collected: capsuleData.is_collected ?? false,
          is_unlocked: capsuleData.is_unlocked ?? false,
          // 关键：将位置信息映射为地图组件使用的 lng/lat
          // 处理两种可能的数据结构：直接的 latitude/longitude 或 location 对象
          lng: capsuleData?.longitude || capsuleData?.location?.longitude,
          lat: capsuleData?.latitude || capsuleData?.location?.latitude,
          content_preview: capsuleData.content_preview || capsuleData.content?.substring(0, 50) + '...' || '暂无描述',
        }
      })

      // 2. 应用前端筛选逻辑
      processedCapsules = processedCapsules.filter(capsule => {
        // 可见性筛选（除了"我的胶囊"外的其他筛选条件）
        if (filters.value.visibility === 'unlocked') {
          // 只显示已解锁的胶囊 (假设status为'published'表示已解锁)
          if (capsule.status !== 'published') return false
        }
        // 注意：当筛选为"all"或"mine"时，不需要进行前端可见性筛选

        // 时间筛选
        if (filters.value.time !== 'all') {
          const capsuleTime = new Date(capsule.created_at)
          const now = new Date()

          if (filters.value.time === 'today') {
            const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
            if (capsuleTime < today) return false
          } else if (filters.value.time === 'week') {
            const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
            if (capsuleTime < weekAgo) return false
          }
        }

        return true
      })

      // 3. 仅保留有有效坐标的胶囊用于地图显示
      const capsulesWithCoords = processedCapsules.filter(
        (c) => {
          // 基础坐标检查
          if (!c.lng || !c.lat || isNaN(c.lng) || isNaN(c.lat)) {
            return false
          }

          // 地理范围验证：过滤掉不在中国的坐标
          // 中国大致范围：经度73°-135°，纬度18°-54°
          if (c.lng < 73 || c.lng > 135 || c.lat < 18 || c.lat > 54) {
            console.warn(`过滤掉无效坐标: [${c.lng}, ${c.lat}] (超出中国范围)`)
            return false
          }

          // 上海同济大学附近范围检查（可选，更严格的过滤）
          // 上海大致范围：经度120.8°-122.2°，纬度30.7°-31.8°
          // if (c.lng < 120.8 || c.lng > 122.2 || c.lat < 30.7 || c.lat > 31.8) {
          //   console.warn(`过滤掉远离上海的坐标: [${c.lng}, ${c.lat}]`)
          //   return false
          // }

          return true
        }
      )

      // 4. 更新胶囊数据
      capsules.value = capsulesWithCoords

      console.log(`筛选后加载 ${capsules.value.length} 个有坐标的胶囊（原始数据：${capsuleList.length} 个）`)
    } else {
        console.log('附近胶囊为空，同济大学附近5公里范围内没有公开胶囊');
        console.log('提示：请检查其他账号创建的胶囊是否：');
        console.log('1. 设置为公开或校园可见');
        console.log('2. 位置在同济大学附近5公里范围内');
        console.log('3. 坐标设置正确');

        capsules.value = [];
    }

  } catch (error) {
    console.error('获取我的胶囊列表失败:', error)
    alert('加载胶囊数据失败，请稍后重试。')
    capsules.value = []; // 失败时清空列表
  } finally {
    isLoading.value = false
    loadingMessage.value = ''
  }
}

// --- 6. 标记点击处理函数 (步骤三：获取胶囊详情) ---
/**
 * 处理 MapContainer 报告的标记点击事件，获取详情并弹出模态框
 * @param {string} capsuleId - 被点击胶囊的 ID
 */
const handleCapsuleClick = async (capsuleId) => {
  console.log(`点击了胶囊 ID: ${capsuleId}。开始加载详情...`)

  // 1. 显示加载状态，并弹出模态框 (使用 LoginView.vue 中做好的页面)
  isEditMode.value = false // 查看详情，非编辑模式
  currentEditData.value = { loading: true, id: capsuleId } 
  showFormModal.value = true

  try {
    // 2. 调用 API 获取胶囊详情
    const response = await getCapsuleDetail(capsuleId)

    // 3. 更新详情数据，展示在 CapsuleForm 中
    currentEditData.value = response.data
  } catch (error) {
    console.error(`获取胶囊 ${capsuleId} 详情失败:`, error)
    currentEditData.value = { error: '加载详情失败，请重试或检查网络。' }
    alert('加载胶囊详情失败。')
  }
}

// --- 7. 模态框/表单事件处理函数 (保持不变) ---
const handleCloseForm = () => {
  showFormModal.value = false
  currentEditData.value = null
}

const onCapsuleSubmitted = async (result) => {
  console.log('Capsule Form Submitted:', result)

  // CapsuleForm已经处理了成功/失败的显示，这里只需要处理成功的情况
  // 如果result存在，说明操作成功
  if (result) {
    // 关闭表单
    handleCloseForm()

    // 刷新地图上的胶囊数据
    await fetchCapsules()
  } else {
    // 只有在result为null或undefined时才处理失败情况
    console.error('Capsule submission failed:', result)
  }
}

// --- 8. 筛选功能 ---
const applyFilters = () => {
  // 获取选中的筛选条件
  const visibilityRadio = document.querySelector('input[name="visibility"]:checked')
  const timeRadio = document.querySelector('input[name="time"]:checked')

  if (visibilityRadio) {
    filters.value.visibility = visibilityRadio.value
  }
  if (timeRadio) {
    filters.value.time = timeRadio.value
  }

  console.log('应用筛选:', filters.value)
  console.log('当前用户位置:', userLocation.value)

  // 重新加载胶囊数据
  fetchCapsules()
}

// --- 9. 其他处理函数 ---
// 切换胶囊列表显示
const toggleCapsuleList = () => {
  showCapsuleList.value = !showCapsuleList.value
}

// 获取可见性文字
const getVisibilityText = (visibility) => {
  switch (visibility) {
    case 'private': return '仅自己可见'
    case 'friends': return '好友可见'
    case 'campus':
    case 'public': return '校园公开'
    default: return '公开'
  }
}

// 格式化距离
const formatDistance = (distance) => {
  if (distance < 1000) return `${Math.round(distance)}米`
  return `${(distance / 1000).toFixed(1)}公里`
}

// 解锁胶囊
const handleUnlockCapsule = async (capsuleId) => {
  if (isUnlocking.value) return

  isUnlocking.value = true
  try {
    const result = await unlockCapsule({
      capsule_id: capsuleId,
      user_location: {
        latitude: userLocation.value.latitude,
        longitude: userLocation.value.longitude
      }
    })

    if (result.success) {
      alert('解锁成功！')
      // 刷新胶囊数据
      await fetchCapsules()
    } else {
      alert(`解锁失败：${result.message}`)
    }
  } catch (error) {
    console.error('解锁胶囊失败:', error)
    alert('解锁失败，请重试')
  } finally {
    isUnlocking.value = false
  }
}

// #region 顶部导航栏事件处理
const handleGoHub = () => {
  routeJump('/hubviews') 
}

const handleSearch = (keyword) => {
  console.log('用户搜索关键词:', keyword)
  // TODO: 在地图视图中，搜索功能通常意味着
  // 1. 搜索地名并移动地图中心。
  // 2. 搜索胶囊标题/标签，并刷新 fetchCapsules，可能需要一个新的 API 来支持关键词搜索。

  // 示例：可以结合当前筛选条件重新获取数据
  // fetchCapsules({ search: keyword }) 
  alert(`搜索功能（关键词："${keyword}"）待实现。`)
}

const handleHeaderAction = (actionKey) => {
  if (actionKey === 'create') {
    isEditMode.value = false
    currentEditData.value = null
    showFormModal.value = true

  } else if (actionKey === 'filter') {
    const sidebar = document.querySelector('.map-sidebar')
    if (sidebar) {
      // 在移动端，通过切换 'show' 类来显示/隐藏侧边栏
      sidebar.classList.toggle('show')
    }

  } else if (actionKey === 'help') {
    // 动作 3: 帮助
    alert('使用提示：\n\n1. 创建胶囊：点击"创建胶囊"按钮\n2. 查看胶囊：点击地图上的标记\n3. 筛选胶囊：使用左侧筛选面板\n4. 定位：允许浏览器获取位置信息')
  }
}
// #endregion

// --- 10. 生命周期钩子 ---
onMounted(() => {
  // 页面加载时立即获取胶囊数据，不等待定位
  fetchCapsules()

  // MapContainer 将在其内部的 mounted 钩子中处理地图初始化和初始定位
})
</script>

<style scoped>
/* ================================================= */
/* 设计令牌 (为组件内使用定义变量) */
/* ================================================= */
:root {
  --bg: #f5f8ff;
  --card: #ffffff;
  --muted: #6b7280;
  --accent: #6c8cff;
  --accent-hover: #5a7cff;
  --accent-light: rgba(108, 140, 255, 0.1);
  --danger: #ef4444;
  --shadow: 0 6px 18px rgba(12, 18, 36, 0.06);
  --shadow-deep: 0 0 20px rgba(0, 0, 0, 0.08); /* 新增: 用于侧边栏阴影 */
  --radius: 12px;
  --radius-sm: 8px;
}

/* ================================================= */
/* 整体布局样式 */
/* ================================================= */
.map-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.map-main {
  flex-grow: 1;
  display: flex;
}

/* 侧边栏/筛选栏主体 */
.map-sidebar {
  width: 280px;
  min-width: 280px;
  padding: 16px;
  background-color: var(--bg); /* 使用背景色 */
  box-shadow: var(--shadow-deep); /* 启用阴影 */
  z-index: 10;
  overflow-y: auto;
}

/* 包装器取代了原来的 .map-container */
.map-container-wrapper {
  flex-grow: 1;
  position: relative;
  height: 100%;
  display: flex;
  min-height: 0;
}
/* MapContainer 内部的 amap-container 高度已由 props 控制 */

.loading-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 5px;
}

/* ================================================= */
/* 筛选栏样式 (Filter Bar) - 新增或修正部分 */
/* ================================================= */
.filter-card {
  background: var(--card);
  padding: 20px;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.filter-title {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 20px 0;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 10px;
}

.filter-group {
  margin-bottom: 20px;
}

.filter-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 10px;
}

.filter-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-item {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: var(--muted);
  cursor: pointer;
  padding: 4px 0;
}

.option-item input[type='radio'] {
  margin-right: 10px;
  /* 基础美化，实际效果可能依赖浏览器默认样式 */
  accent-color: var(--accent);
}

/* 底部按钮样式 (参考 MapContainer.vue) */
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
  display: block; /* 确保按钮占据一行 */
  width: 100%;
  margin-top: 10px;
}

.btn:hover {
  background: var(--accent-hover);
  box-shadow: var(--shadow);
  transform: translateY(-1px);
}

.btn.small {
  padding: 6px 12px;
  font-size: 14px;
}

/* 筛选统计样式 */
.filter-stats {
  margin-top: 16px;
  padding: 12px;
  background: rgba(108, 140, 255, 0.05);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--accent);
}

.stats-text {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.stats-number {
  color: var(--accent);
  font-weight: 700;
  font-size: 16px;
}

.stats-detail {
  margin: 0;
  font-size: 12px;
  color: var(--muted);
  line-height: 1.4;
}

/* ================================================= */
/* 胶囊列表面板样式 */
/* ================================================= */
.capsules-list-panel {
  position: fixed;
  bottom: 80px;
  left: 20px;
  width: 280px;
  max-height: 300px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: var(--radius-sm);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 900;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: linear-gradient(135deg, var(--accent), #8b9eff);
  color: white;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
}

.panel-header h4 {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 16px;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: scale(1.1);
}

.capsules-list {
  max-height: 240px;
  overflow-y: auto;
}

.capsule-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
  transition: all 0.2s ease;
  min-height: 60px;
}

.capsule-item:hover {
  background: rgba(108, 140, 255, 0.05);
  transform: translateX(2px);
}

.capsule-item:last-child {
  border-bottom: none;
}

.capsule-info {
  flex: 1;
  margin-right: 8px;
  min-width: 0; /* 允许内容省略 */
}

.capsule-info h5 {
  margin: 0 0 2px 0;
  font-size: 12px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.capsule-info p {
  margin: 0 0 4px 0;
  font-size: 10px;
  color: var(--muted);
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.capsule-meta {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
}

.visibility-badge {
  font-size: 9px;
  padding: 1px 4px;
  border-radius: 3px;
  background: var(--accent-light);
  color: var(--accent);
  font-weight: 500;
}

.distance {
  font-size: 9px;
  color: var(--muted);
  font-weight: 500;
}

.capsule-actions {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex-shrink: 0;
}

.capsule-actions .btn {
  font-size: 9px;
  padding: 3px 6px;
  min-width: 45px;
  text-align: center;
  border-radius: 4px;
  font-weight: 500;
}

.capsule-actions .btn.primary {
  background: var(--accent);
  color: white;
  border: none;
}

.capsule-actions .btn.primary:hover {
  background: var(--accent-hover);
  transform: scale(1.05);
}

.capsule-actions .btn:not(.primary) {
  background: rgba(108, 140, 255, 0.1);
  color: var(--accent);
  border: 1px solid rgba(108, 140, 255, 0.2);
}

.capsule-actions .btn:not(.primary):hover {
  background: rgba(108, 140, 255, 0.2);
}

.capsule-actions .btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

.more-indicator {
  padding: 6px 12px;
  text-align: center;
  font-size: 10px;
  color: var(--muted);
  background: rgba(108, 140, 255, 0.05);
  border-top: 1px solid rgba(229, 231, 235, 0.3);
  font-weight: 500;
}

/* 添加最小化状态 */
.capsules-list-panel.minimized {
  max-height: 36px;
}

.capsules-list-panel.minimized .capsules-list {
  display: none;
}

.capsules-list-panel.minimized .panel-header {
  border-radius: var(--radius-sm);
}

/* 滚动条美化 */
.capsules-list::-webkit-scrollbar {
  width: 4px;
}

.capsules-list::-webkit-scrollbar-track {
  background: transparent;
}

.capsules-list::-webkit-scrollbar-thumb {
  background: rgba(108, 140, 255, 0.3);
  border-radius: 2px;
}

.capsules-list::-webkit-scrollbar-thumb:hover {
  background: rgba(108, 140, 255, 0.5);
}

/* ================================================= */
/* 媒体查询 (保持不变) */
/* ================================================= */
@media (max-width: 768px) {
  .map-main {
    flex-direction: column;
  }


  .map-sidebar {
    /* 移动端时默认隐藏，通过 show 类控制显示 */
    display: none;
    position: fixed;
    top: 70px;
    left: 20px;
    right: 20px;
    z-index: 90;
    background: var(--bg);
    padding: 20px;
    border-radius: var(--radius);
    box-shadow: var(--shadow-lg); /* 注意：shadow-lg 需在上层或此处定义 */
  }


  .map-sidebar.show {
    display: flex;
  }

  .map-container-wrapper {
    order: -1;
  }

}
</style>