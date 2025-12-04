<template>
  <!-- 我的胶囊页：管理用户创建的所有胶囊，整合共用组件减少重复代码 -->
  <div class="my-capsule-page">
    <!-- 顶部导航（复用共用组件） -->
    <AppHeader
      page-title="我的胶囊"
      page-subtitle="管理你创建的时光胶囊，支持编辑、删除和分享"
      :show-search="true"
      search-placeholder="搜索胶囊标题/标签/描述..."
      :actions="[
        { key: 'create', text: '创建胶囊', icon: '✚', type: 'primary' },
        { key: 'export', text: '导出数据', icon: '📤', type: 'ghost' },
        { key: 'setting', text: '隐私设置', icon: '⚙️', type: 'ghost' }
      ]"
      @go-hub="handleGoHub"
      @search="handleHeaderSearch"
      @action-click="handleHeaderAction"
    />

    <!-- 主体内容：侧边导航 + 胶囊管理区 -->
    <div class="my-capsule-main">
      <!-- 侧边导航（复用共用组件） -->
      <Sidebar
        :nav-items="[
          { key: 'myCapsule', label: '我的胶囊', icon: '👤', badge: { count: capsuleTotal, color: '#6c8cff' } },
          { key: 'hub', label: '中枢', icon: '🏠' },
          { key: 'map', label: '地图', icon: '🗺️' },
          { key: 'create', label: '创建胶囊', icon: '✚' },
          { key: 'timeline', label: '时间轴', icon: '📅' },
          { key: 'events', label: '校园活动', icon: '🎪' },
          { key: 'logout', label: '注销', icon: '🔐' }
        ]"
        current-active="myCapsule"
        tip-text="提示：点击胶囊卡片可查看详情，支持网格/列表视图切换"
        @nav-change="handleNavChange"
      />

      <!-- 胶囊管理区 -->
      <div class="capsule-management">
        <!-- 1. 筛选控制栏：复用共用组件 CapsuleFilterBar，替代原重复控制栏代码 -->
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
          @reset-filter="handleResetFilter"
        />

        <!-- 2. 胶囊列表：复用 CapsuleCard + 新增 CapsuleActionButtons 组件 -->
        <div 
          class="capsule-list"
          :class="viewMode === 'grid' ? 'grid-view' : 'list-view'"
        >
          <CapsuleCard
            v-for="capsule in filteredCapsules"
            :key="capsule.id"
            :capsule="capsule"
            :view-mode="viewMode"
            @view="handleViewCapsule(capsule.id)"
            @like="handleLikeCapsule(capsule.id)"
            @click="handleCardClick(capsule.id)"
          >
            <!-- 胶囊操作按钮组：复用共用组件 CapsuleActionButtons，替代原重复按钮代码 -->
            <!--TODO4:这里有个鉴权问题,不是自己的不能编辑/删除,改为了is_mine-->
            <template #actions>
              <CapsuleActionButtons
                :capsule="capsule"
                :is-owner= "capsule.is_mine"
                :view-mode="viewMode"
                :is-processing="{
                  view: isProcessing[`view_${capsule.id}`],
                  edit: isProcessing[`edit_${capsule.id}`],
                  delete: isProcessing[`delete_${capsule.id}`],
                  like: isProcessing[`like_${capsule.id}`]
                }"
                @view="handleViewCapsule(capsule.id)"
                @like="handleLikeCapsule(capsule.id)"
                @edit="handleEditCapsule(capsule.id)"
                @delete="handleDeleteCapsule(capsule.id)"
                @share="handleShareCapsule(capsule)"
                @collect="handleCollectCapsule(capsule.id)"
              />
            </template>
          </CapsuleCard>

          <!-- 空状态 -->
          <div
            v-if="filteredCapsules.length === 0"
            class="empty-state"
          >
            <i class="fas fa-box-open empty-icon" />
            <h4 class="empty-title">
              暂无胶囊
            </h4>
            <p class="empty-desc">
              点击"创建胶囊"开始记录你的校园回忆吧～
            </p>
            <button 
              class="btn primary"
              @click="handleOpenCreateForm"
            >
              <i class="fas fa-plus" /> 创建第一个胶囊
            </button>
          </div>
        </div>

        <!-- 3. 分页控件 -->
        <div
          v-if="capsuleTotal > 0"
          class="pagination"
        >
          <button 
            class="page-btn" 
            :disabled="currentPage === 1 || isLoading"
            @click="handlePageChange(currentPage - 1)"
          >
            上一页
          </button>
          <span class="page-info">
            第 {{ currentPage }} 页 / 共 {{ Math.ceil(capsuleTotal / pageSize) }} 页（共 {{ capsuleTotal }} 个胶囊）
          </span>
          <button 
            class="page-btn" 
            :disabled="currentPage >= Math.ceil(capsuleTotal / pageSize) || isLoading"
            @click="handlePageChange(currentPage + 1)"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 胶囊创建/编辑表单（复用共用组件，与中枢页使用相同的组件和逻辑） -->
    <CapsuleForm
      :is-show="showFormModal"
      :is-edit="isEditMode"
      :edit-data="currentEditData"
      @close="handleCloseForm"
      @submit="onCapsuleCreated"
    />

    <!-- 胶囊详情弹窗 -->
    <div
      class="capsule-detail-modal"
      :class="{ active: showDetailModal }"
    >
      <div
        class="modal-overlay"
        @click="handleCloseDetail"
      />
      <div class="modal-panel">
        <div class="modal-header">
          <h3 class="modal-title">
            {{ currentDetailData.title }}
          </h3>
          <button
            class="modal-close"
            @click="handleCloseDetail"
          >
            ✕
          </button>
        </div>
        <div class="modal-body">
          <div class="detail-meta">
            <span v-if="currentDetailData.time"><i class="fas fa-clock" /> {{ formatStandard(currentDetailData.time) }}</span>
            <span v-if="currentDetailData.vis"><i class="fas fa-lock" /> {{ getVisText(currentDetailData.vis) }}</span>
            <span><i class="fas fa-unlock-alt" /> {{ getUnlockText(currentDetailData.unlockType, currentDetailData.unlockValue) }}</span>
            <span><i class="fas fa-map-marker-alt" /> {{ currentDetailData.location || '未知位置' }}</span>
          </div>
          <div
            v-if="currentDetailData.img"
            class="detail-image"
          >
            <img
              :src="currentDetailData.img"
              alt="胶囊图片"
              class="detail-img"
            >
          </div>
          <div class="detail-desc">
            {{ currentDetailData.desc || '无内容描述' }}
          </div>
          <div v-if="currentDetailData.tags && currentDetailData.tags.length > 0" class="detail-tags">
            <span
              v-for="(tag, idx) in currentDetailData.tags"
              :key="idx"
              class="tag-item"
            >
              {{ tag }}
            </span>
          </div>
          <div class="detail-stats">
            <span class="stat-item"><i class="fas fa-heart" /> {{ currentDetailData.likes || 0 }} 点赞</span>
            <span class="stat-item"><i class="fas fa-eye" /> {{ currentDetailData.views || 0 }} 浏览</span>
          </div>
        </div>
        <div class="modal-actions">
          <button
            class="btn ghost"
            @click="handleCloseDetail"
          >
            关闭
          </button>
          <button 
            class="btn primary"
            @click="handleEditCapsule(currentDetailData.id)"
          >
            编辑胶囊
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatStandard } from '@/utils/formatTime.js'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
// 复用共用组件（新增2个优化组件，减少重复代码）
import AppHeader from '@/components/AppHeader.vue'
import CapsuleActionButtons from '@/components/CapsuleActionButtons.vue'; // 新增：操作按钮共用组件
import CapsuleCard from '@/components/CapsuleCard.vue'
import CapsuleFilterBar from '@/components/CapsuleFilterBar.vue'; // 新增：筛选控制共用组件
import CapsuleForm from '@/components/CapsuleForm.vue'; // 使用与中枢页相同的组件
import Sidebar from '@/components/Sidebar.vue'
// 引入API - 使用与中枢页相同的胶囊创建API
import {
  deleteCapsule,
  getMyCapsules,
  updateCapsule,
  getCapsuleDetail, 
  likeCapsule
} from '@/api/new/capsulesApi.js'

