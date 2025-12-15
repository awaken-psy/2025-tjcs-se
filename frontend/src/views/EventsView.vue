<template>
  <div class="events-page">
    <!-- 页面装饰 -->
    <div class="page-decoration" />
    
    <!-- 顶部导航 -->
    <AppHeader
      page-title="时光胶囊 · 校园活动"
      page-subtitle="浏览校园活动，报名参与感兴趣的活动，记录活动回忆"
      :show-search="true"
      search-placeholder="搜索活动名称/主办方/标签..."
      :actions="headerActions"
      @go-hub="handleGoHub"
      @search="handleSearch"
      @action-click="handleHeaderAction"
    />
    
    <!-- 主体内容 -->
    <div class="events-main">
      <!-- 侧边筛选栏 -->
      <div class="events-sidebar">
        <!-- 活动状态筛选 -->
        <div class="filter-card">
          <h3 class="filter-title">活动状态</h3>
          <div class="radio-group">
            <label 
              v-for="status in statusOptions" 
              :key="status.value"
              class="radio-item"
              :class="{ checked: filter.status === status.value }"
            >
              <input
                v-model="filter.status"
                type="radio"
                name="eventStatus"
                :value="status.value"
                class="radio-input"
                @change="handleFilterChange"
              >
              <span class="radio-dot"></span>
              {{ status.label }}
            </label>
          </div>
        </div>
        
        <!-- 时间范围筛选 -->
        <div class="filter-card">
          <h3 class="filter-title">时间范围</h3>
          <div class="date-group">
            <label class="form-label" for="event-start">开始时间</label>
            <input
              id="event-start"
              v-model="filter.startTime"
              type="date"
              class="form-control"
              @change="handleFilterChange"
            >
          </div>
          <div class="date-group">
            <label class="form-label" for="event-end">结束时间</label>
            <input
              id="event-end"
              v-model="filter.endTime"
              type="date"
              class="form-control"
              @change="handleFilterChange"
            >
          </div>
          <button class="btn small reset-date-btn" @click="resetDateFilter">
            <i class="fas fa-redo"></i> 重置为近3个月
          </button>
        </div>
        
        <!-- 我的报名统计 -->
        <div class="filter-card stats-card">
          <RegStatsCard
            :total-reg="myRegCount"
            :upcoming-reg="upcomingRegCount"
            :ended-reg="endedRegCount"
            card-title="我的报名"
            size="default"
            show-view-btn
            view-btn-text="查看我的报名列表"
            @view-list="handleShowMyReg"
            @click-all="handleClickRegTab('all')"
            @click-upcoming="handleClickRegTab('upcoming')"
            @click-ended="handleClickRegTab('ended')"
          />
        </div>
        
        <!-- 热门标签 -->
        <div class="filter-card">
          <h3 class="filter-title">热门标签</h3>
          <div class="tag-list">
            <span
              v-for="tag in hotTags"
              :key="tag"
              class="tag-item"
              @click="handleFilterByTag(tag)"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- 活动列表区 -->
      <div class="events-content">
        <!-- 控制栏 -->
        <div class="control-bar">
          <div class="sort-controls">
            <label class="sort-label">排序：</label>
            <select 
              v-model="filter.sort"
              class="sort-select"
              @change="handleFilterChange"
            >
              <option value="time">按时间（默认）</option>
              <option value="hot">按热度</option>
              <option value="deadline">按报名截止</option>
            </select>
          </div>
          <div class="view-controls">
            <button 
              class="view-btn"
              :class="{ active: viewMode === 'grid' }"
              @click="handleViewMode('grid')"
            >
              <i class="fas fa-th"></i> 网格视图
            </button>
            <button 
              class="view-btn"
              :class="{ active: viewMode === 'list' }"
              @click="handleViewMode('list')"
            >
              <i class="fas fa-list"></i> 列表视图
            </button>
          </div>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>正在加载活动数据...</p>
        </div>
        
        <!-- 活动列表 -->
        <div v-else class="events-list" :class="viewMode === 'grid' ? 'grid-view' : 'list-view'">
          <EventCard
            v-for="event in eventsList"
            :key="event.id"
            :event="event"
            :view-mode="viewMode"
            class="custom-event-card"
            @view="handleViewEvent"
            @register="handleRegister"
            @cancel-register="handleCancelRegister"
            @edit="handleEditEvent"
            @delete="handleDeleteEvent"
          />
          
          <!-- 空状态 -->
          <div v-if="eventsList.length === 0" class="empty-state">
            <div class="empty-icon-container">
              <i class="fas fa-calendar-alt empty-icon"></i>
            </div>
            <h4 class="empty-title">暂无活动</h4>
            <p class="empty-desc">当前筛选条件下无活动，尝试调整状态或时间范围</p>
            <button class="empty-action-btn" @click="resetDateFilter">
              <i class="fas fa-filter"></i> 重置筛选条件
            </button>
          </div>
        </div>
        
        <!-- 分页控件 -->
        <div v-if="totalEvents > 0 && !isLoading" class="pagination">
          <button 
            class="page-btn"
            :disabled="currentPage === 1 || isLoading"
            @click="handlePageChange(currentPage - 1)"
          >
            <i class="fas fa-chevron-left"></i> 上一页
          </button>
          <span class="page-info">{{ pageInfo }}</span>
          <button 
            class="page-btn"
            :disabled="currentPage >= totalPages || isLoading"
            @click="handlePageChange(currentPage + 1)"
          >
            下一页 <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>
    </div>
    
    <!-- 活动详情弹窗 -->
    <EventDetailModal
      :show="showDetailModal"
      :event="currentEvent"
      :is-processing="isProcessing[currentEvent.id] || false"
      @close="handleCloseDetail"
      @register="handleRegister"
      @cancel-register="handleCancelRegister"
    />
    
    <!-- 编辑活动弹窗 -->
    <EventEditModal
      :show="showEditModal"
      :event="editingEvent"
      @close="handleCloseEditModal"
      @save="handleUpdateEvent"
    />
    
    <!-- 我的报名弹窗 -->
    <MyRegistrationsModal
      :show="showMyRegModal"
      :events="myRegEvents"
      :loading="isLoading"
      :total="myRegCount"
      @close="handleCloseMyReg"
      @view="handleViewEvent"
      @register="handleRegister"
      @cancel-register="handleCancelRegister"
      @edit="handleEditEvent"
      @delete="handleDeleteEvent"
      @discover="handleDiscoverEvents"
    />
    
    <!-- 创建活动弹窗 -->
    <EventCreateModal
      :show="showCreateModal"
      @close="handleCloseCreateModal"
      @success="handleCreateEvent"
    />
  </div>
