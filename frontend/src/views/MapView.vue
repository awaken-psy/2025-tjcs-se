<template>
  <AppHeader
    page-title="时光胶囊 · 地图"
    page-subtitle="探索校园内的胶囊，定位后可查看附近内容"
    :show-search="false"
    search-placeholder="搜索地点/胶囊标题/标签..."
    :actions="[
      { key: 'create', text: '创建胶囊', icon: '✚', type: 'primary' },
      { key: 'help', text: '帮助', icon: '❓', type: 'ghost' },
    ]"
    @go-hub="handleGoHub"
    @search="handleSearch"
    @action-click="handleHeaderAction" />

  <div class="map-main">
    <!-- <div class="map-sidebar">
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
    </div> -->

    <div class="map-sidebar">
      <div class="filter-card">
        <h3 class="filter-title">胶囊探索筛选</h3>

        <div class="filter-group">
          <label class="filter-label">🔍 关键词检索</label>
          <input
            type="text"
            v-model="filters.keyword"
            placeholder="输入地点、标题或标签..."
            class="filter-input"
            @keyup.enter="applyFilters" />
        </div>

        <div class="filter-group">
          <label class="filter-label">📅 创建时间范围</label>
          <div class="date-range-inputs">
            <input
              type="date"
              v-model="filters.startTime"
              class="filter-input date-input" />
            <span class="date-sep">至</span>
            <input
              type="date"
              v-model="filters.endTime"
              class="filter-input date-input" />
          </div>
        </div>

        <div class="filter-group">
          <label class="filter-label">👁️ 可见范围</label>
          <select v-model="filters.visibility" class="filter-input">
            <option value="all">全部可见性</option>
            <option value="public">公开 (所有人)</option>
            <option value="friend">好友可见</option>
            <option value="private">私密 (仅自己)</option>
          </select>
        </div>

        <div class="filter-group">
          <label class="filter-label">🔒 解锁要求</label>
          <select v-model="filters.unlockType" class="filter-input">
            <option value="all">全部解锁方式</option>
            <option value="public">直接解锁 (无门槛)</option>
            <option value="password">密码解锁</option>
            <option value="private">仅限创建者解锁</option>
          </select>
        </div>

        <div class="filter-actions">
          <button class="btn primary apply-btn" @click="applyFilters">
            应用筛选条件
          </button>
          <button class="btn ghost small reset-btn" @click="resetFilters">
            清空重置
          </button>
        </div>

        <div class="filter-stats" v-if="capsules.length >= 0">
          <p class="stats-text">
            地图显示:
            <span class="stats-number">{{ capsules.length }}</span> 个胶囊
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
        @marker-clicked="handleCapsuleClick"
        @view-capsule="handleViewCapsule" />

      <div v-if="isLoading" class="loading-overlay">
        {{ loadingMessage }}
      </div>

      <div
        class="capsules-list-panel"
        :class="{ minimized: !showCapsuleList }"
        v-if="capsules.length > 0">
        <div
          class="panel-header"
          @click="toggleCapsuleList"
          style="cursor: pointer">
          <h4>附近胶囊 ({{ capsules.length }})</h4>
          <button
            class="close-btn"
            @click.stop="toggleCapsuleList"
            :title="showCapsuleList ? '最小化' : '展开'">
            {{ showCapsuleList ? '−' : '+' }}
          </button>
        </div>
        <div class="capsules-list" v-show="showCapsuleList">
          <div
            v-for="capsule in capsules.slice(0, 3)"
            :key="capsule.id"
            class="capsule-item">
            <div class="capsule-info">
              <h5 :title="capsule.title || '未命名胶囊'">
                {{ capsule.title || '未命名胶囊' }}
              </h5>
              <p>{{ capsule.content_preview || '暂无描述' }}</p>
              <div class="capsule-meta">
                <span class="visibility-badge">{{
                  getVisibilityText(capsule.visibility)
                }}</span>
                <span class="distance">{{
                  formatDistance(capsule.distance || 0)
                }}</span>
              </div>
            </div>
            <div class="capsule-actions">
              <button
                class="btn small"
                @click.stop="handleViewCapsule(capsule.id)">
                查看
              </button>
              <button
                class="btn small primary"
                @click.stop="handleUnlockCapsule(capsule.id)"
                :disabled="capsule.is_unlocked || isUnlocking">
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
    :edit-data="currentEditData"
    @close="handleCloseForm"
    @submit="onCapsuleCreated" />

  <CapsuleDetail
    :show-modal="showDetailModal"
    :detail-data="currentDetailData"
    @close="showDetailModal = false" />

  <GenericModal
    :is-show="showUnlockModal"
    title="解锁时光胶囊"
    width="450px"
    @close="showUnlockModal = false">
    <template #default>
      <div v-if="currentUnlockCapsule" class="unlock-form-content">
        <p class="unlock-tip">
          您正尝试解锁胶囊 **{{ currentUnlockCapsule.title }}**。
        </p>

        <div
          v-if="currentUnlockCapsule.unlock_conditions_type === 'password'"
          class="form-group password-group">
          <label for="unlock-password">🔑 请输入解锁密码：</label>
          <input
            id="unlock-password"
            type="password"
            v-model="unlockPasswordInput"
            placeholder="输入密码"
            @keyup.enter="handleConfirmUnlock"
            :disabled="isProcessing[`unlock_${currentUnlockCapsule.id}`]" />
        </div>

        <div
          v-else-if="currentUnlockCapsule.unlock_conditions_type === 'location'"
          class="location-tip">
          <p>🗺️ 这是一个**地点触发**的胶囊。</p>
          <p class="note">
            点击“开始解锁”后，系统将获取您的位置信息并进行半径校验。
          </p>
        </div>

        <div v-else class="location-tip">
          <p>🔓 正在尝试解锁。</p>
          <p class="note">
            点击“开始解锁”后，系统将获取您的位置（如需）并进行 API 解锁请求。
          </p>
        </div>
      </div>
    </template>
    <template #actions>
      <button
        class="btn ghost"
        @click="showUnlockModal = false"
        :disabled="isProcessing[`unlock_${currentUnlockCapsule?.id}`]">
        取消
      </button>
      <button
        class="btn primary"
        @click="handleConfirmUnlock"
        :disabled="
          (currentUnlockCapsule?.unlock_conditions_type === 'password' &&
            !unlockPasswordInput) ||
          isProcessing[`unlock_${currentUnlockCapsule?.id}`]
        ">
        <i
          v-if="isProcessing[`unlock_${currentUnlockCapsule?.id}`]"
          class="fas fa-spinner fa-spin"></i>
        <span v-else>
          {{
            currentUnlockCapsule?.unlock_conditions_type === 'password'
              ? '提交密码并解锁'
              : '开始解锁'
          }}
        </span>
      </button>
    </template>
  </GenericModal>