/**
 * 页面作用：
 * 1. 管理用户创建的胶囊，支持筛选（可见性）、排序（时间/点赞）、视图切换（网格/列表）
 * 2. 整合共用组件减少重复代码，使用与中枢页相同的胶囊创建组件和API调用逻辑
 * 3. 支持胶囊创建/编辑/删除、详情查看
 * 
 * 依赖组件：
 * - 基础共用组件：AppHeader、Sidebar、CapsuleCard、CapsuleForm（与中枢页相同）
 * - 新增优化组件：CapsuleFilterBar（筛选控制）、CapsuleActionButtons（操作按钮）
 * 
 * 页面状态：
 * - 胶囊数据：capsuleList（原始）、filteredCapsules（筛选后）、capsuleTotal（总数）
 * - 筛选条件：filter（可见性、排序、搜索）
 * - 视图/分页：viewMode（网格/列表）、currentPage（当前页）、pageSize（页大小）
 * - 弹窗状态：showFormModal（表单）、showDetailModal（详情）、isEditMode（编辑模式）
 * - 加载状态：isLoading（全局）、isProcessing（按钮级加载）
 */

const router = useRouter()

// 胶囊数据
const capsuleList = ref([])
const capsuleTotal = ref(0)

// 筛选条件
const filter = ref({
  vis: 'public', // 可见性：public/friend/private
  sort: 'newest', // 排序：newest/oldest/popular
  search: '' // 搜索关键词（顶部导航搜索）
})