</template>


<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// API导入
import {
  createEvent,
  updateEvent,
  deleteEvent,
  getEventList,
  getEventDetail,
  getMyRegisteredEvents,
  registerForEvent,
  cancelEventRegistration
} from '@/api/new/EventsApi.js'

// 新增：上传API
import { uploadFile } from '@/api/new/uploadApi.js'

// 组件导入
import AppHeader from '@/components/AppHeader.vue'
import EventCard from '@/components/EventCard.vue'
import EventDetailModal from '@/components/EventDetailModal.vue'
import EventEditModal from '@/components/EventEditModal.vue'
import EventCreateModal from '@/components/EventCreateModal.vue'
import MyRegistrationsModal from '@/components/MyRegistrationsModal.vue'
import EventRegButton from '@/components/EventRegButton.vue'
import EventStatusBadge from '@/components/EventStatusBadge.vue'
import RegStatsCard from '@/components/RegStatsCard.vue'
import EventMetaInfo from '@/components/EventMetaInfo.vue'

const router = useRouter()

// 响应式数据
const eventsList = ref([])
const allEvents = ref([]) // 存储所有活动数据
const myRegEvents = ref([])
const totalEvents = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const isLoading = ref(false)
const isProcessing = ref({})
const viewMode = ref('grid')

// 弹窗状态
const showDetailModal = ref(false)
const showEditModal = ref(false)
const showMyRegModal = ref(false)
const showCreateModal = ref(false)
const currentEvent = ref({})
const editingEvent = ref({})

// 筛选条件
const filter = reactive({
  status: 'all',
  startTime: getDefaultStartDate(),
  endTime: getDefaultEndDate(),
  sort: 'time',
  search: ''
})

// 静态数据
const headerActions = [
  { key: 'create', text: '创建活动', icon: '✚', type: 'primary' },
  { key: 'myReg', text: '我的报名', icon: '📝', type: 'ghost' },
  { key: 'refresh', text: '刷新', icon: '🔄', type: 'ghost' }
]

const statusOptions = [
  { value: 'all', label: '全部活动' },
  { value: 'upcoming', label: '未开始' },
  { value: 'ongoing', label: '进行中' },
  { value: 'ended', label: '已结束' }
]

const hotTags = ['毕业季', '文化节', '校友分享', '体育比赛', '讲座', '社团活动']

