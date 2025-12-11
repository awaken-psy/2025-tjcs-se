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
    @go-hub-user="handleGoHub"
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
        <button class="btn small">应用筛选</button>
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
import { ref, onMounted } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import CapsuleForm from '@/components/CapsuleForm.vue'
import MapContainer from '@/components/MapContainer.vue'

// 引入用户提供的 API 函数
// 仅使用创建、获取列表、获取详情、更新、删除这几个api函数
import { getMyCapsules, getCapsuleDetail } from '@/api/new/capsulesApi'

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

// --- 3. 模态框/详情状态 ---
const showFormModal = ref(false)
const isEditMode = ref(false)
const currentEditData = ref(null)

// --- 4. 地理定位更新函数 (对应步骤一) ---
/**
 * 接收 MapContainer 报告的最新定位
 * @param {Object} coords - { longitude: number, latitude: number }
 */
const handleLocationUpdate = (coords) => {
  console.log('MapContainer 报告新的定位:', coords)
  userLocation.value = coords

  // 定位成功后，立即开始加载胶囊 (步骤二)
  fetchCapsules()
}

// --- 5. 胶囊 API 调用函数 (步骤二：获取我的胶囊列表) ---
const fetchCapsules = async () => {
  loadingMessage.value = '正在加载胶囊数据...'
  isLoading.value = true
  try {
    // 调用 API 获取胶囊列表，使用用户提供的参数结构
    const res = await getMyCapsules({
      page: 1,
      size: 20,
      status: 'all',
    })

    // 检查并处理返回的数据结构
    if (res && Array.isArray(res.capsules)) {
      // 1. 映射数据结构，增加地图所需属性 (lng/lat)
      const processedCapsules = res.capsules.map((capsule) => ({
        ...capsule,
        is_mine: true, // 假设 getMyCapsules 返回的都是自己的
        liked: capsule.is_liked ?? false, 
        collected: capsule.is_collected ?? false, 
        // 关键：将位置信息映射为地图组件使用的 lng/lat
        lng: capsule?.longitude, 
        lat: capsule?.latitude, 
      }))
      
      // 2. 更新总数
      capsuleTotal.value = res.capsules.length

      // 3. 仅保留有坐标的胶囊用于地图显示，并更新到 capsules 状态
      // 这是实现“按照定位打印一个气泡”的关键步骤
      capsules.value = processedCapsules.filter(
        (c) => c.lng && c.lat
      )
      
      console.log(`成功加载 ${capsules.value.length} 个有坐标的胶囊。`)
    } else {
        console.warn('API 返回数据结构异常或列表为空:', res);
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

const onCapsuleSubmitted = (data) => {
  console.log('Capsule Form Submitted:', data)
  handleCloseForm()
}

// --- 8. 其他处理函数 (保持不变) ---
const handleGoHub = () => {}
const handleSearch = (keyword) => {}
const handleHeaderAction = (actionKey) => {}

// --- 9. 生命周期钩子 ---
onMounted(() => {
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