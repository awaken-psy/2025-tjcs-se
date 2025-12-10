<template>
  <div class="my-capsule-page">
    <AppHeader
      page-title="我的胶囊"
      page-subtitle="管理你创建的时光胶囊，支持编辑、删除和分享"
      :show-search="true"
      search-placeholder="搜索胶囊标题/标签/描述..."
      :actions="[
        { key: 'create', text: '创建胶囊', icon: '✚', type: 'primary' },
        { key: 'export', text: '导出数据', icon: '📤', type: 'ghost' },
        { key: 'setting', text: '隐私设置', icon: '⚙️', type: 'ghost' },
      ]"
      @go-hub="handleGoHub"
      @search="handleHeaderSearch"
      @action-click="handleHeaderAction" />

    <div class="my-capsule-main">
      <Sidebar
        :nav-items="[
          {
            key: 'myCapsule',
            label: '我的胶囊',
            icon: '👤',
            badge: { count: capsuleTotal, color: '#6c8cff' },
          },
          { key: 'hub', label: '中枢', icon: '🏠' },
          { key: 'map', label: '地图', icon: '🗺️' },
          { key: 'create', label: '创建胶囊', icon: '✚' },
          { key: 'timeline', label: '时间轴', icon: '📅' },
          { key: 'events', label: '校园活动', icon: '🎪' },
          { key: 'logout', label: '注销', icon: '🔐' },
        ]"
        current-active="myCapsule"
        tip-text="提示：点击胶囊卡片可查看详情，支持网格/列表视图切换"
        @nav-change="handleNavChange" />

      <div class="capsule-management">
        <CapsuleFilterBar
          :current-vis="filter.vis"
          :current-sort="filter.sort"
          :current-view-mode="viewMode"
          :show-visibility-filter="true"
          :show-search="false"
          :show-reset-btn="true"
          search-placeholder="搜索胶囊标题/标签..."
          @filter-change="handleFilterChange"
          @sort-change="handleSortChange"
          @view-mode-change="handleViewModeChange"
          @reset-filter="handleResetFilter" />

        <div
          class="capsule-list"
          :class="viewMode === 'grid' ? 'grid-view' : 'list-view'">
          <CapsuleCard
            v-for="capsule in filteredCapsules"
            :key="capsule.id"
            :capsule="capsule"
            :view-mode="viewMode"
            @view="handleViewCapsule(capsule.id)"
            @like="handleLikeCapsule(capsule.id)"
            @click="handleCardClick(capsule.id)">
            <template #actions>
              <CapsuleActionButtons
                :capsule="capsule"
                :is-owner="capsule.is_mine"
                :view-mode="viewMode"
                :is-processing="{
                  view: isProcessing[`view_${capsule.id}`],
                  edit: isProcessing[`edit_${capsule.id}`],
                  delete: isProcessing[`delete_${capsule.id}`],
                  like: isProcessing[`like_${capsule.id}`],
                }"
                @view="handleViewCapsule(capsule.id)"
                @like="handleLikeCapsule(capsule.id)"
                @edit="handleEditCapsule(capsule.id)"
                @delete="handleDeleteCapsule(capsule.id)"
                @share="handleShareCapsule(capsule)"
                @collect="handleCollectCapsule(capsule.id)" />
            </template>
          </CapsuleCard>

          <div v-if="filteredCapsules.length === 0" class="empty-state">
            <i class="fas fa-box-open empty-icon" />
            <h4 class="empty-title">暂无胶囊</h4>
            <p class="empty-desc">点击"创建胶囊"开始记录你的校园回忆吧～</p>
            <button class="btn primary" @click="handleOpenCreateForm">
              <i class="fas fa-plus" /> 创建第一个胶囊
            </button>
          </div>
        </div>

        <div v-if="capsuleTotal > 0" class="pagination">
          <button
            class="page-btn"
            :disabled="currentPage === 1 || isLoading"
            @click="handlePageChange(currentPage - 1)">
            上一页
          </button>
          <span class="page-info">
            第 **{{ currentPage }}** 页 / 共 **{{
              Math.ceil(capsuleTotal / pageSize)
            }}** 页（共 **{{ capsuleTotal }}** 个胶囊）
          </span>
          <button
            class="page-btn"
            :disabled="
              currentPage >= Math.ceil(capsuleTotal / pageSize) || isLoading
            "
            @click="handlePageChange(currentPage + 1)">
            下一页
          </button>
        </div>
      </div>
    </div>

    <CapsuleForm
      :is-show="showFormModal"
      :is-edit="isEditMode"
      :edit-data="currentEditData"
      @close="handleCloseForm"
      @submit="onCapsuleCreated" />

    <div class="capsule-detail-modal" :class="{ active: showDetailModal }">
      <div class="modal-overlay" @click="handleCloseDetail" />
      <div class="modal-panel">
        <div class="modal-header">
          <h3 class="modal-title">
            {{ currentDetailData.title }}
          </h3>
          <button class="modal-close" @click="handleCloseDetail">✕</button>
        </div>
        <div class="modal-body">
          <div class="detail-meta">
            <span v-if="currentDetailData.time" class="meta-item"
              ><i class="fas fa-clock" /> **投递时间：**
              {{ formatStandard(currentDetailData.time) }}</span
            >
            <span v-if="currentDetailData.vis" class="meta-item"
              ><i class="fas fa-eye" /> **可见性：**
              {{ getVisText(currentDetailData.vis) }}</span
            >
            <span class="meta-item"
              ><i :class="getUnlockIcon(currentDetailData.unlockType)" />
              **解锁条件：**
              {{
                getUnlockText(
                  currentDetailData.unlockType,
                  currentDetailData.unlockValue
                )
              }}</span
            >
            <span class="meta-item"
              ><i class="fas fa-map-marker-alt" /> **投递位置：**
              {{ currentDetailData.location || '未知位置' }}</span
            >
          </div>

          <div
            v-if="
              currentDetailData.media_files &&
              currentDetailData.media_files.length > 0
            "
            class="detail-media-preview">
            <img
              :src="currentDetailData.media_files[0].url"
              alt="胶囊媒体预览"
              class="detail-img-preview"
              @click="handleOpenMediaViewer(currentDetailData.media_files)" />
            <div
              v-if="currentDetailData.media_files.length > 1"
              class="media-count">
              <i class="fas fa-images" /> +{{
                currentDetailData.media_files.length - 1
              }}
            </div>
            <div class="media-tip">**点击图片查看所有媒体文件**</div>
          </div>

          <div class="detail-desc">
            **内容描述：**
            {{ currentDetailData.desc || '无内容描述' }}
          </div>

          <div
            v-if="currentDetailData.tags && currentDetailData.tags.length > 0"
            class="detail-tags">
            <span
              v-for="(tag, idx) in currentDetailData.tags"
              :key="idx"
              class="tag-item">
              # {{ tag }}
            </span>
          </div>

          <div class="detail-stats">
            <span class="stat-item"
              ><i
                class="fas fa-heart"
                :class="{ liked: currentDetailData.liked }" />
              {{ currentDetailData.likes || 0 }} 点赞</span
            >
            <span class="stat-item"
              ><i class="fas fa-eye" />
              {{ currentDetailData.views || 0 }} 浏览</span
            >
            <span class="stat-item"
              ><i
                class="fas fa-bookmark"
                :class="{ collected: currentDetailData.collected }" />
              {{ currentDetailData.collected ? '已收藏' : '未收藏' }}</span
            >
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn ghost" @click="handleCloseDetail">关闭</button>
          <button
            class="btn primary"
            v-if="currentDetailData.is_mine"
            @click="handleEditCapsule(currentDetailData.id)">
            编辑胶囊
          </button>
          <button
            class="btn ghost"
            @click="handleShareCapsule(currentDetailData)">
            <i class="fas fa-share-alt" /> 分享
          </button>
        </div>
      </div>
    </div>

    <GenericModal
      :is-show="showExportModal"
      title="导出我的胶囊数据"
      width="650px"
      @close="showExportModal = false">
      <template #default>
        <div class="export-form-content">
          <p class="export-tip">
            选择你希望导出的数据格式和内容范围。系统将打包并准备下载链接。
          </p>

          <div class="form-group">
            <label for="export-format">📥 导出格式：</label>
            <select
              id="export-format"
              v-model="exportData.format"
              :disabled="isExporting">
              <option value="json">JSON (包含所有元数据和文本)</option>
              <option value="zip">ZIP (包含 JSON、CSV 和所有媒体文件)</option>
            </select>
          </div>

          <div class="form-group media-checkbox-group">
            <label>📸 包含媒体文件：</label>
            <input
              type="checkbox"
              id="include-media"
              v-model="exportData.includeMedia"
              :disabled="isExporting" />
            <label for="include-media" class="checkbox-label">
              包含图片、视频等原始文件。
              <span v-if="exportData.format === 'json'" class="note"
                >(JSON 格式只包含媒体链接)</span
              >
            </label>
          </div>

          <div class="form-group time-range-group">
            <label for="export-time-range">📅 时间范围：</label>
            <select
              id="export-time-range"
              v-model="exportData.timeRange"
              :disabled="isExporting">
              <option value="all">所有胶囊</option>
              <option value="lastYear">过去一年</option>
              <option value="custom">自定义范围</option>
            </select>
          </div>

          <div
            v-if="exportData.timeRange === 'custom'"
            class="form-group date-input-group">
            <label>从：</label>
            <input
              type="date"
              v-model="exportData.startDate"
              :disabled="isExporting"
              :max="new Date().toISOString().split('T')[0]" />
            <label>到：</label>
            <input
              type="date"
              v-model="exportData.endDate"
              :disabled="isExporting"
              :max="new Date().toISOString().split('T')[0]" />
          </div>
        </div>
      </template>
      <template #actions>
        <div v-if="isExporting" class="export-loading-status">
          <i class="fas fa-spinner fa-spin"></i> 正在准备导出文件...
        </div>
        <button
          class="btn ghost"
          :disabled="isExporting"
          @click="showExportModal = false">
          取消
        </button>
        <button
          class="btn primary"
          :disabled="isExporting"
          @click="handleExportData">
          <i v-if="!isExporting" class="fas fa-download"></i>
          <span v-else>处理中...</span>
          开始导出
        </button>
      </template>
    </GenericModal>

    <GenericModal
      :is-show="showSettingModal"
      title="全局隐私设置"
      width="600px"
      @close="showSettingModal = false">
      <template #default>
        <div v-if="isSavingSettings" class="loading-state-overlay">
          <i class="fas fa-spinner fa-spin loading-icon"></i>
          <p>正在加载您的设置...</p>
        </div>

        <div v-else class="setting-form-content">
          <p class="setting-tip">
            ⚙️
            这些设置将作为您未来创建新胶囊时的**默认值**，不会影响已发布的胶囊。
          </p>

          <div class="form-group setting-group">
            <label for="default-vis">默认胶囊可见性：</label>
            <select
              id="default-vis"
              v-model="privacySettings.defaultVisibility">
              <option value="public">校园公开 (所有人可见)</option>
              <option value="friend">好友可见 (仅互相关注者可见)</option>
              <option value="private">仅自己可见 (最高隐私)</option>
            </select>
            <span class="setting-desc"> 新胶囊创建时的初始可见性选项。 </span>
          </div>

          <hr class="setting-divider" />

          <div class="form-group setting-group checkbox-switch-group">
            <label>投递时记录地理位置：</label>
            <label class="switch">
              <input
                type="checkbox"
                v-model="privacySettings.allowLocationTracking" />
              <span class="slider round"></span>
            </label>
            <span class="setting-desc">
              关闭后，创建胶囊时将不会保存您的 GPS 位置信息。
            </span>
          </div>

          <div class="form-group setting-group checkbox-switch-group">
            <label>评论互动时默认匿名：</label>
            <label class="switch">
              <input type="checkbox" v-model="privacySettings.enableAnonMode" />
              <span class="slider round"></span>
            </label>
            <span class="setting-desc">
              开启后，您在公共胶囊下的评论和互动将默认以匿名身份显示。
            </span>
          </div>

          <hr class="setting-divider" />

          <div class="form-group setting-group">
            <label for="auto-delete">媒体文件自动删除：</label>
            <select
              id="auto-delete"
              v-model="privacySettings.autoDeleteMediaAfterDays">
              <option :value="0">永不删除</option>
              <option :value="365">1 年后自动删除</option>
              <option :value="90">90 天后自动删除</option>
              <option :value="30">30 天后自动删除</option>
            </select>
            <span class="setting-desc">
              已上传的媒体文件（图片/视频）在多少天后自动从服务器删除，以释放存储空间。
            </span>
          </div>
        </div>
      </template>
      <template #actions>
        <button
          class="btn ghost"
          :disabled="isSavingSettings"
          @click="showSettingModal = false">
          取消
        </button>
        <button
          class="btn primary"
          :disabled="isSavingSettings"
          @click="handleSavePrivacySettings">
          <i v-if="isSavingSettings" class="fas fa-spinner fa-spin"></i>
          <i v-else class="fas fa-save"></i>
          {{ isSavingSettings ? '保存中...' : '保存设置' }}
        </button>
      </template>
    </GenericModal>

    <GenericModal
      :is-show="showMediaViewerModal"
      :title="`媒体文件查看 (${currentMediaIndex + 1} / ${
        currentMediaFiles.length
      })`"
      width="90vw"
      @close="handleCloseMediaViewer">
      <template #default>
        <div class="media-viewer-content">
          <div v-if="!currentMedia" class="media-loading-state">
            <i class="fas fa-exclamation-triangle"></i>
            暂无媒体文件或文件加载失败。
          </div>

          <div v-else class="media-display-area">
            <img
              v-if="
                currentMedia.fileMimeType &&
                currentMedia.fileMimeType.startsWith('image/')
              "
              :src="currentMedia.url"
              alt="胶囊图片"
              class="media-content image-viewer" />
            <video
              v-else-if="
                currentMedia.fileMimeType &&
                currentMedia.fileMimeType.startsWith('video/')
              "
              :src="currentMedia.url"
              controls
              class="media-content video-viewer">
              您的浏览器不支持视频播放。
            </video>
            <div v-else class="media-content file-viewer">
              <i class="fas fa-file-alt file-icon"></i>
              <p>不支持在线预览的文件类型：{{ currentMedia.fileMimeType }}</p>
              <a
                :href="currentMedia.url"
                target="_blank"
                class="btn primary btn-sm"
                >下载文件</a
              >
            </div>

            <div v-if="hasMultipleMedia" class="media-navigation">
              <button
                class="nav-btn prev-btn"
                @click="handlePrevMedia"
                aria-label="上一个媒体">
                <i class="fas fa-chevron-left"></i>
              </button>
              <button
                class="nav-btn next-btn"
                @click="handleNextMedia"
                aria-label="下一个媒体">
                <i class="fas fa-chevron-right"></i>
              </button>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="media-file-info">
          <span v-if="currentMedia && currentMedia.fileName"
            >文件名：{{ currentMedia.fileName }}</span
          >
          <span v-else>文件信息：未知</span>
        </div>
        <button class="btn primary" @click="handleCloseMediaViewer">
          确定
        </button>
      </template>
    </GenericModal>
  </div>
</template>

<script setup>
import { formatStandard } from '@/utils/formatTime.js'
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
// 假设这些组件存在，如果不存在，需要创建它们。
import AppHeader from '@/components/AppHeader.vue'
import CapsuleActionButtons from '@/components/CapsuleActionButtons.vue'
import CapsuleCard from '@/components/CapsuleCard.vue'
import CapsuleFilterBar from '@/components/CapsuleFilterBar.vue'
import CapsuleForm from '@/components/CapsuleForm.vue'
import Sidebar from '@/components/Sidebar.vue'
// 假设新增一个通用弹窗组件，用于设置/导出/媒体查看
import GenericModal from '@/components/GenericModal.vue'

// 引入API
import {
  deleteCapsule,
  getMyCapsules,
  updateCapsule,
  getCapsuleDetail,
  likeCapsule,
} from '@/api/new/capsulesApi.js'

const router = useRouter()

// 胶囊数据
const capsuleList = ref([])
const capsuleTotal = ref(0)

// 筛选条件
const filter = ref({
  vis: 'public',
  sort: 'newest',
  search: '',
})

// 视图与分页
const viewMode = ref('grid')
const currentPage = ref(1)
const pageSize = ref(10)

// 弹窗状态 (新增导出、设置、媒体查看)
const showFormModal = ref(false)
const isEditMode = ref(false)
const currentEditData = ref({})
const showDetailModal = ref(false)
const currentDetailData = ref({})

// 加载状态
const isLoading = ref(false)
const isProcessing = ref({})

// 新增：导出数据状态
const showExportModal = ref(false)
const isExporting = ref(false)
const exportData = ref({
  format: 'json', // 默认 JSON
  timeRange: 'all', // 默认全部
  startDate: '',
  endDate: '',
  includeMedia: true, // 默认包含媒体文件
})

// 新增：隐私设置状态
const showSettingModal = ref(false)
const isSavingSettings = ref(false)
const privacySettings = ref({
  defaultVisibility: 'friend', // 新创建胶囊的默认可见性: public, friend, private
  allowLocationTracking: true, // 是否允许记录投递时的地理位置
  enableAnonMode: false, // 是否在评论和互动时默认匿名
  autoDeleteMediaAfterDays: 0, // 媒体文件自动删除天数 (0 代表永不删除)
})

// 媒体文件查看器状态 (已在第一轮修改中添加，这里是确认和增强)
const showMediaViewerModal = ref(false) // 新增：媒体查看器弹窗
const currentMediaFiles = ref([]) // 媒体文件列表
const currentMediaIndex = ref(0) // 当前正在查看的媒体索引

/**
 * 计算属性：筛选后的胶囊列表 (逻辑不变)
 */
const filteredCapsules = computed(() => {
  const list = Array.isArray(capsuleList.value) ? capsuleList.value : []
  if (list.length === 0) return []

  let result = [...list]

  // 1. 可见性筛选
  if (filter.value.vis !== 'public') {
    result = result.filter((c) => c.vis === filter.value.vis)
  }

  // 2. 搜索筛选（顶部导航搜索）
  if (filter.value.search) {
    const keyword = filter.value.search.toLowerCase()
    result = result.filter((c) => {
      const searchStr = `${c.title}${c.desc}${(c.tags || []).join(
        ''
      )}`.toLowerCase()
      return searchStr.includes(keyword)
    })
  }

  // 3. 排序
  switch (filter.value.sort) {
    case 'oldest':
      result.sort((a, b) => new Date(a.time) - new Date(b.time))
      break
    case 'popular':
      result.sort((a, b) => (b.likes || 0) - (a.likes || 0))
      break
    case 'newest':
    default:
      result.sort((a, b) => new Date(b.time) - new Date(a.time))
      break
  }

  return result
})

/**
 * 页面初始化：加载我的胶囊列表
 */
onMounted(async () => {
  await fetchCapsuleList()
})

// 核心方法：加载我的胶囊列表（调用API）
const fetchCapsuleList = async () => {
  console.log('加载我的胶囊列表，当前筛选条件：', filter.value)
  isLoading.value = true
  try {
    const res = await getMyCapsules({
      page: currentPage.value,
      size: pageSize.value,
      status: 'all',
    })

    if (res && Array.isArray(res.capsules)) {
      // 数据映射：假设 API 返回了 is_liked 和 is_collected 字段
      capsuleList.value = res.capsules.map((capsule) => ({
        ...capsule,
        is_mine: true, // 假设 getMyCapsules 返回的都是自己的
        liked: capsule.is_liked ?? false, // 使用 API 返回值，否则初始化为 false
        collected: capsule.is_collected ?? false, // 使用 API 返回值，否则初始化为 false
      }))
      capsuleTotal.value = res.pagination?.total ?? res.capsules.length
    } else {
      capsuleList.value = []
      capsuleTotal.value = 0
    }
  } catch (error) {
    console.error('获取胶囊列表失败:', error)
    capsuleList.value = []
    capsuleTotal.value = 0
  } finally {
    isLoading.value = false
  }
}

// 辅助函数：获取可见性文本
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

// 辅助函数：获取解锁条件文本 (UI 增强)
const getUnlockText = (type, value) => {
  if (!type) return '无特殊条件，立即可见'

  switch (type) {
    case 'time':
      return `时间触发（${formatStandard(value)}后解锁）`
    case 'event':
      const eventMap = {
        graduation: '毕业典礼',
        freshman: '新生入学',
        anniversary: '校庆',
      }
      return `事件触发（${eventMap[value] || value}时解锁）`
    case 'location':
      return '地点触发（靠近指定位置5米内解锁）'
    default:
      return '未知触发条件'
  }
}

// 辅助函数：获取解锁条件的 Icon (UI 增强)
const getUnlockIcon = (type) => {
  switch (type) {
    case 'time':
      return 'fas fa-hourglass-half'
    case 'event':
      return 'fas fa-calendar-alt'
    case 'location':
      return 'fas fa-crosshairs'
    default:
      return 'fas fa-unlock'
  }
}

// —— 顶部导航相关方法 ——
const handleGoHub = () => {
  router.push('/hubviews')
}

const handleHeaderSearch = (keyword) => {
  filter.value.search = keyword
}

// 变更：控制新增的导出和设置弹窗
const handleHeaderAction = (key) => {
  switch (key) {
    case 'create':
      handleOpenCreateForm()
      break
    case 'export':
      showExportModal.value = true
      break // 控制导出弹窗
    case 'setting':
      showSettingModal.value = true
      break // 控制设置弹窗
  }
}

// —— 侧边导航相关方法 ——
const handleNavChange = (key) => {
  const routeMap = {
    myCapsule: '/my-capsule',
    hub: '/hubviews',
    map: '/map',
    create: '/capsules',
    timeline: '/timeline',
    events: '/events',
    logout: '/logout',
  }

  if (key === 'create') {
    handleOpenCreateForm()
    return
  }

  if (key === 'logout') {
    localStorage.removeItem('user_token')
    localStorage.removeItem('user_info')
    router.push('/login')
    return
  }

  router.push(routeMap[key] || '/my-capsule')
}

// —— 共用组件 CapsuleFilterBar 事件处理 ——
const handleFilterChange = async (params) => {
  if (params.type === 'vis') {
    filter.value.vis = params.value
    currentPage.value = 1
    await fetchCapsuleList()
  }
}

const handleSortChange = (sortType) => {
  filter.value.sort = sortType
}

const handleViewModeChange = (mode) => {
  viewMode.value = mode
}

const handleResetFilter = async () => {
  filter.value = { vis: 'public', sort: 'newest', search: '' }
  currentPage.value = 1
  await fetchCapsuleList()
}

// —— 分页相关方法 ——
const handlePageChange = async (page) => {
  currentPage.value = page
  await fetchCapsuleList()
}

// —— 胶囊操作相关方法 ——

const handleViewCapsule = async (capsuleId) => {
  isProcessing.value[`view_${capsuleId}`] = true
  try {
    const detail = await getCapsuleDetail(capsuleId)
    if (detail) {
      currentDetailData.value = {
        ...detail,
        is_mine: true, // 假设详情页也知道是否是自己的
        // 字段映射和增强
        unlockType: detail.unlock_conditions?.type,
        unlockValue: detail.unlock_conditions?.value,
        location: detail.location?.address,
        media_files: detail.media_files || [], // 确保是数组
        likes: detail.like_count,
        views: detail.view_count,
        liked: detail.is_liked ?? false, // 假设详情 API 也返回点赞状态
        collected: detail.is_collected ?? false, // 假设详情 API 也返回收藏状态
      }
      showDetailModal.value = true
    } else {
      alert('获取胶囊详情失败')
    }
  } catch (error) {
    console.error(`获取胶囊详情(${capsuleId})失败：`, error)
    alert('加载详情失败，请稍后重试')
  } finally {
    isProcessing.value[`view_${capsuleId}`] = false
  }
}

const handleCardClick = (capsuleId) => {
  handleViewCapsule(capsuleId)
}

const handleLikeCapsule = async (capsuleId) => {
  const capsule = capsuleList.value.find((c) => c.id === capsuleId)
  if (!capsule) return

  isProcessing.value[`like_${capsuleId}`] = true
  try {
    const result = await likeCapsule(capsuleId)

    if (result.code === 200 || result.success) {
      const isLiked = result.data?.is_liked ?? !capsule.liked
      const newCount =
        result.data?.like_count ??
        (capsule.like_count || 0) + (isLiked ? 1 : -1)

      // 乐观更新
      capsule.liked = isLiked
      capsule.like_count = newCount

      // 刷新列表
      await fetchCapsuleList()
    } else {
      alert(`点赞操作失败：${result.message || '未知错误'}`)
    }
  } catch (error) {
    console.error(`点赞胶囊(${capsuleId})失败：`, error)
    alert('点赞失败，请稍后重试')
  } finally {
    isProcessing.value[`like_${capsuleId}`] = false
  }
}

// 优化：移除打开编辑表单时的 fetchCapsuleList 调用
const handleEditCapsule = (capsuleId) => {
  const capsule = capsuleList.value.find((c) => c.id === capsuleId)

  if (capsule) {
    // 1. 设置编辑数据，并进行字段映射 (假设 API 的 desc 对应表单的 content)
    currentEditData.value = {
      ...capsule,
      content: capsule.desc,
    }

    // 2. 切换到编辑模式并打开表单
    isEditMode.value = true
    showFormModal.value = true

    // 3. 关闭详情弹窗
    handleCloseDetail()
  }
}

const handleDeleteCapsule = async (capsuleId) => {
  if (!confirm('确定要删除该胶囊吗？此操作不可恢复！')) return

  isProcessing.value[`delete_${capsuleId}`] = true
  try {
    await deleteCapsule(capsuleId)

    alert('删除成功！')

    handleCloseDetail()

    // 本地移除被删除的胶囊 (乐观更新)
    capsuleList.value = capsuleList.value.filter((c) => c.id !== capsuleId)

    // 重新加载列表
    await fetchCapsuleList()
  } catch (error) {
    console.error(`删除胶囊(${capsuleId})失败：`, error)
    alert('删除失败，请稍后重试')
  } finally {
    isProcessing.value[`delete_${capsuleId}`] = false
  }
}

const handleShareCapsule = (capsule) => {
  // 变更：改为打开一个分享弹窗 (可选)
  alert(`分享胶囊：${capsule.title}（后续对接分享接口，支持复制链接/微信分享）`)
}

const handleCollectCapsule = async (capsuleId) => {
  const capsule = capsuleList.value.find((c) => c.id === capsuleId)
  if (capsule) {
    // 假设这里调用 collectCapsule API
    capsule.collected = !capsule.collected
    alert(capsule.collected ? '收藏成功' : '取消收藏成功')

    // 刷新列表
    await fetchCapsuleList()
  }
}

// —— 胶囊表单相关方法 ——
const handleOpenCreateForm = () => {
  isEditMode.value = false
  currentEditData.value = {}
  showFormModal.value = true
}

const handleCloseForm = () => {
  showFormModal.value = false
  currentEditData.value = {}
  isEditMode.value = false
}

const onCapsuleCreated = async (formData) => {
  if (!formData) {
    handleCloseForm()
    return
  }

  if (isEditMode.value) {
    const capsuleId = currentEditData.value.id
    if (!capsuleId) {
      alert('编辑失败：无法获取胶囊ID。')
      handleCloseForm()
      return
    }

    try {
      // 字段映射：content -> desc (假设 API 实际存储字段是 desc)
      const updateData = {
        title: formData.title,
        desc: formData.content, // 假设 API 期望的是 desc 字段
        visibility: formData.visibility,
        tags: formData.tags,
        // ... 其他需要更新的字段
      }

      await updateCapsule(capsuleId, updateData)
      alert('胶囊更新成功！')
    } catch (error) {
      console.error(`更新胶囊(${capsuleId})失败:`, error)
      alert(`胶囊更新失败：${error.message || '未知错误'}`)
    }
  }

  handleCloseForm() // 关闭表单
  await fetchCapsuleList() // 重新加载列表以显示更新后的数据
}

// 详情弹窗相关方法
const handleCloseDetail = () => {
  showDetailModal.value = false
  currentDetailData.value = {}
}

const handleExportData = async () => {
  if (isExporting.value) return

  // 简单验证
  if (
    exportData.value.timeRange === 'custom' &&
    (!exportData.value.startDate || !exportData.value.endDate)
  ) {
    alert('请选择有效的自定义时间范围！')
    return
  }

  // 检查 ZIP 格式和媒体文件包含
  if (exportData.value.format === 'json' && exportData.value.includeMedia) {
    if (!confirm('JSON 格式只包含媒体文件链接，不包含原始文件。确定继续吗？')) {
      return
    }
  }

  isExporting.value = true
  console.log('开始导出数据，参数：', exportData.value)

  // TODO: 对接实际的导出 API (例如：/api/v1/capsules/export)
  try {
    // 模拟 API 耗时（通常导出是后台任务）
    // 假设这里调用 API 发起导出任务
    // const result = await exportCapsuleData(exportData.value);

    await new Promise((resolve) => setTimeout(resolve, 2000))

    // 假设导出发起成功，实际项目中可能返回一个任务ID
    alert(
      `导出任务已成功发起！数据将以 ${exportData.value.format.toUpperCase()} 格式准备完成。请留意系统通知或邮件。`
    )

    // 关闭弹窗
    showExportModal.value = false
  } catch (error) {
    console.error('导出失败:', error)
    alert(`数据导出失败：${error.message || '请检查网络或联系管理员。'}`)
  } finally {
    isExporting.value = false
  }
}

// 模拟从后端加载设置的函数（实际应调用 API）
const fetchPrivacySettings = async () => {
  // TODO: 调用 getPrivacySettings API
  isSavingSettings.value = true
  try {
    await new Promise((resolve) => setTimeout(resolve, 500))
    // 模拟加载到的数据
    const loadedSettings = {
      defaultVisibility: 'public',
      allowLocationTracking: true,
      enableAnonMode: false,
      autoDeleteMediaAfterDays: 365,
    }
    privacySettings.value = loadedSettings
  } catch (error) {
    console.error('加载隐私设置失败:', error)
  } finally {
    isSavingSettings.value = false
  }
}

// 新增：顶部导航点击“设置”时加载数据
watch(showSettingModal, (newValue) => {
  if (newValue) {
    fetchPrivacySettings()
  }
})

// —— 新增：保存隐私设置逻辑 ——
const handleSavePrivacySettings = async () => {
  if (isSavingSettings.value) return

  isSavingSettings.value = true
  console.log('保存隐私设置，参数：', privacySettings.value)

  // TODO: 对接实际的保存 API (例如：/api/v1/user/settings/privacy)
  try {
    // 模拟 API 耗时
    // const result = await updatePrivacySettings(privacySettings.value);

    await new Promise((resolve) => setTimeout(resolve, 1500))

    alert('隐私设置已成功保存！')

    // 关闭弹窗
    showSettingModal.value = false
  } catch (error) {
    console.error('保存设置失败:', error)
    alert(`保存失败：${error.message || '请检查网络或联系管理员。'}`)
  } finally {
    isSavingSettings.value = false
  }
}

// 计算属性：当前正在展示的媒体文件
const currentMedia = computed(() => {
  return currentMediaFiles.value[currentMediaIndex.value] || null
})

// 计算属性：判断是否有多个媒体文件
const hasMultipleMedia = computed(() => {
  return currentMediaFiles.value.length > 1
})

// —— 媒体文件查看器逻辑 ——

// 媒体文件查看器：打开媒体查看器
const handleOpenMediaViewer = (mediaFiles) => {
  currentMediaFiles.value = mediaFiles.filter((f) => f.url) // 过滤掉没有 URL 的文件
  currentMediaIndex.value = 0 // 重置到第一个文件
  showMediaViewerModal.value = true
}

// 媒体文件查看器：关闭媒体查看器
const handleCloseMediaViewer = () => {
  showMediaViewerModal.value = false
  currentMediaFiles.value = []
  currentMediaIndex.value = 0
}

// 媒体文件查看器：切换媒体（下一个）
const handleNextMedia = () => {
  if (currentMediaFiles.value.length === 0) return
  currentMediaIndex.value =
    (currentMediaIndex.value + 1) % currentMediaFiles.value.length
}

// 媒体文件查看器：切换媒体（上一个）
const handlePrevMedia = () => {
  if (currentMediaFiles.value.length === 0) return
  currentMediaIndex.value =
    (currentMediaIndex.value - 1 + currentMediaFiles.value.length) %
    currentMediaFiles.value.length
}
</script>

<style scoped>
.my-capsule-page {
  background-color: var(--bg);
  min-height: 100vh;
}

.my-capsule-main {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 20px;
  padding: 0 20px 20px;
}

/* 胶囊管理区：容器样式 */
.capsule-management {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 胶囊列表：布局样式（网格/列表） */
.capsule-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 网格视图：复用 CapsuleCard 样式，仅补充布局 */
.grid-view {
  flex-direction: row;
  flex-wrap: wrap;
  gap: 20px;
}

.grid-view .capsule-card {
  flex: 1;
  min-width: 280px;
  max-width: calc(33.333% - 20px);
}

/* 列表视图：复用 CapsuleCard 样式，仅补充布局 */
.list-view .capsule-card {
  width: 100%;
}

/* 空状态：页面独有的空状态样式 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: var(--card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
  color: rgba(108, 140, 255, 0.3);
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #1e293b;
}

.empty-desc {
  color: var(--muted);
  margin-bottom: 16px;
}

/* 分页控件：页面独有的分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.page-btn {
  background: transparent;
  border: 1px solid rgba(108, 140, 255, 0.2);
  color: var(--accent);
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:enabled {
  background: var(--accent-light);
  border-color: var(--accent);
}

.page-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  color: var(--muted);
  border-color: rgba(12, 18, 36, 0.08);
}

.page-info {
  color: var(--muted);
  font-size: 14px;
}

/* 详情弹窗样式增强 */
.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px; /* 增大间隔 */
  font-size: 14px;
  color: var(--muted);
  border-bottom: 1px dashed rgba(12, 18, 36, 0.06);
  padding-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-media-preview {
  position: relative;
  width: 100%;
  border-radius: var(--radius-sm);
  overflow: hidden;
  cursor: pointer;
  background: #f0f0f0;
}

.detail-img-preview {
  width: 100%;
  height: 240px; /* 统一预览高度 */
  object-fit: cover;
  transition: opacity 0.3s;
}

.detail-media-preview:hover .detail-img-preview {
  opacity: 0.8;
}

.media-count {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.media-tip {
  position: absolute;
  bottom: 0;
  width: 100%;
  text-align: center;
  padding: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.3s;
}
.detail-media-preview:hover .media-tip {
  opacity: 1;
}

.detail-desc {
  line-height: 1.6;
  color: #374151;
  white-space: pre-wrap;
  margin: 0;
  border: 1px solid #e2e8f0;
  padding: 15px;
  border-radius: var(--radius-sm);
  background: #f9f9fb;
}

.detail-stats .liked {
  color: #ff4757; /* 点赞后的心形颜色 */
}
.detail-stats .collected {
  color: #ffa502; /* 收藏后的书签颜色 */
}

/* 按钮样式：仅保留页面独有的按钮样式，组件按钮样式由共用组件自带 */
.btn {
  padding: 10px 16px;
  border-radius: var(--radius-sm);
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn.primary {
  background: var(--accent);
  color: white;
}

.btn.primary:hover {
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

/* 设计令牌：统一全局样式变量 */
:root {
  --bg: #f5f8ff;
  --card: #ffffff;
  --muted: #6b7280;
  --accent: #6c8cff;
  --accent-hover: #5a7cff;
  --accent-light: rgba(108, 140, 255, 0.1);
  --shadow: 0 6px 18px rgba(12, 18, 36, 0.06);
  --shadow-lg: 0 10px 25px rgba(12, 18, 36, 0.1);
  --radius: 12px;
  --radius-sm: 8px;
}

/* 响应式适配：仅保留页面独有的响应式逻辑 */
@media (max-width: 1024px) {
  .my-capsule-main {
    grid-template-columns: 200px 1fr;
  }

  .grid-view .capsule-card {
    min-width: 240px;
    max-width: calc(50% - 20px);
  }
}

@media (max-width: 768px) {
  .my-capsule-main {
    grid-template-columns: 1fr;
  }

  .grid-view .capsule-card {
    min-width: 100%;
    max-width: 100%;
  }

  .modal-panel {
    padding: 16px;
  }
}

/* 新增：导出表单样式 */
.export-form-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.export-tip {
  font-size: 14px;
  color: var(--muted);
  padding-bottom: 10px;
  border-bottom: 1px dashed #e5e7eb;
}

.form-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.form-group label {
  font-weight: 500;
  color: #1f2937;
  flex-shrink: 0;
}

.form-group select,
.form-group input[type='date'] {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: var(--radius-sm);
  flex-grow: 1;
  min-width: 150px;
}

/* 媒体文件选择的特殊样式 */
.media-checkbox-group {
  align-items: flex-start; /* 保持多行文本对齐 */
}

.checkbox-label {
  font-weight: 400 !important;
  font-size: 14px;
  color: #4b5563;
  cursor: pointer;
  display: block; /* 允许文本换行 */
}

.checkbox-label input[type='checkbox'] {
  margin: 0;
  width: auto;
  flex-grow: 0;
}

.note {
  font-style: italic;
  color: var(--accent);
  font-size: 12px;
  display: block;
}

.time-range-group select {
  max-width: 200px;
}

.date-input-group {
  padding-left: 20px;
}

/* 导出加载状态 */
.export-loading-status {
  display: flex;
  align-items: center;
  color: var(--accent);
  margin-right: auto; /* 推开右侧按钮 */
  font-weight: 500;
  gap: 8px;
}

/* 新增：设置表单样式 */
.setting-form-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.setting-tip {
  font-size: 14px;
  color: var(--muted);
  padding-bottom: 10px;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 5px;
}

.setting-group {
  display: grid;
  grid-template-columns: 180px 1fr;
  align-items: center;
  gap: 10px 20px;
  padding: 10px 0;
  border-radius: var(--radius-sm);
}

.setting-group label:first-child {
  font-weight: 600;
  color: #1f2937;
  grid-column: 1 / 2;
}

.setting-group select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: var(--radius-sm);
  max-width: 250px;
}

.setting-desc {
  grid-column: 2 / 3;
  font-size: 13px;
  color: #6b7280;
  margin-top: -10px; /* 向上调整以适应网格布局 */
}

.setting-divider {
  border: none;
  border-top: 1px dashed #e5e7eb;
  margin: 10px 0;
}

/* 开关样式 (Switch Toggle) */
.checkbox-switch-group {
  grid-template-columns: 180px auto 1fr; /* 调整列宽 */
}

.checkbox-switch-group label:first-child {
  grid-column: 1 / 2;
}

.switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
  grid-column: 2 / 3; /* 放在第二列 */
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
}

.slider:before {
  position: absolute;
  content: '';
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.4s;
}

input:checked + .slider {
  background-color: var(--accent);
}

input:checked + .slider:before {
  transform: translateX(24px);
}

.slider.round {
  border-radius: 24px;
}

.slider.round:before {
  border-radius: 50%;
}

.checkbox-switch-group .setting-desc {
  grid-column: 3 / 4; /* 描述放在第三列 */
}

/* 加载状态覆盖 */
.loading-state-overlay {
  min-height: 200px; /* 确保加载状态下弹窗不会太小 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: var(--accent);
  gap: 10px;
  font-size: 16px;
  font-weight: 500;
}
.loading-icon {
  font-size: 24px;
}

/* 新增：媒体查看器样式 */
.generic-modal-wrapper :deep(.modal-panel) {
  max-width: 90vw;
  width: 90vw;
  height: 90vh; /* 媒体查看器使用固定高宽 */
}

.media-viewer-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

.media-display-area {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #000; /* 深色背景看媒体文件效果更好 */
  flex-grow: 1;
  overflow: hidden;
}

.media-content {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain; /* 确保图片或视频完整显示，而不是裁剪 */
}

.file-viewer {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 15px;
  color: white;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg);
  max-width: 300px;
  text-align: center;
}

.file-icon {
  font-size: 3rem;
  color: var(--accent);
}

.media-loading-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  flex-grow: 1;
  color: #999;
  font-size: 16px;
}

/* 媒体导航按钮 */
.media-navigation {
  position: absolute;
  top: 50%;
  width: 100%;
  display: flex;
  justify-content: space-between;
  transform: translateY(-50%);
  pointer-events: none; /* 允许点击穿透到媒体文件 */
}

.nav-btn {
  background: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  cursor: pointer;
  transition: background 0.2s;
  margin: 0 10px;
  pointer-events: auto; /* 恢复按钮的点击事件 */
}

.nav-btn:hover {
  background: rgba(0, 0, 0, 0.8);
}

.media-file-info {
  margin-right: auto;
  font-size: 14px;
  color: var(--muted);
}
</style>