// 计算属性
const myRegCount = computed(() => myRegEvents.value.length)
const upcomingRegCount = computed(() => myRegEvents.value.filter(e => getEventStatus(e) === 'upcoming').length)
const endedRegCount = computed(() => myRegEvents.value.filter(e => getEventStatus(e) === 'ended').length)
const totalPages = computed(() => Math.ceil(totalEvents.value / pageSize.value))
const pageInfo = computed(() => {
  if (totalEvents.value === 0) return '暂无活动'
  const start = (currentPage.value - 1) * pageSize.value + 1
  const end = Math.min(currentPage.value * pageSize.value, totalEvents.value)
  return `第 ${start}-${end} 条 / 共 ${totalEvents.value} 条`
})

// 辅助函数
function getDefaultStartDate() {
  const date = new Date()
  date.setFullYear(date.getFullYear() - 1) // 放宽到1年前
  return date.toISOString().split('T')[0]
}

function getDefaultEndDate() {
  const date = new Date()
  date.setFullYear(date.getFullYear() + 1) // 放宽到1年后
  return date.toISOString().split('T')[0]
}

function getEventStatus(event) {
  if (!event.date) return 'upcoming'
  const now = new Date()
  const eventDate = new Date(event.date)
  return eventDate < now ? 'ended' : 'upcoming'
}

// 图片上传辅助函数
async function uploadImageIfNeeded(coverImg) {
  if (!coverImg) return null
  
  // 如果是base64图片，需要上传
  if (coverImg.startsWith('data:image')) {
    try {
      console.log('检测到base64图片，开始上传...')
      
      // 将base64转换为Blob
      const response = await fetch(coverImg)
      const blob = await response.blob()
      
      // 创建File对象
      const fileType = coverImg.split(';')[0].split('/')[1]
      const fileName = `event_cover_${Date.now()}.${fileType}`
      const file = new File([blob], fileName, { type: `image/${fileType}` })
      
      // 调用上传API
      const uploadResult = await uploadFile(file, 'image')
      console.log('图片上传成功:', uploadResult)
      
      // 根据拦截器，返回的是data部分
      if (uploadResult && uploadResult.url) {
        return uploadResult.url
      }
      return null
    } catch (error) {
      console.error('图片上传失败:', error)
      throw new Error('图片上传失败，请稍后重试')
    }
  }
  
  // 如果是URL，直接返回
  return coverImg
}

// 本地筛选函数
function filterEventsLocally(allEvents) {
  if (!Array.isArray(allEvents)) return []
  
  let filteredEvents = [...allEvents]
  
  // 关键词筛选
  if (filter.search && filter.search.trim()) {
    const keyword = filter.search.toLowerCase().trim()
    filteredEvents = filteredEvents.filter(event => 
      event.name?.toLowerCase().includes(keyword) ||
      event.description?.toLowerCase().includes(keyword) ||
      event.location?.toLowerCase().includes(keyword) ||
      (Array.isArray(event.tags) && event.tags.some(tag => 
        tag.toLowerCase().includes(keyword)
      ))
    )
  }
  
  // 状态筛选
  if (filter.status !== 'all') {
    const now = new Date()
    filteredEvents = filteredEvents.filter(event => {
      if (!event.date) {
        // 没有日期的活动，根据状态决定是否显示
        return filter.status === 'upcoming' || filter.status === 'all'
      }
      
      const eventDate = new Date(event.date)
      
      switch (filter.status) {
        case 'upcoming':
          return eventDate >= now
        case 'ongoing':
          // 假设活动持续一天，可以扩展为支持多日活动
          return eventDate <= now && new Date(eventDate.getTime() + 24 * 60 * 60 * 1000) > now
        case 'ended':
          return eventDate < now
        default:
          return true
      }
    })
  }
  
  // 时间范围筛选
  if (filter.startTime) {
    const startDate = new Date(filter.startTime)
    filteredEvents = filteredEvents.filter(event => {
      if (!event.date) return true // 没有日期的活动不过滤
      const eventDate = new Date(event.date)
      return eventDate >= startDate
    })
  }
  
  if (filter.endTime) {
    const endDate = new Date(filter.endTime)
    endDate.setHours(23, 59, 59, 999) // 设置为当天的最后一刻
    filteredEvents = filteredEvents.filter(event => {
      if (!event.date) return true // 没有日期的活动不过滤
      const eventDate = new Date(event.date)
      return eventDate <= endDate
    })
  }
  
  // 排序
  filteredEvents.sort((a, b) => {
    // 处理没有日期的情况
    if (!a.date && !b.date) return 0
    if (!a.date) return 1 // 没有日期的排在后面
    if (!b.date) return -1 // 没有日期的排在后面
    
    const dateA = new Date(a.date)
    const dateB = new Date(b.date)
    
    switch (filter.sort) {
      case 'hot':
        // 按参与人数排序（降序）
        return (b.participant_count || 0) - (a.participant_count || 0)
      case 'deadline':
        // 按截止时间排序（升序）
        return dateA - dateB
      case 'time':
      default:
        // 按时间排序（升序）
        return dateA - dateB
    }
  })
  
  return filteredEvents
}

