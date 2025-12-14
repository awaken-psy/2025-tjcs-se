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
              <button class="btn small" @click.stop="handleViewCapsule(capsule.id)">查看</button>
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

  <CapsuleDetail
    :show-modal="showDetailModal"
    :detail-data="currentDetailData"
    @close="handleCloseDetail"
    @edit="handleEditCapsule"
    @share="handleShareCapsule"
    @openMedia="handleOpenMediaViewer" />
</template>

<script setup>
// #region 导入模块
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router' // 新增导入
import { useUserStore } from '@/store/user' // 新增导入
import AppHeader from '@/components/AppHeader.vue'
import CapsuleForm from '@/components/CapsuleForm.vue'
import MapContainer from '@/components/MapContainer.vue'
import CapsuleDetail from '@/components/CapsuleDetail.vue' // 新增导入
import { routeJump } from '@/utils/routeUtils'

// 引入用户提供的 API 函数
// 仅使用创建、获取列表、获取详情、更新、删除这几个api函数
import {
  getMyCapsules,
  getCapsuleDetail,
  updateCapsule, // 新增
  deleteCapsule, // 新增
} from '@/api/new/capsulesApi'
import { getNearbyCapsules } from '@/api/new/hubApi'
import { unlockCapsule } from '@/api/new/unlockApi'
import { likeCapsule, collectCapsule } from '@/api/new/interactionsApi' // 新增
// #endregion

// #region 状态定义
// 路由和用户状态
const router = useRouter()
const userStore = useUserStore()

const defaultCenter = [120.529881, 31.026362]
const isLoading = ref(false)
const loadingMessage = ref('')

// --- 2. 胶囊数据状态 ---
const capsules = ref([]) // 存储用于地图的胶囊列表 (用于 MapContainer:capsule-data)
const userLocation = ref({
  longitude: defaultCenter[0],
  latitude: defaultCenter[1],
})

// --- 2.1 新增状态 ---
const showCapsuleList = ref(true) // 控制胶囊列表显示
const isUnlocking = ref(false) // 解锁状态
const isProcessing = ref({}) // 用于处理点赞/删除等操作的加载状态 (从 MyCapsuleView 复用)

// --- 3. 模态框/详情状态 ---
const showFormModal = ref(false) // 表单（创建/编辑）
const isEditMode = ref(false)
const currentEditData = ref(null)

const showDetailModal = ref(false) // 详情页（从 MyCapsuleView 复用）
const currentDetailData = ref({}) // 详情数据（从 MyCapsuleView 复用）

// --- 3.1 筛选状态 ---
const filters = ref({
  visibility: 'all',
  time: 'all',
})
// #endregion

// #region 地图核心方法 
/**
 * 接收 MapContainer 报告的最新定位
 * @param {Object} coords - { longitude: number, latitude: number }
 */
const handleLocationUpdate = (coords) => {
  userLocation.value = coords
  fetchCapsules()
}