// 视图与分页
const viewMode = ref('grid')  // 视图模式：grid/list
const currentPage = ref(1)    // 当前页码
const pageSize = ref(10)      // 每页大小，值不变

// 弹窗状态
const showFormModal = ref(false)
const isEditMode = ref(false)
const currentEditData = ref({})
const showDetailModal = ref(false)
const currentDetailData = ref({})

// 加载状态
const isLoading = ref(false)
const isProcessing = ref({}) // 按钮级加载：key=操作类型_胶囊ID，value=布尔值

/**
 * 计算属性：筛选后的胶囊列表
 */
const filteredCapsules = computed(() => {
  const list = Array.isArray(capsuleList.value) ? capsuleList.value : []
  if (list.length === 0) return []

  let result = [...list]

  // 1. 可见性筛选
  if (filter.value.vis !== 'public') {
    result = result.filter(c => c.vis === filter.value.vis)
  }

  // 2. 搜索筛选（顶部导航搜索）
  if (filter.value.search) {
    const keyword = filter.value.search.toLowerCase()
    result = result.filter(c => {
      const searchStr = `${c.title}${c.desc}${(c.tags || []).join('')}`.toLowerCase()
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
onMounted(async() => {
  await fetchCapsuleList()
})


//核心方法：加载我的胶囊列表（调用API）
// reviewed
const fetchCapsuleList = async () => {
  console.log('加载我的胶囊列表，当前筛选条件：', filter.value)
  isLoading.value = true
  try {
    const res = await getMyCapsules({
      page: currentPage.value,
      size: pageSize.value,
      status: 'published' // 假设只显示已发布的胶囊
    })

    //console.log('获取胶囊列表接口返回数据：', res)
    //NOTE:分页模型中，后端响应了四个值，分别是页面大小，总页数，总胶囊数，和当前页数。
    //其中页面大小和当前页数是request的，实际只用了总胶囊数，总页数是前端自己算的

    if (res && Array.isArray(res.capsules)) {
      // 数据映射：将后端字段映射到前端组件期望的字段
      capsuleList.value = res.capsules.map(capsule => ({
        ...capsule,
        // 添加前端需要的状态字段
        is_mine: true,
        //TODO：返回的json要加一个bool值的liked和collected字段
        liked: false, // 初始化为未点赞状态，后续可以根据用户数据设置
        collected: false,    // 初始化为未收藏
        // 其他字段保持原样，因为组件现在直接使用后端字段名
      }))
      capsuleList.value = res.capsules
      capsuleTotal.value = res.pagination?.total ?? res.capsules.length
      //console.log(`打印获取到的胶囊列表，共 ${capsuleTotal.value} 个胶囊`, JSON.parse(JSON.stringify(capsuleList.value)))
    } else {
      rawCapsules = []
      capsuleTotal.value = 0
      console.warn('接口返回数据格式异常:', res)
    }

    // 映射后端字段到前端期望的字段格式
    capsuleList.value = rawCapsules.map(capsule => ({
      id: capsule.id,
      title: capsule.title,
      desc: capsule.content_preview || '', // 映射 content_preview -> desc
      vis: capsule.visibility, // 映射 visibility -> vis
      time: capsule.created_at, // 映射 created_at -> time
      likes: capsule.like_count || 0, // 映射 like_count -> likes
      views: capsule.unlock_count || 0,
      tags: capsule.tags || [],
      status: capsule.status,
      cover: capsule.cover_image,
      // 保留原始数据以备其他用途
      ...capsule
    }))
  } catch (error) {
    console.error('获取胶囊列表失败:', error)
    capsuleList.value = []
    capsuleTotal.value = 0
  } finally {
    isLoading.value = false
  }
}

/**
 * 辅助函数：获取可见性文本
 */
const getVisText = (vis) => {
  switch (vis) {
  case 'public': return '校园公开'
  case 'friend': return '好友可见'
  case 'private': return '仅自己可见'
  default: return '未知'
  }
}

/**
 * 辅助函数：获取解锁条件文本
 */
const getUnlockText = (type, value) => {
  // 如果没有触发条件（type为null或undefined），显示"无特殊条件"
  if (!type) return '无特殊条件'

  switch (type) {
  case 'time': return `时间触发（${formatStandard(value)}后）`
  case 'event':
    const eventMap = { 'graduation': '毕业典礼', 'freshman': '新生入学', 'anniversary': '校庆' }
    return `事件触发（${eventMap[value] || value}）`
  case 'location': return '地点触发（靠近5米内）'
  default: return '未知触发条件'
  }
}

// —— 顶部导航相关方法 ——
// reviewed
const handleGoHub = () => {
  router.push('/hubviews')
}

const handleHeaderSearch = (keyword) => {
  filter.value.search = keyword
}

const handleHeaderAction = (key) => {
  switch (key) {
    case 'create': handleOpenCreateForm(); break
    //TODO1: 后续对接实际功能,要加api
    //导出整个胶囊，包括图片等资源
    //设置隐私，vis=public/friend/private
    case 'export': alert('导出我的胶囊数据（后续对接导出接口）'); break
    case 'setting': alert('胶囊隐私设置（后续对接设置接口）'); break
  }
}

// —— 侧边导航相关方法 ——
// reviewed
const handleNavChange = (key) => {
  //TODO2：还要改路由跳转逻辑
  const routeMap = {
    myCapsule: '/my-capsule', 
    hub: '/hubviews', 
    map: '/map', 
    create: '/capsules',
    timeline: '/timeline', 
    events: '/events', 
    logout: '/logout'
  }
  
  if (key === 'create') {
    handleOpenCreateForm()
    return
  }
  
  if (key === 'logout') {
    //TODO3: 后续对接实际注销逻辑
    localStorage.removeItem('user_token')
    localStorage.removeItem('user_info')
    router.push('/login')
    return
  }
  
  router.push(routeMap[key] || '/my-capsule')
}

// —— 共用组件 CapsuleFilterBar 事件处理 ——
// reviewed
const handleFilterChange = async(params) => {
  if (params.type === 'vis') {
    filter.value.vis = params.value
    currentPage.value = 1 // 筛选变化重置页码
    await fetchCapsuleList()
  }
}

const handleSortChange = (sortType) => {
  filter.value.sort = sortType
}

const handleViewModeChange = (mode) => {
  viewMode.value = mode
}

const handleResetFilter = async() => {
  filter.value = { vis: 'public', sort: 'newest', search: '' }
  currentPage.value = 1
  await fetchCapsuleList()
}

// —— 分页相关方法 ——
// reviewed
const handlePageChange = async(page) => {
  currentPage.value = page
  await fetchCapsuleList()
}

// —— 共用组件 CapsuleActionButtons 事件处理 ——
// 原代码: const handleViewCapsule = (capsuleId) => { ... }
const handleViewCapsule = async(capsuleId) => {
  // 调用 getCapsuleDetail 获取最新详情 (TODO5)
  isProcessing.value[`view_${capsuleId}`] = true
  try {
    const detail = await getCapsuleDetail(capsuleId)
    if (detail) {
      currentDetailData.value = detail
      // 将解锁条件和媒体文件等详细信息映射到 currentDetailData
      currentDetailData.value.unlockType = detail.unlock_conditions?.type
      currentDetailData.value.unlockValue = detail.unlock_conditions?.value
      currentDetailData.value.location = detail.location?.address
      currentDetailData.value.img = detail.media_files?.[0]?.url // 假设取第一个媒体文件作为图片
      currentDetailData.value.likes = detail.like_count // 确保 likes 字段正确
      currentDetailData.value.views = detail.view_count // 确保 views 字段正确
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

//TODO: 点赞API
// 原代码: const handleLikeCapsule = (capsuleId) => { ... }
//TODO: 点赞API
const handleLikeCapsule = async(capsuleId) => {
  const capsule = capsuleList.value.find(c => c.id === capsuleId)
  if (!capsule) return

  isProcessing.value[`like_${capsuleId}`] = true
  try {
    // 🚨 修改点 9：调用 likeCapsule API (TODO: 点赞 API)
    const result = await likeCapsule(capsuleId) 
    
    // 乐观更新或根据 API 响应更新
    if (result.code === 200 || result.success) {
      // 假设 API 返回了新的点赞状态和计数
      const isLiked = result.data?.is_liked ?? !capsule.liked
      const newCount = result.data?.like_count ?? (capsule.like_count || 0) + (isLiked ? 1 : -1)

      capsule.liked = isLiked
      capsule.like_count = newCount
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

//TODO: 对接更新api
const handleEditCapsule = (capsuleId) => {
// 原代码: const handleEditCapsule = (capsuleId) => { ... }
//TODO: 对接更新api (逻辑已在 onCapsuleCreated 中统一处理)
const handleEditCapsule = (capsuleId) => {
  const capsule = capsuleList.value.find(c => c.id === capsuleId)
  if (capsule) {
    // 🚨 修改点 10：将详情数据赋给编辑表单，并关闭详情弹窗
    currentEditData.value = {
      ...capsule,
      content: capsule.desc, // 假设表单内容字段名为 content，但详情字段名为 desc
    } 
    isEditMode.value = true
    showFormModal.value = true
    handleCloseDetail() // 关闭详情弹窗，防止两个弹窗同时存在
  }
}

// 原代码: const handleDeleteCapsule = async(capsuleId) => { ... }
const handleDeleteCapsule = async(capsuleId) => {
  if (!confirm('确定要删除该胶囊吗？此操作不可恢复！')) return

  isProcessing.value[`delete_${capsuleId}`] = true
  try {
    const result = await deleteCapsule(capsuleId)
    // 🚨 修改点 11：完善删除成功的逻辑 (TODO8)
    if (result.code === 200 || result.success) {
      alert('删除成功！') 
      await fetchCapsuleList() // 重新加载列表
    } else {
      alert(result.message || '删除失败，请稍后重试')
    }
  } catch (error) {
    console.error(`删除胶囊(${capsuleId})失败：`, error)
    alert('删除失败，请稍后重试')
  } finally {
    isProcessing.value[`delete_${capsuleId}`] = false
  }
}

const handleShareCapsule = (capsule) => {
  //TODO6: 后续对接实际分享接口
  alert(`分享胶囊：${capsule.title}（后续对接分享接口，支持复制链接/微信分享）`)
}

const handleCollectCapsule = (capsuleId) => {
  const capsule = capsuleList.value.find(c => c.id === capsuleId)
  if (capsule) {
    capsule.collected = !capsule.collected
    //TODO7: api里面没有收藏的这一项
    alert(capsule.collected ? '收藏成功' : '取消收藏成功')
  }
}

// —— 胶囊表单相关方法（使用与中枢页相同的逻辑）——
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

// 只处理表单关闭和刷新，不再直接调用createCapsule，防止重复创建
const onCapsuleCreated = async() => {
  handleCloseForm()
  await fetchCapsuleList() // 重新加载列表
}

// —— 详情弹窗相关方法 ——
// reviewed
const handleCloseDetail = () => {
  showDetailModal.value = false
  currentDetailData.value = {}
}
</script>

<style scoped>
/* 页面整体样式：仅保留页面独有的布局样式，组件样式由共用组件自带 */
.my-capsule-page {
  background-color: var(--bg);
  min-height: 100vh;
}

/* 主体内容布局 */
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

/* 详情弹窗：页面独有的弹窗样式（组件无弹窗逻辑） */
.capsule-detail-modal {
  position: fixed;
  inset: 0;
  display: none;
  z-index: 1000;
}

.capsule-detail-modal.active {
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-overlay {
  position: absolute;
  inset: 0;
  background: rgba(8, 12, 20, 0.32);
  backdrop-filter: blur(4px);
}

.modal-panel {
  position: relative;
  width: 720px;
  max-width: 94%;
  max-height: 90vh;
  overflow-y: auto;
  background: var(--card);
  border-radius: var(--radius);
  padding: 24px;
  box-shadow: var(--shadow-lg);
  z-index: 1001;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(12, 18, 36, 0.06);
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: #1e293b;
}

.modal-close {
  background: transparent;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--muted);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #1e293b;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 14px;
  color: var(--muted);
}

.detail-image {
  width: 100%;
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.detail-img {
  width: 100%;
  height: auto;
  max-height: 400px;
  object-fit: cover;
}

.detail-desc {
  line-height: 1.6;
  color: #374151;
  white-space: pre-wrap;
  margin: 0;
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  padding: 4px 8px;
  border-radius: 6px;
  background: var(--accent-light);
  color: var(--accent);
  font-size: 13px;
}

.detail-stats {
  display: flex;
  gap: 16px;
  color: var(--muted);
  font-size: 14px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid rgba(12, 18, 36, 0.06);
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
</style>