// API 调用函数
async function fetchEventsList() {
  isLoading.value = true
  try {
    // 获取所有活动数据（不传筛选参数）
    const result = await getEventList({})
    console.log('fetchEventsList 返回结果:', result)
    
    if (result && typeof result === 'object') {
      let fetchedEvents = []
      
      // 检查后端返回的数据结构
      if (result.list && Array.isArray(result.list)) {
        fetchedEvents = result.list
      } else if (result.data && Array.isArray(result.data)) {
        fetchedEvents = result.data
      } else if (Array.isArray(result)) {
        fetchedEvents = result
      }
      
      // 存储所有活动数据
      allEvents.value = fetchedEvents
      
      // 应用本地筛选
      applyLocalFilter()
      
    } else {
      allEvents.value = []
      eventsList.value = []
      totalEvents.value = 0
    }
  } catch (error) {
    console.error('获取活动列表异常:', error)
    allEvents.value = []
    eventsList.value = []
    totalEvents.value = 0
  } finally {
    isLoading.value = false
  }
}

async function fetchMyRegEvents() {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    // 注意：axios拦截器已经返回了data部分
    const result = await getMyRegisteredEvents(params)
    console.log('fetchMyRegEvents 返回结果:', result)
    
    if (result && typeof result === 'object') {
      if (result.list && Array.isArray(result.list)) {
        myRegEvents.value = result.list
      } else if (result.data && Array.isArray(result.data)) {
        myRegEvents.value = result.data
      } else if (Array.isArray(result)) {
        myRegEvents.value = result
      } else {
        myRegEvents.value = []
      }
    } else {
      myRegEvents.value = []
    }
  } catch (error) {
    console.error('获取我的报名列表异常:', error)
    myRegEvents.value = []
  }
}

async function fetchEventDetail(eventId) {
  try {
    // 注意：axios拦截器已经返回了data部分
    const result = await getEventDetail(eventId)
    console.log('fetchEventDetail 返回结果:', result)
    
    if (result && typeof result === 'object') {
      return result
    }
    return null
  } catch (error) {
    console.error('获取活动详情异常:', error)
    return null
  }
}

async function handleRegister(eventId) {
  if (!eventId) return
  
  isProcessing.value[eventId] = true
  try {
    // 注意：axios拦截器已经处理了成功响应，只会在出错时抛出异常
    const result = await registerForEvent(eventId)
    console.log('handleRegister 返回结果:', result)
    
    // 如果走到这里，说明请求成功
    alert('报名成功！')
    // 刷新列表
    await Promise.all([fetchEventsList(), fetchMyRegEvents()])
  } catch (error) {
    console.error('报名异常:', error)
    alert(error.message || '报名失败，请稍后重试')
  } finally {
    isProcessing.value[eventId] = false
  }
}

async function handleCancelRegister(eventId) {
  if (!eventId) return
  
  isProcessing.value[eventId] = true
  try {
    // 注意：axios拦截器已经处理了成功响应，只会在出错时抛出异常
    const result = await cancelEventRegistration(eventId)
    console.log('handleCancelRegister 返回结果:', result)
    
    // 如果走到这里，说明请求成功
    alert('取消报名成功！')
    // 刷新列表
    await Promise.all([fetchEventsList(), fetchMyRegEvents()])
  } catch (error) {
    console.error('取消报名异常:', error)
    alert(error.message || '取消报名失败，请稍后重试')
  } finally {
    isProcessing.value[eventId] = false
  }
}