// 核心方法：加载地图上的胶囊列表
const fetchCapsules = async () => {
  loadingMessage.value = '正在加载胶囊数据...'
  isLoading.value = true
  try {
    let res

    //NOTE: 根据所有者不同调用不同的 API
    if (filters.value.visibility === 'mine') {
      // 获取我的胶囊
      res = await getMyCapsules({
        page: 1,
        size: 100,
        status: 'all',
      })
    } else {
      // 获取附近胶囊（默认情况）
      const requestParams = {
        lat: userLocation.value.latitude || 31.026362,
        lng: userLocation.value.longitude || 120.529881,
        range: 5000, // 5公里范围
        page: 1,
        size: 100,
      }
      res = await getNearbyCapsules(requestParams)
    }

    // 统一处理返回数据结构
    let capsuleList = []
    if (res && Array.isArray(res.capsules)) {
      capsuleList = res.capsules
    } 

    if (capsuleList.length > 0) {
      let processedCapsules = capsuleList.map((capsule) => {
        const capsuleData =  capsule
        return {
          ...capsuleData,
          distance: capsule.distance || capsuleData.distance || 0,
          is_mine: filters.value.visibility === 'mine',
          liked: capsuleData.is_liked ?? false,
          collected: capsuleData.is_collected ?? false,
          is_unlocked: capsuleData.is_unlocked ?? false,
          lng: capsuleData?.longitude || capsuleData?.location?.longitude,
          lat: capsuleData?.latitude || capsuleData?.location?.latitude,
          content_preview:
            capsuleData.content_preview ||
            capsuleData.content?.substring(0, 50) + '...' ||
            '暂无描述',
        }
      })

      // 应用前端筛选逻辑 (可见性和时间)
      processedCapsules = processedCapsules.filter((capsule) => {
        if (filters.value.visibility === 'unlocked' && capsule.status !== 'published') return false

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

      // 仅保留有有效坐标的胶囊用于地图显示
      const capsulesWithCoords = processedCapsules.filter(
        (c) => c.lng && c.lat && !isNaN(c.lng) && !isNaN(c.lat)
      )

      capsules.value = capsulesWithCoords
    } else {
      capsules.value = []
    }
  } catch (error) {
    console.error('获取胶囊列表失败:', error)
    alert('加载胶囊数据失败，请稍后重试。')
    capsules.value = []
  } finally {
    isLoading.value = false
    loadingMessage.value = ''
  }
}
// #endregion

// #region 胶囊交互方法 (从 MyCapsuleView 复用并调整)

/**
 * 处理 MapContainer 报告的标记点击事件，获取详情并弹出模态框 (委托给 handleViewCapsule)
 * @param {string} capsuleId - 被点击胶囊的 ID
 */
const handleCapsuleClick = (capsuleId) => {
  handleViewCapsule(capsuleId)
}

/**
 * 委托给 handleViewCapsule，获取详情并展示
 * @param {string} capsuleId
 */
const handleViewCapsule = async (capsuleId) => {
  const loadingKey = `view_${capsuleId}`
  isProcessing.value[loadingKey] = true

  // 1. 关闭表单和列表弹窗
  handleCloseForm()
  handleCloseDetail()

  // 2. 显示加载状态，并弹出模态框 (从 MyCapsuleView 复用)
  try {
    // 调用 API 获取详情数据
    const detail = await getCapsuleDetail(capsuleId)

    if (detail) {
      // 🌟 关键：根据 API 响应结构进行精确映射 (从 MyCapsuleView 复制)
      currentDetailData.value = {
        id: detail.id,
        title: detail.title,
        visibility: detail.visibility,
        content: detail.content,
        created_at: detail.created_at,
        status: detail.status,
        tags: detail.tags || [],
        // location 信息
        latitude: detail.location.latitude,
        longitude: detail.location.longitude,
        address: detail.location.address,
        // unlock_conditions 信息
        unlock_conditions_type: detail.unlock_conditions.type,
        unlock_conditions_password: detail.unlock_conditions.password || '',
        unlock_conditions_radius: detail.unlock_conditions.radius || 50,
        unlock_conditions_is_unlocked: detail.unlock_conditions.is_unlocked || false,
        unlock_conditions_unlockable_time: detail.unlock_conditions.unlockable_time || null,
        // stats 信息
        view_count: detail.stats.view_count || 0,
        like_count: detail.stats.like_count || 0,
        comment_count: detail.stats.comment_count || 0,
        unlock_count: detail.stats.unlock_count || 0,
        is_liked: detail.stats.is_liked ?? false,
        is_collected: detail.stats.is_collected ?? false,
        // media_files 信息
        media_files: detail.media_files || [],
        // creator 信息
        is_mine: detail.creator?.user_id === userStore.user_id,
      }

      showDetailModal.value = true
    } else {
      console.error(`未找到胶囊 ${capsuleId}`)
      alert('未找到胶囊信息')
    }
  } catch (error) {
    console.error(`查看胶囊详情(${capsuleId})失败：`, error)
    alert('查看详情失败，请稍后重试')
  } finally {
    isProcessing.value[loadingKey] = false
  }
}

const handleCloseDetail = () => {
  showDetailModal.value = false
  currentDetailData.value = {}
}

const handleLikeCapsule = async (capsuleId) => {
  const capsule = capsules.value.find((c) => c.id === capsuleId)
  if (!capsule) return

  isProcessing.value[`like_${capsuleId}`] = true
  try {
    await likeCapsule(capsuleId)
    await fetchCapsules()
  } catch (error) {
    console.error(`点赞胶囊(${capsuleId})失败：`, error)
    alert('点赞失败，请稍后重试')
  } finally {
    isProcessing.value[`like_${capsuleId}`] = false
  }
}

const handleCollectCapsule = async (capsuleId) => {
  const capsule = capsules.value.find((c) => c.id === capsuleId)
  if (!capsule) return

  isProcessing.value[`collect_${capsuleId}`] = true
  try {
    await collectCapsule(capsuleId)
    await fetchCapsules()
  } catch (error) {
    console.error(`收藏胶囊(${capsuleId})失败：`, error)
    alert('收藏失败，请稍后重试')
  } finally {
    isProcessing.value[`collect_${capsuleId}`] = false
  }
}

const handleEditCapsule = (capsuleId) => {
  // 💡 优化：从当前列表数据中查找，避免重复 API 调用
  const capsule = capsules.value.find((c) => c.id === capsuleId)

  if (capsule) {
    currentEditData.value = {
      ...capsule,
    }

    isEditMode.value = true
    showFormModal.value = true

    // 关闭详情弹窗
    handleCloseDetail()
  } else {
    alert('编辑失败：未能找到该胶囊的列表数据。')
  }
}

const handleDeleteCapsule = async (capsuleId) => {
  if (!confirm('确定要删除该胶囊吗？此操作不可恢复！')) return

  isProcessing.value[`delete_${capsuleId}`] = true
  try {
    await deleteCapsule(capsuleId)
    alert('删除成功！')
    await fetchCapsules()
  } catch (error) {
    console.error(`删除胶囊(${capsuleId})失败：`, error)
    alert('删除失败，请稍后重试')
  } finally {
    isProcessing.value[`delete_${capsuleId}`] = false
  }
}

const handleShareCapsule = (capsule) => {
  // 💡 最佳实践：此处应调用一个专用的分享服务函数
  console.log(`准备分享胶囊：${capsule.title}`)
  alert(`分享胶囊：${capsule.title}（后续对接分享接口，支持复制链接/微信分享）`)
}

// #endregion

// #region 模态框/表单事件处理函数 (更新)
const handleCloseForm = () => {
  showFormModal.value = false
  currentEditData.value = null
  isEditMode.value = false
}

// 替换原来的 onCapsuleSubmitted，使用 MyCapsuleView 中更强大的逻辑
const onCapsuleSubmitted = async (result) => {
  console.log('Capsule Form Submitted:', result)

  if (!result) {
    handleCloseForm()
    return
  }

  // 统一的请求数据结构
  const payload = {
    title: result.title,
    content: result.content,
    visibility: result.visibility,
    tags: result.tags,
    location: result.location,
    unlock_conditions: result.unlock_conditions,
    media_files: result.media_files || [],
  }

  if (isEditMode.value) {
    // 🚀 更新模式 (从 MyCapsuleView 复用)
    const capsuleId = currentEditData.value.id
    if (!capsuleId) {
      alert('编辑失败：无法获取胶囊ID。')
      handleCloseForm()
      return
    }

    try {
      console.log(`📡 准备更新胶囊ID: ${capsuleId}`, payload)
      await updateCapsule(capsuleId, payload)
      alert('胶囊更新成功！')

      // 重新加载列表数据以刷新地图
      await fetchCapsules()
    } catch (error) {
      console.error(`更新胶囊(${capsuleId})失败:`, error)
      alert(`胶囊更新失败：${error.message || '未知错误'}`)
    }
  } else {
    // 🆕 创建模式 (假设 CapsuleForm 已经完成了 createCapsule API 调用)
    console.log('创建模式：CapsuleForm已成功提交。')
    // 重新加载列表以获取最新创建的胶囊
    await fetchCapsules()
  }

  handleCloseForm() // 关闭表单
}
// #endregion

// #region 筛选功能 (保留)
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
  // 重新加载胶囊数据
  fetchCapsules()
}
// #endregion

// #region 其他处理函数 (保留/调整)
// 切换胶囊列表显示
const toggleCapsuleList = () => {
  showCapsuleList.value = !showCapsuleList.value
}

// 获取可见性文字
const getVisibilityText = (visibility) => {
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

// 格式化距离
const formatDistance = (distance) => {
  if (distance < 1000) return `${Math.round(distance)}米`
  return `${(distance / 1000).toFixed(1)}公里`
}

// 解锁胶囊 (保留)
const handleUnlockCapsule = async (capsuleId) => {
  if (isUnlocking.value) return

  isUnlocking.value = true
  try {
    const result = await unlockCapsule({
      capsule_id: capsuleId,
      user_location: {
        latitude: userLocation.value.latitude,
        longitude: userLocation.value.longitude,
      },
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

const handleGoHub = () => {
  routeJump('/hubviews')
}
const handleSearch = (keyword) => {}

const handleHeaderAction = (actionKey) => {
  if (actionKey === 'create') {
    // 显示创建胶囊表单
    isEditMode.value = false
    currentEditData.value = null
    showFormModal.value = true
  } else if (actionKey === 'filter') {
    // 切换筛选侧边栏显示（移动端）
    const sidebar = document.querySelector('.map-sidebar')
    if (sidebar) {
      sidebar.classList.toggle('show')
    }
  } else if (actionKey === 'help') {
    alert(
      '使用提示：\n\n1. 创建胶囊：点击"创建胶囊"按钮\n2. 查看胶囊：点击地图上的标记或列表中的"查看"\n3. 筛选胶囊：使用左侧筛选面板\n4. 定位：允许浏览器获取位置信息'
    )
  }
}


onMounted(() => {
  // 页面加载时立即获取胶囊数据，不等待定位
  fetchCapsules()
})
// #endregion
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
  --shadow-deep: 0 0 20px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.1); /* 新增：用于移动端侧边栏 */
  --radius: 12px;
  --radius-sm: 8px;
}

/* ================================================= */
/* 整体布局样式 */
/* ================================================= */
.map-page {
  /* 确保页面占满视口 */
  width: 100%; 
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.map-main {
  flex-grow: 1;
  display: flex;
  min-height: 0; /* 解决 flex 容器内元素溢出问题 */
}

/* 侧边栏/筛选栏主体 */
.map-sidebar {
  width: 280px;
  min-width: 280px;
  padding: 16px;
  background-color: var(--bg);
  box-shadow: var(--shadow-deep);
  z-index: 10;
  overflow-y: auto;
  flex-shrink: 0; /* 防止被地图压缩 */
}

/* 包装器取代了原来的 .map-container */
.map-container-wrapper {
  flex-grow: 1;
  position: relative;
  height: 100%;
  display: flex;
  min-height: 0;
}

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
  font-size: 14px;
}

/* ================================================= */
/* 筛选栏样式 (Filter Bar) */
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
  accent-color: var(--accent);
}

/* 底部按钮样式 */
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
  display: block;
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
  position: absolute; /* 修改为 absolute，以便在 map-container-wrapper 内部定位 */
  bottom: 20px; /* 调整 bottom 距离 */
  left: 20px; /* 调整 left 距离 */
  width: 280px;
  max-height: 300px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: var(--radius-sm);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 900;
  overflow: hidden;
  backdrop-filter: blur(10px);
  transition: max-height 0.3s ease-out; /* 增加过渡效果 */
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
  min-width: 0;
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
  border-radius: var(--radius-sm);
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
/* 媒体查询 (响应式) */
/* ================================================= */
@media (max-width: 768px) {
  .map-main {
    flex-direction: column;
  }

  /* 移动端侧边栏 */
  .map-sidebar {
    /* 移动端时默认隐藏，通过 show 类控制显示 */
    display: none;
    position: fixed;
    top: 60px; /* 假设 AppHeader 高度在 60px 左右 */
    left: 10px;
    right: 10px;
    width: auto; /* 占据父容器宽度 */
    max-height: 80vh; /* 限制最大高度 */
    z-index: 90;
    padding: 20px;
    box-shadow: var(--shadow-lg); 
    /* 确保在 show 状态下以 flex 方式展示内容 */
  }

  .map-sidebar.show {
    /* 修复：在移动端显示时，应保持 block/flex，使其内容垂直排列 */
    display: block; 
  }

  .map-container-wrapper {
    order: -1;
  }
  
  /* 移动端胶囊列表面板调整 */
  .capsules-list-panel {
    bottom: 10px;
    left: 50%;
    transform: translateX(-50%);
    width: 95%;
    max-width: 350px;
  }
}
</style>