</template>

<script setup>
// #region 导入模块
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import AppHeader from '@/components/AppHeader.vue'
import CapsuleForm from '@/components/CapsuleForm.vue'
import MapContainer from '@/components/MapContainer.vue'
import CapsuleDetail from '@/components/CapsuleDetail.vue'
import GenericModal from '@/components/GenericModal.vue'
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
const showCapsuleList = ref(true)
const isUnlocking = ref(false)
const isProcessing = ref({})

// === 解锁相关状态 (从 MyCapsuleView 复用) ===
const showUnlockModal = ref(false)
const currentUnlockCapsule = ref(null) // 暂存待解锁的胶囊对象
const unlockPasswordInput = ref('') // 暂存用户输入的密码
// ===========================================

// --- 3. 模态框/详情状态 ---
const showFormModal = ref(false) // 表单（创建/编辑）
const isEditMode = ref(false)
const currentEditData = ref(null)

const showDetailModal = ref(false) // 详情页（从 MyCapsuleView 复用）
const currentDetailData = ref({}) // 详情数据（从 MyCapsuleView 复用）

// --- 3.1 筛选状态 ---
const filters = ref({
  keyword: '', // 搜索标题/标签
  startTime: '', // 开始时间
  endTime: '', // 结束时间
  visibility: 'all', // 可见性: all, public, friends, private
  unlockType: 'all', // 解锁方式: all, any, password, mine_only
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
  isLoading.value = true
  loadingMessage.value = '正在根据条件过滤胶囊...'
  
  try {
    const res = await getNearbyCapsules({
      lat: userLocation.value.latitude,
      lng: userLocation.value.longitude,
      range: 500000,
      page: 1,
      size: 300 
    })

    let rawList = res?.capsules || []

    // 执行多维度前端过滤
    const filteredList = rawList.filter(capsule => {
      // 1. 关键词过滤 (标题或标签数组)
      if (filters.value.keyword) {
        const kw = filters.value.keyword.toLowerCase()
        const titleMatch = capsule.title?.toLowerCase().includes(kw)
        const tagMatch = capsule.tags?.some(tag => tag.toLowerCase().includes(kw))
        if (!titleMatch && !tagMatch) return false
      }

      // 2. 时间范围过滤 (创建日期)
      if (filters.value.startTime || filters.value.endTime) {
        const capsuleDate = new Date(capsule.created_at).setHours(0,0,0,0)
        if (filters.value.startTime && capsuleDate < new Date(filters.value.startTime).getTime()) return false
        if (filters.value.endTime && capsuleDate > new Date(filters.value.endTime).getTime()) return false
      }

      // 3. 可见性匹配 (public, friend, private)
      if (filters.value.visibility !== 'all') {
        if (capsule.visibility !== filters.value.visibility) return false
      }

      // 4. 解锁方式匹配 (通过 unlock_conditions.type)
      if (filters.value.unlockType !== 'all') {
        const currentUnlockType = capsule.unlock_conditions?.type || capsule.unlock_conditions_type
        if (currentUnlockType !== filters.value.unlockType) return false
      }

      return true
    })

    // 格式化数据并映射坐标
    capsules.value = filteredList.map(c => ({
      ...c,
      lng: c.longitude || c.location?.longitude,
      lat: c.latitude || c.location?.latitude,
      is_unlocked: c.is_unlocked ?? false
    })).filter(c => c.lng && c.lat && !isNaN(c.lng))

  } catch (error) {
    console.error('筛选请求失败:', error)
  } finally {
    isLoading.value = false
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
 * 委托给 handleViewCapsule，获取详情并展示 (从 MyCapsuleView.vue 复制并调整)
 * @param {string} capsuleId
 */
const handleViewCapsule = async (capsuleId) => {
  const loadingKey = `view_${capsuleId}`
  isProcessing.value[loadingKey] = true
  // 1. 关闭表单和解锁弹窗
  handleCloseForm()
  handleCloseDetail()

  try {
    // 调用 API 获取详情数据
    const detail = await getCapsuleDetail(capsuleId)
    if (detail) {
      // 🌟 关键：数据映射逻辑 (从 MyCapsuleView.vue 复用)
      currentDetailData.value = {
        id: detail.id,
        title: detail.title,
        content: detail.content,
        created_at: detail.created_at,
        status: detail.status,
        visibility: detail.visibility,
        tags: detail.tags || [],
        // location & unlock conditions
        latitude: detail.location?.latitude,
        longitude: detail.location?.longitude,
        address: detail.location?.address,
        unlock_conditions_type: detail.unlock_conditions?.type,
        unlock_conditions_password: detail.unlock_conditions?.password || '',
        unlock_conditions_radius: detail.unlock_conditions?.radius || 50,
        unlock_conditions_is_unlocked:
          detail.unlock_conditions?.is_unlocked || false,
        unlock_conditions_unlockable_time:
          detail.unlock_conditions?.unlockable_time || null,
        // stats
        view_count: detail.stats?.view_count || 0,
        like_count: detail.stats?.like_count || 0,
        comment_count: detail.stats?.comment_count || 0,
        unlock_count: detail.stats?.unlock_count || 0,
        is_liked: detail.stats?.is_liked ?? false,
        is_collected: detail.stats?.is_collected ?? false,
        // media
        media_files: detail.media_files || [],
        // creator
        is_mine: detail.creator?.user_id === userStore.userInfo.user_id,
        creator: detail.creator || {},
      }
      console.log('mapview查看胶囊详情:', currentDetailData.value)
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

/**
 * 实际执行解锁API请求的函数，处理地理位置获取逻辑 (从 MyCapsuleView.vue 复制并调整 MapView 的位置参数)
 * @param {string} capsuleId
 * @param {string | null} password
 * @returns {Promise<Object>} API response
 */
const doUnlockRequest = (capsuleId, password = null) => {
  return new Promise((resolve, reject) => {
    // MapView 应该始终有 userLocation，但为了兼容 MyCapsuleView 的复杂逻辑，我们保持地理位置的优先获取。
    const capsule = currentUnlockCapsule.value || {}
    // 从 currentUnlockCapsule 中获取 radius，它在 startUnlockProcess 中被设置
    const requiredRadius = capsule.unlock_conditions_radius || 0

    // 1. 如果需要地理位置，尝试获取最新位置 (MapContainer 应该已经提供了 userLocation)
    if (requiredRadius > 0 && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const apiParams = {
            capsule_id: capsuleId,
            password: password || undefined,
            user_location: {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
            },
          }
          unlockCapsule(apiParams).then(resolve).catch(reject)
        },
        (posError) => {
          // 如果获取位置失败，检查是否是位置条件触发的胶囊
          const errorMsg = posError.message || '无法获取您的地理位置信息。'
          if (requiredRadius > 0) {
            reject(new Error(`地点解锁失败: ${errorMsg}。请检查定位权限。`))
          } else {
            // 非地点解锁，继续尝试请求（使用 MapView 存储的位置）
            const apiParams = {
              capsule_id: capsuleId,
              password: password || undefined,
              user_location: userLocation.value, // 使用 MapView 存储的位置
            }
            unlockCapsule(apiParams).then(resolve).catch(reject)
          }
        },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
      )
    } else {
      // 2. 如果不需要地理位置或浏览器不支持（使用 MapView 存储的位置）
      const apiParams = {
        capsule_id: capsuleId,
        password: password || undefined,
        user_location: userLocation.value, // 使用 MapView 存储的位置
      }
      unlockCapsule(apiParams).then(resolve).catch(reject)
    }
  })
}

/**
 * 核心解锁流程 (从 MyCapsuleView.vue 复制)
 * @param {string} capsuleId
 * @param {string | null} password
 */
const startUnlockProcess = async (capsuleId, password = null) => {
  const loadingKey = `unlock_${capsuleId}`
  isProcessing.value[loadingKey] = true
  try {
    // 1. 获取胶囊详情（确保我们有最新的 creator_id 和 unlock_conditions）
    const detail = await getCapsuleDetail(capsuleId)
    // 检查是否已经解锁
    const isMine = detail.creator?.user_id === userStore.user_id

    // 2. 根据解锁类型执行前置检查 (如果需要密码但没传，则弹出 Modal)
    if (detail.unlock_conditions?.type === 'password' && !password) {
      currentUnlockCapsule.value = {
        // 只保留核心信息用于 Modal 显示
        id: detail.id,
        title: detail.title || '未命名胶囊',
        unlock_conditions_type: detail.unlock_conditions.type,
      }
      showUnlockModal.value = true
      unlockPasswordInput.value = '' // 清空输入
      isProcessing.value[loadingKey] = false // 此时应暂时解除 loading
      return // 等待用户输入密码后再次调用
    }

    // 3. 执行解锁请求 (包括位置/密码校验)
    // 提前设置 currentUnlockCapsule 用于 doUnlockRequest 获取 radius
    currentUnlockCapsule.value = {
      id: detail.id,
      title: detail.title || '未命名胶囊',
      unlock_conditions_type: detail.unlock_conditions?.type,
      unlock_conditions_radius: detail.unlock_conditions?.radius || 0,
    }
    const result = await doUnlockRequest(capsuleId, password)

    alert('解锁成功！')
    // 成功后：刷新数据并关闭弹窗
    showUnlockModal.value = false
    unlockPasswordInput.value = ''
    await fetchCapsules() // 刷新地图数据
  } catch (error) {
    console.error(`解锁胶囊(${capsuleId})失败：`, error)
    alert(`解锁失败：${error.message || '请稍后重试'}`)
  } finally {
    isProcessing.value[loadingKey] = false
  }
}

/**
 * 触发解锁流程 (MapContainer/列表点击) (从 MyCapsuleView.vue 复制并调整参数)
 * @param {string} capsuleId
 */
const handleUnlockCapsule = (capsuleId) => {
  // 从 MapView.vue 的 capsules 列表中查找胶囊，获取必要信息
  const capsule = capsules.value.find((c) => c.id === capsuleId)
  if (!capsule) {
    alert('未能找到该胶囊信息，无法解锁。')
    return
  }

  // 设置 currentUnlockCapsule 用于弹窗和 doUnlockRequest 内部使用
  currentUnlockCapsule.value = {
    id: capsule.id,
    title: capsule.title || '未命名胶囊',
    unlock_conditions_type: capsule.unlock_conditions_type || 'any',
    unlock_conditions_radius: capsule.unlock_conditions_radius || 0,
  }

  // 如果是密码类型，弹出解锁 Modal
  if (capsule.unlock_conditions_type === 'password') {
    showUnlockModal.value = true
    unlockPasswordInput.value = ''
  } else {
    // 其他类型（location/any），直接尝试解锁
    startUnlockProcess(capsuleId)
  }
}

// —— 处理解锁弹窗确认按钮 —— (从 MyCapsuleView.vue 复制)
const handleConfirmUnlock = () => {
  const capsule = currentUnlockCapsule.value
  if (!capsule) return
  // 传入用户输入的密码
  startUnlockProcess(capsule.id, unlockPasswordInput.value)
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
// 应用筛选并刷新数据
const applyFilters = () => {
  fetchCapsules()
}

// 重置筛选条件
const resetFilters = () => {
  filters.value = {
    keyword: '',
    startTime: '',
    endTime: '',
    visibility: 'all',
    unlockType: 'all',
  }
  fetchCapsules()
}
// #endregion

// #region 辅助函数
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

/**
 * 关闭详情模态框并清空数据
 */
const handleCloseDetail = () => {
  showDetailModal.value = false
  currentDetailData.value = {}
}

// #endregion

// #region 顶部导航处理函数
const handleGoHub = () => {
  routeJump('/hubviews')
}
const handleSearch = (keyword) => {}

const handleHeaderAction = (actionKey) => {
  if (actionKey === 'create') {
    currentEditData.value = null
    isEditMode.value = true
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

// #endregion

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

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: var(--radius-sm);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px var(--accent-light);
}

.filter-group {
  margin-bottom: 24px; /* 稍微加大间距 */
}

.filter-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: var(--radius-sm);
  font-size: 13px;
  background-color: #fff;
  color: #334155;
  margin-top: 4px;
}

.filter-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-light);
  outline: none;
}

.date-range-inputs {
  display: flex;
  align-items: center;
  gap: 5px;
}

.date-input {
  flex: 1;
  padding: 8px;
  font-size: 11px;
}

.date-sep {
  font-size: 12px;
  color: var(--muted);
}

.filter-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 25px;
}

.apply-btn {
  height: 40px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.reset-btn {
  background: transparent;
  color: var(--muted);
}



</style>