async function handleCreateEvent(eventData) {
  try {
    console.log('开始创建活动，原始数据:', eventData)
    
    // 处理图片上传
    let coverImageUrl = null
    if (eventData.cover_img) {
      try {
        coverImageUrl = await uploadImageIfNeeded(eventData.cover_img)
        console.log('图片处理结果:', coverImageUrl)
      } catch (uploadError) {
        console.error('图片上传失败，继续创建活动:', uploadError)
        // 图片上传失败，仍然创建活动，但不带图片
      }
    }
    
    // 准备提交数据
    const submitData = {
      name: eventData.name,
      description: eventData.description,
      date: eventData.date,
      location: eventData.location,
      tags: eventData.tags,
      ...(coverImageUrl && { cover_img: coverImageUrl })
    }
    
    console.log('提交的活动数据:', submitData)
    
    // 注意：axios拦截器已经处理了成功响应
    const result = await createEvent(submitData)
    console.log('handleCreateEvent 返回结果:', result)
    
    // 如果走到这里，说明请求成功
    alert('活动创建成功！')
    handleCloseCreateModal()
    // 刷新列表
    await fetchEventsList()
  } catch (error) {
    console.error('创建活动异常:', error)
    alert(error.message || '活动创建失败，请稍后重试')
  }
}

async function handleEditEvent(eventId) {
  const event = await fetchEventDetail(eventId)
  if (event) {
    editingEvent.value = event
    showEditModal.value = true
  }
}

async function handleUpdateEvent(updatedData) {
  try {
    console.log('开始更新活动，原始数据:', updatedData)
    
    // 处理图片上传
    let coverImageUrl = null
    if (updatedData.cover_img) {
      try {
        coverImageUrl = await uploadImageIfNeeded(updatedData.cover_img)
        console.log('图片处理结果:', coverImageUrl)
      } catch (uploadError) {
        console.error('图片上传失败，继续更新活动:', uploadError)
        // 图片上传失败，仍然更新活动，但保留原有图片或清空
        if (editingEvent.value.cover_img) {
          coverImageUrl = editingEvent.value.cover_img
        }
      }
    }
    
    // 准备提交数据
    const submitData = {
      name: updatedData.name,
      description: updatedData.description,
      date: updatedData.date,
      location: updatedData.location,
      tags: updatedData.tags,
      ...(coverImageUrl !== null && { cover_img: coverImageUrl })
    }
    
    console.log('提交的更新数据:', submitData)
    
    // 注意：axios拦截器已经处理了成功响应
    const result = await updateEvent(editingEvent.value.id, submitData)
    console.log('handleUpdateEvent 返回结果:', result)
    
    // 如果走到这里，说明请求成功
    alert('活动更新成功！')
    handleCloseEditModal()
    // 刷新列表
    await Promise.all([fetchEventsList(), fetchMyRegEvents()])
  } catch (error) {
    console.error('更新活动异常:', error)
    alert(error.message || '活动更新失败，请稍后重试')
  }
}

async function handleDeleteEvent(eventId) {
  if (!eventId || !confirm('确定要删除这个活动吗？此操作不可撤销。')) return
  
  try {
    // 注意：axios拦截器已经处理了成功响应
    const result = await deleteEvent(eventId)
    console.log('handleDeleteEvent 返回结果:', result)
    
    // 如果走到这里，说明请求成功
    alert('活动删除成功！')
    // 刷新列表
    await Promise.all([fetchEventsList(), fetchMyRegEvents()])
  } catch (error) {
    console.error('删除活动异常:', error)
    alert(error.message || '活动删除失败，请稍后重试')
  }
}

// 事件处理函数（保持不变）
function handleGoHub() {
  router.push({ name: 'HubViews' })
}

function handleSearch(keyword) {
  filter.search = keyword
  currentPage.value = 1
  fetchEventsList()
}

function handleHeaderAction(key) {
  switch (key) {
    case 'create':
      handleShowCreateModal()
      break
    case 'myReg':
      handleShowMyReg()
      break
    case 'refresh':
      handleRefresh()
      break
  }
}

function handleFilterChange() {
  currentPage.value = 1
  // 直接应用本地筛选，不需要重新调用API
  applyLocalFilter()
}

function resetDateFilter() {
  filter.startTime = getDefaultStartDate()
  filter.endTime = getDefaultEndDate()
  filter.search = ''
  filter.status = 'all'
  currentPage.value = 1
  applyLocalFilter()
}

function handleFilterByTag(tag) {
  filter.search = tag
  currentPage.value = 1
  applyLocalFilter()
}

// 应用本地筛选
function applyLocalFilter() {
  if (!allEvents.value || allEvents.value.length === 0) {
    // 如果没有数据，显示空列表
    eventsList.value = []
    totalEvents.value = 0
    return
  }
  
  // 应用筛选
  const filteredEvents = filterEventsLocally(allEvents.value)
  
  // 分页处理
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  eventsList.value = filteredEvents.slice(startIndex, endIndex)
  totalEvents.value = filteredEvents.length
}

function handleViewMode(mode) {
  viewMode.value = mode
}

function handlePageChange(page) {
  currentPage.value = page
  applyLocalFilter()
}

async function handleViewEvent(eventId) {
  const event = await fetchEventDetail(eventId)
  if (event) {
    currentEvent.value = event
    showDetailModal.value = true
  }
}

function handleCloseDetail() {
  showDetailModal.value = false
  currentEvent.value = {}
}

function handleCloseEditModal() {
  showEditModal.value = false
  editingEvent.value = {}
}

function handleShowMyReg() {
  showMyRegModal.value = true
}

function handleCloseMyReg() {
  showMyRegModal.value = false
}

function handleClickRegTab(tab) {
  showMyRegModal.value = true
}

function handleDiscoverEvents() {
  handleCloseMyReg()
  resetDateFilter()
}

function handleShowCreateModal() {
  showCreateModal.value = true
}

function handleCloseCreateModal() {
  showCreateModal.value = false
}

function handleRefresh() {
  currentPage.value = 1
  filter.search = ''
  fetchEventsList()
}

// 生命周期
onMounted(() => {
  fetchEventsList()
  fetchMyRegEvents()
})
</script>



<style scoped>
/* 全局样式重置与基础配置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 页面主容器（升级背景质感） */
.events-page {
  background: linear-gradient(180deg, #f9faff 0%, #f0f7ff 100%);
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

/* 顶部装饰层（新增，提升视觉层次） */
.page-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 240px;
  background: linear-gradient(135deg, #e8f4f8 0%, #f0f8fb 100%);
  border-radius: 0 0 50% 50% / 20px;
  z-index: 0;
  opacity: 0.8;
}

/* 主体内容布局（优化比例与间距） */
.events-main {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 30px;
  padding: 20px 30px 60px;
  max-width: 1600px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

/* 侧边筛选栏（优化固定效果与间距） */
.events-sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: sticky;
  top: 120px;
  height: fit-content;
  padding-top: 10px;
}

/* 筛选卡片（全量视觉升级） */
.filter-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(149, 157, 165, 0.08);
  border: 1px solid rgba(230, 236, 240, 0.8);
  backdrop-filter: blur(12px);
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
  position: relative;
}

/* 卡片渐变装饰（新增） */
.filter-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #4299e1, #38b2ac);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.filter-card:hover {
  box-shadow: 0 12px 32px rgba(149, 157, 165, 0.12);
  transform: translateY(-4px);
}

.filter-card:hover::before {
  opacity: 1;
}

/* 统计卡片特殊样式 */
.stats-card {
  background: linear-gradient(135deg, #f5fafe 0%, #eaf6fa 100%);
  border: 1px solid rgba(66, 153, 225, 0.15);
}

/* 筛选标题（优化样式） */
.filter-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 20px 0;
  color: #2d3748;
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
}

.filter-title::before {
  content: '';
  width: 4px;
  height: 20px;
  background: #4299e1;
  border-radius: 2px;
}

/* 单选按钮（全量视觉重写） */
.radio-group {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 12px;
  transition: all 0.3s ease;
  color: #4a5568;
  font-size: 15px;
  position: relative;
  overflow: hidden;
}

.radio-item:hover {
  background: rgba(66, 153, 225, 0.05);
  color: #2d3748;
}

.radio-item.checked {
  background: rgba(66, 153, 225, 0.1);
  color: #4299e1;
  font-weight: 500;
}

.radio-input {
  appearance: none;
  width: 0;
  height: 0;
  opacity: 0;
}

.radio-dot {
  display: inline-block;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid #cbd5e0;
  transition: all 0.3s ease;
  position: relative;
}

.radio-item.checked .radio-dot {
  border-color: #4299e1;
  background-color: #4299e1;
}

.radio-item.checked .radio-dot::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: white;
  animation: dotScale 0.3s ease;
}

/* 表单控件（全量升级） */
.form-control {
  width: 100%;
  padding: 12px 16px;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  background: white;
  font-size: 15px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
  color: #2d3748;
  font-weight: 400;
}

.form-control:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 4px rgba(66, 153, 225, 0.1);
  transform: translateY(-1px);
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #718096;
  font-weight: 500;
}

.date-group {
  margin-bottom: 16px;
}

/* 重置按钮（样式升级） */
.reset-date-btn {
  width: 100%;
  margin-top: 10px;
  background: rgba(66, 153, 225, 0.08);
  color: #4299e1;
  border: 1px solid transparent;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 14px;
  border: none;
}

.reset-date-btn:hover {
  background: #4299e1;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.2);
}

/* 活动列表区（优化间距） */
.events-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-top: 10px;
}

/* 控制栏（视觉升级） */
.control-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 24px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(149, 157, 165, 0.06);
  border: 1px solid rgba(230, 236, 240, 0.5);
  transition: all 0.3s ease;
}

.control-bar:hover {
  box-shadow: 0 6px 20px rgba(149, 157, 165, 0.08);
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sort-label {
  font-size: 15px;
  color: #4a5568;
  font-weight: 500;
}

/* 排序下拉框（样式升级） */
.sort-select {
  padding: 12px 16px;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  background: white;
  font-size: 15px;
  cursor: pointer;
  min-width: 180px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  color: #2d3748;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%234a5568' viewBox='0 0 16 16'%3E%3Cpath d='M8 11l4-4H4l4 4z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 16px center;
  padding-right: 40px;
}

.sort-select:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 4px rgba(66, 153, 225, 0.1);
  transform: translateY(-1px);
}

/* 视图切换按钮（样式升级） */
.view-controls {
  display: flex;
  gap: 10px;
}

.view-btn {
  background: transparent;
  border: 1px solid #e2e8f0;
  color: #4a5568;
  padding: 10px 20px;
  border-radius: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  font-weight: 500;
  border: none;
}

.view-btn:hover {
  background: rgba(66, 153, 225, 0.05);
  color: #4299e1;
  border-color: rgba(66, 153, 225, 0.3);
  transform: translateY(-1px);
}

.view-btn.active {
  background: #4299e1;
  color: white;
  border-color: #4299e1;
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.2);
}

.view-btn.active:hover {
  background: #3182ce;
  border-color: #3182ce;
}

/* 加载状态（优化动画） */
.loading-state {
  text-align: center;
  padding: 100px 20px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(149, 157, 165, 0.06);
  border: 1px solid rgba(230, 236, 240, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(66, 153, 225, 0.1);
  border-top-color: #4299e1;
  border-radius: 50%;
  animation: spin 1.2s linear infinite;
  position: relative;
}

.loading-spinner::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  border: 2px solid rgba(66, 153, 225, 0.05);
  border-radius: 50%;
}

.loading-state p {
  font-size: 16px;
  color: #4a5568;
  font-weight: 500;
}

/* 活动列表布局（优化间距与响应式） */
.events-list.grid-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 28px;
}

.events-list.list-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 胶囊卡片（自定义样式） */
.custom-event-card {
  border-radius: 20px !important;
  overflow: hidden;
  box-shadow: 0 6px 20px rgba(149, 157, 165, 0.08) !important;
  border: 1px solid rgba(230, 236, 240, 0.6) !important;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
  background: white !important;
}

.custom-event-card:hover {
  transform: translateY(-6px) !important;
  box-shadow: 0 12px 30px rgba(149, 157, 165, 0.12) !important;
  border-color: rgba(66, 153, 225, 0.2) !important;
}

/* 空状态（全量视觉升级） */
.empty-state {
  text-align: center;
  padding: 80px 40px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(149, 157, 165, 0.06);
  border: 1px solid rgba(230, 236, 240, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  transition: all 0.3s ease;
}

.empty-state.small {
  padding: 60px 20px;
}

.empty-icon-container {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #e8f4f8 0%, #f0f8fb 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(149, 157, 165, 0.08);
  transition: all 0.3s ease;
}

.empty-state:hover .empty-icon-container {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(149, 157, 165, 0.1);
}

.empty-icon {
  font-size: 48px;
  color: #4299e1;
  transition: all 0.3s ease;
}

.empty-state:hover .empty-icon {
  transform: rotate(5deg) scale(1.1);
}

.empty-title {
  font-size: 22px;
  font-weight: 600;
  margin: 0;
  color: #2d3748;
}

.empty-desc {
  color: #718096;
  font-size: 16px;
  max-width: 400px;
  line-height: 1.6;
}

/* 空状态操作按钮（新增） */
.empty-action-btn {
  padding: 12px 24px;
  border-radius: 14px;
  background: #4299e1;
  color: white;
  border: none;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.2);
}

.empty-action-btn:hover {
  background: #3182ce;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(66, 153, 225, 0.25);
}

/* 分页控件（视觉升级） */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  padding: 16px 24px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(149, 157, 165, 0.06);
  border: 1px solid rgba(230, 236, 240, 0.5);
  transition: all 0.3s ease;
}

.pagination:hover {
  box-shadow: 0 6px 20px rgba(149, 157, 165, 0.08);
}

.page-btn {
  background: transparent;
  border: 1px solid #e2e8f0;
  color: #4299e1;
  padding: 12px 24px;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  font-weight: 500;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
}

.page-btn:hover:enabled {
  background: #4299e1;
  color: white;
  border-color: #4299e1;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.2);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  color: #a0aec0;
  border-color: #e2e8f0;
  transform: none;
  box-shadow: none;
}

.page-info {
  color: #4a5568;
  font-size: 15px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 热门标签样式 */
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-item {
  background: rgba(66, 153, 225, 0.1);
  color: #4299e1;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid transparent;
}

.tag-item:hover {
  background: #4299e1;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.2);
}

/* 弹窗系统（全量视觉升级） */
.event-detail-modal,
.event-edit-modal,
.my-reg-modal,
.event-create-modal {
  position: fixed;
  inset: 0;
  display: none;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.event-detail-modal.active,
.event-edit-modal.active,
.my-reg-modal.active,
.event-create-modal.active {
  display: flex;
  align-items: center;
  justify-content: center;
  animation: modalFadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-overlay {
  position: absolute;
  inset: 0;
  background: rgba(17, 24, 39, 0.6);
  backdrop-filter: blur(6px);
  transition: all 0.4s ease;
  opacity: 0;
  animation: overlayFadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* 弹窗动画 */
@keyframes modalFadeIn {
  from { background: rgba(17, 24, 39, 0); }
  to { background: rgba(17, 24, 39, 0.6); }
}

@keyframes overlayFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes panelSlideIn {
  100% {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

/* 报名按钮自定义样式 */
.custom-reg-btn {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.custom-reg-btn:not(:disabled):hover {
  transform: translateY(-2px) !important;
}

.custom-reg-btn:disabled {
  opacity: 0.7 !important;
  cursor: not-allowed !important;
  transform: none !important;
  box-shadow: none !important;
}

/* 辅助样式 */
.danger {
  color: #e53e3e;
  font-weight: 500;
}

.success {
  color: #48bb78;
}

/* 动画定义 */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes dotScale {
  0% {
    transform: translate(-50%, -50%) scale(0);
  }
  70% {
    transform: translate(-50%, -50%) scale(1.2);
  }
  100% {
    transform: translate(-50%, -50%) scale(1);
  }
}

/* 响应式优化（全量适配） */
@media (max-width: 1200px) {
  .events-main {
    grid-template-columns: 280px 1fr;
    gap: 24px;
    padding: 16px 24px 40px;
  }

  .events-list.grid-view {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 24px;
  }
}

@media (max-width: 992px) {
  .meta-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .reg-item {
    gap: 16px;
    padding: 16px;
  }

  .reg-img {
    width: 80px;
    height: 80px;
  }
}

@media (max-width: 768px) {
  .events-main {
    grid-template-columns: 1fr;
    gap: 20px;
    padding: 16px 16px 30px;
  }

  .events-sidebar {
    position: static;
    padding-top: 0;
  }

  .filter-card {
    padding: 20px;
    border-radius: 16px;
  }

  .control-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
    padding: 16px 20px;
  }

  .sort-controls, .view-controls {
    width: 100%;
  }

  .view-controls {
    justify-content: space-between;
  }

  .view-btn {
    flex: 1;
    justify-content: center;
    padding: 10px 0;
  }

  .events-list.grid-view {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .pagination {
    gap: 12px;
    padding: 12px 16px;
  }

  .page-btn {
    padding: 10px 16px;
    font-size: 14px;
  }

  .page-info {
    font-size: 14px;
  }

  .empty-state {
    padding: 60px 20px;
  }

  .empty-icon-container {
    width: 80px;
    height: 80px;
  }

  .empty-icon {
    font-size: 40px;
  }

  .empty-title {
    font-size: 18px;
  }

  .empty-desc {
    font-size: 14px;
  }
}

@media (max-width: 576px) {
  .filter-title {
    font-size: 16px;
    margin-bottom: 16px;
  }

  .radio-item {
    font-size: 14px;
    padding: 6px 10px;
  }

  .form-control {
    padding: 10px 14px;
    font-size: 14px;
  }

  .sort-select {
    min-width: auto;
    width: 100%;
    padding: 10px 14px;
    font-size: 14px;
  }

  .page-info {
    font-size: 13px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 12px;
  }
}
</style>