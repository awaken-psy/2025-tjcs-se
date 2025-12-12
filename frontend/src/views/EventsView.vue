<template>
  <!-- 校园活动页：视觉全量优化，功能保持不变 -->
  <div class="events-page">
    <!-- 顶部装饰层（新增，提升层次感） -->
    <div class="page-decoration" />

    <!-- 顶部导航（复用组件，优化样式绑定） -->
    <AppHeader
      page-title="时光胶囊 · 校园活动"
      page-subtitle="浏览校园活动，报名参与感兴趣的活动，记录活动回忆"
      :show-search="true"
      search-placeholder="搜索活动名称/主办方/标签..."
      :actions="[
        { key: 'create', text: '创建活动', icon: '✚', type: 'primary' },
        { key: 'myReg', text: '我的报名', icon: '📝', type: 'ghost' },
        { key: 'refresh', text: '刷新', icon: '🔄', type: 'ghost' }
      ]"
      class="custom-header"
      @go-hub="handleGoHub"
      @search="handleSearch"
      @action-click="handleHeaderAction"
    />

    <!-- 主体内容：优化布局比例与间距 -->
    <div class="events-main">
      <!-- 侧边筛选栏（固定宽度，优化滚动体验） -->
      <div class="events-sidebar">
        <!-- 活动状态筛选（视觉升级） -->
        <div class="filter-card">
          <h3 class="filter-title">
            活动状态
          </h3>
          <div class="radio-group">
            <label
              class="radio-item"
              :class="{ checked: filter.status === 'all' }"
            >
              <input
                v-model="filter.status"
                type="radio"
                name="eventStatus"
                value="all"
                class="radio-input"
                @change="handleFilterChange"
              >
              <span class="radio-dot" />
              全部活动
            </label>
            <label
              class="radio-item"
              :class="{ checked: filter.status === 'upcoming' }"
            >
              <input
                v-model="filter.status"
                type="radio"
                name="eventStatus"
                value="upcoming"
                class="radio-input"
                @change="handleFilterChange"
              >
              <span class="radio-dot" />
              未开始
            </label>
            <label
              class="radio-item"
              :class="{ checked: filter.status === 'ongoing' }"
            >
              <input
                v-model="filter.status"
                type="radio"
                name="eventStatus"
                value="ongoing"
                class="radio-input"
                @change="handleFilterChange"
              >
              <span class="radio-dot" />
              进行中
            </label>
            <label
              class="radio-item"
              :class="{ checked: filter.status === 'ended' }"
            >
              <input
                v-model="filter.status"
                type="radio"
                name="eventStatus"
                value="ended"
                class="radio-input"
                @change="handleFilterChange"
              >
              <span class="radio-dot" />
              已结束
            </label>
          </div>
        </div>

        <!-- 时间范围筛选（样式升级） -->
        <div class="filter-card">
          <h3 class="filter-title">
            时间范围
          </h3>
          <div class="date-group">
            <label
              class="form-label"
              for="event-start"
            >开始时间</label>
            <input
              id="event-start"
              v-model="filter.startTime"
              type="date"
              class="form-control"
              @change="handleFilterChange"
            >
          </div>
          <div class="date-group">
            <label
              class="form-label"
              for="event-end"
            >结束时间</label>
            <input
              id="event-end"
              v-model="filter.endTime"
              type="date"
              class="form-control"
              @change="handleFilterChange"
            >
          </div>
          <button 
            class="btn small reset-date-btn"
            @click="resetDateFilter"
          >
            <i class="fas fa-redo" /> 重置为近3个月
          </button>
        </div>

        <!-- 我的报名统计（组件样式同步优化） -->
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

        <!-- 热门标签（视觉升级） -->
        <div class="filter-card">
          <h3 class="filter-title">
            热门标签
          </h3>
          <div class="tag-list">
            <span
              v-for="(tag, idx) in hotTags"
              :key="idx"
              class="tag-item"
              @click="handleFilterByTag(tag)"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </div>

      <!-- 活动列表区（优化布局与卡片样式） -->
      <div class="events-content">
        <!-- 控制栏（视觉升级，增加背景层次） -->
        <div class="control-bar">
          <div class="sort-controls">
            <label class="sort-label">排序：</label>
            <select 
              v-model="filter.sort"
              class="sort-select"
              @change="handleFilterChange"
            >
              <option value="time">
                按时间（默认）
              </option>
              <option value="hot">
                按热度
              </option>
              <option value="deadline">
                按报名截止
              </option>
            </select>
          </div>
          <div class="view-controls">
            <button 
              class="view-btn" 
              :class="{ active: viewMode === 'grid' }"
              @click="handleViewMode('grid')"
            >
              <i class="fas fa-th" /> 网格视图
            </button>
            <button 
              class="view-btn" 
              :class="{ active: viewMode === 'list' }"
              @click="handleViewMode('list')"
            >
              <i class="fas fa-list" /> 列表视图
            </button>
          </div>
        </div>

        <!-- 加载状态（优化动画与布局） -->
        <div
          v-if="isLoading"
          class="loading-state"
        >
          <div class="loading-spinner" />
          <p>正在加载活动数据...</p>
        </div>

        <!-- 活动列表（卡片样式全量升级） -->
        <div 
          v-else
          class="events-list"
          :class="viewMode === 'grid' ? 'grid-view' : 'list-view'"
        >
          <CapsuleCard
            v-for="event in filteredEvents"
            :key="event.id"
            :capsule="adaptEventToCapsule(event)"
            :view-mode="viewMode"
            class="custom-capsule-card"
            @view="handleViewEvent(event.id)"
            @click="handleViewEvent(event.id)"
          >
            <!-- 活动报名按钮（样式同步优化） -->
            <div
              slot="actions"
              class="event-extra-actions"
            >
              <EventRegButton
                :is-registered="event.isRegistered"
                :is-loading="isProcessing[event.id]"
                :is-disabled="isEventDisabled(event)"
                :disabled-tip="getDisabledTip(event)"
                size="default"
                reg-text="立即报名"
                cancel-text="取消报名"
                class="custom-reg-btn"
                @reg="handleRegister(event.id)"
                @cancel="handleCancelReg(event.id)"
              />
            </div>
          </CapsuleCard>

          <!-- 空状态（视觉升级） -->
          <div
            v-if="filteredEvents.length === 0"
            class="empty-state"
          >
            <div class="empty-icon-container">
              <i class="fas fa-calendar-alt empty-icon" />
            </div>
            <h4 class="empty-title">
              暂无活动
            </h4>
            <p class="empty-desc">
              当前筛选条件下无活动，尝试调整状态或时间范围
            </p>
            <button
              class="empty-action-btn"
              @click="resetDateFilter"
            >
              <i class="fas fa-filter" /> 重置筛选条件
            </button>
          </div>
        </div>

        <!-- 分页控件（视觉升级） -->
        <div
          v-if="totalEvents > 0 && !isLoading"
          class="pagination"
        >
          <button 
            class="page-btn" 
            :disabled="currentPage === 1 || isLoading || totalEvents === 0"
            @click="handlePageChange(currentPage - 1)"
          >
            <i class="fas fa-chevron-left" /> 上一页
          </button>
          <span class="page-info">
            {{ pageInfo }}
          </span>
          <button 
            class="page-btn" 
            :disabled="currentPage >= Math.ceil(totalEvents / pageSize) || isLoading || totalEvents === 0"
            @click="handlePageChange(currentPage + 1)"
          >
            下一页 <i class="fas fa-chevron-right" />
          </button>
        </div>
      </div>
    </div>

    <!-- 活动详情弹窗（视觉全量升级） -->
    <div
      class="event-detail-modal"
      :class="{ active: showDetailModal }"
    >
      <div
        class="modal-overlay"
        @click="handleCloseDetail"
      />
      <div class="modal-panel">
        <div class="modal-header">
          <h3 class="modal-title">
            {{ currentEvent.name }}
          </h3>
          <button
            class="modal-close"
            @click="handleCloseDetail"
          >
            <i class="fas fa-times" />
          </button>
        </div>
        <div class="modal-body">
          <!-- 活动封面（优化圆角与阴影） -->
          <div
            v-if="currentEvent.coverImg"
            class="detail-cover"
          >
            <img
              :src="currentEvent.coverImg"
              alt="活动封面"
              class="cover-img"
            >
          </div>

          <!-- 活动基础信息（布局优化） -->
          <EventMetaInfo :event="currentEvent" />

          <!-- 活动详情（样式优化） -->
          <div class="detail-content">
            <h4 class="content-title">
              活动详情
            </h4>
            <div class="content-text">
              {{ currentEvent.detail }}
            </div>
          </div>

          <!-- 活动流程（样式优化） -->
          <div
            v-if="currentEvent.schedule"
            class="detail-schedule"
          >
            <h4 class="content-title">
              活动流程
            </h4>
            <div class="schedule-list">
              <div 
                v-for="(item, idx) in currentEvent.schedule"
                :key="idx"
                class="schedule-item"
              >
                <div class="schedule-time">
                  {{ item.time }}
                </div>
                <div class="schedule-content">
                  {{ item.content }}
                </div>
              </div>
            </div>
          </div>

          <!-- 报名信息（样式优化） -->
          <div
            v-if="currentEvent.isRegistered"
            class="detail-reg"
          >
            <h4 class="content-title">
              我的报名信息
            </h4>
            <div class="reg-tip">
              <i class="fas fa-check-circle success" />
              您已成功报名此活动，请按时参与
            </div>
            <div class="reg-deadline">
              <i class="fas fa-clock" />
              报名截止时间：{{ currentEvent.formattedDeadline || '未设置' }}
            </div>
          </div>
        </div>

        <!-- 弹窗操作按钮（样式优化） -->
        <div class="modal-actions">
          <button
            class="btn ghost"
            @click="handleCloseDetail"
          >
            <i class="fas fa-arrow-left" /> 关闭
          </button>
          <EventRegButton
            :is-registered="currentEvent.isRegistered || false"
            :is-loading="isProcessing[currentEvent.id || '']"
            :is-disabled="isEventDisabled(currentEvent)"
            :disabled-tip="getDisabledTip(currentEvent)"
            size="default"
            reg-text="立即报名"
            cancel-text="取消报名"
            class="custom-reg-btn"
            @reg="handleRegister(currentEvent.id)"
            @cancel="handleCancelReg(currentEvent.id)"
          />
        </div>
      </div>
    </div>

    <!-- 我的报名列表弹窗（视觉全量升级） -->
    <div
      class="my-reg-modal"
      :class="{ active: showMyRegModal }"
    >
      <div
        class="modal-overlay"
        @click="handleCloseMyReg"
      />
      <div class="modal-panel">
        <div class="modal-header">
          <h3 class="modal-title">
            我的报名活动
          </h3>
          <button
            class="modal-close"
            @click="handleCloseMyReg"
          >
            <i class="fas fa-times" />
          </button>
        </div>
        <div class="modal-body">
          <div class="reg-tabs">
            <button
              class="tab-btn"
              :class="{ active: regTab === 'all' }"
              @click="handleRegTabChange('all')"
            >
              全部报名
            </button>
            <button
              class="tab-btn"
              :class="{ active: regTab === 'upcoming' }"
              @click="handleRegTabChange('upcoming')"
            >
              待参与
            </button>
            <button
              class="tab-btn"
              :class="{ active: regTab === 'ended' }"
              @click="handleRegTabChange('ended')"
            >
              已结束
            </button>
          </div>

          <div class="reg-list">
            <div
              v-for="event in filteredMyRegEvents"
              :key="event.id"
              class="reg-item"
              @click="handleViewEvent(event.id)"
            >
              <div
                v-if="event.coverImg"
                class="reg-img"
              >
                <!--OPTIMIZE:没有对图片路径进行安全验证-->
                <img
                  :src="event.coverImg"
                  alt="活动封面"
                  class="list-img"
                >
              </div>
              <div class="reg-info">
                <h4 class="reg-title">
                  {{ event.name }}
                </h4>
                <div class="reg-meta">
                  <span class="meta-item"><i class="fas fa-calendar" /> {{ event.formattedDate }}</span>
                  <span class="meta-item"><i class="fas fa-map-marker-alt" /> {{ event.location }}</span>
                  <span class="meta-item">
                    <EventStatusBadge
                      :status="event.status"
                      size="small"
                    />
                  </span>
                </div>
                <div class="reg-deadline">
                  <i class="fas fa-clock" />
                  报名截止：{{ event.formattedDeadline || '未设置' }}
                </div>
              </div>
              <!-- 报名列表中的取消按钮 -->
              <EventRegButton
                :is-registered="true"
                :is-loading="isProcessing[event.id]"
                :is-disabled="event.status === 'ended'"
                :disabled-tip="event.status === 'ended' ? '活动已结束' : ''"
                size="small"
                reg-text="立即报名"
                cancel-text="取消报名"
                class="custom-reg-btn small"
                @cancel="handleCancelReg(event.id)"
              />
            </div>

            <div
              v-if="filteredMyRegEvents.length === 0"
              class="empty-state small"
            >
              <div class="empty-icon-container">
                <i class="fas fa-calendar-check empty-icon" />
              </div>
              <!--TODO:加入报名活动相关内容-->
              <h4 class="empty-title">
                暂无报名记录
              </h4>
              <p class="empty-desc">
                浏览活动并报名，记录将显示在这里
              </p>
              <button
                class="empty-action-btn"
                @click="handleDiscoverEvents"
              >
                <i class="fas fa-explore" /> 去发现活动
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 活动创建弹窗 -->
    <div
      class="create-event-modal"
      :class="{ active: showCreateEventModal }"
    >
      <div
        class="modal-overlay"
        @click="handleCloseCreateEvent"
      />
      <div class="modal-panel">
        <div class="modal-header">
          <h3 class="modal-title">
            创建新活动
          </h3>
          <button
            class="modal-close"
            @click="handleCloseCreateEvent"
          >
            <i class="fas fa-times" />
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmitCreateEvent" class="create-event-form">
            <!-- 活动名称 -->
            <div class="form-group">
              <label class="form-label" for="eventName">
                活动名称 <span class="required">*</span>
              </label>
              <input
                id="eventName"
                v-model="newEvent.name"
                type="text"
                class="form-control"
                placeholder="请输入活动名称（1-100字符）"
                maxlength="100"
                required
              />
              <div class="form-help">
                {{ newEvent.name.length }}/100 字符
              </div>
            </div>

            <!-- 活动描述 -->
            <div class="form-group">
              <label class="form-label" for="eventDescription">
                活动描述 <span class="required">*</span>
              </label>
              <textarea
                id="eventDescription"
                v-model="newEvent.description"
                class="form-control"
                rows="4"
                placeholder="请输入活动描述"
                required
              />
            </div>

            <!-- 活动时间和地点 -->
            <div class="form-row">
              <div class="form-group half">
                <label class="form-label" for="eventDate">
                  活动时间 <span class="required">*</span>
                </label>
                <input
                  id="eventDate"
                  v-model="newEvent.date"
                  type="datetime-local"
                  class="form-control"
                  required
                />
              </div>
              <div class="form-group half">
                <label class="form-label" for="eventLocation">
                  活动地点 <span class="required">*</span>
                </label>
                <input
                  id="eventLocation"
                  v-model="newEvent.location"
                  type="text"
                  class="form-control"
                  placeholder="请输入活动地点"
                  required
                />
              </div>
            </div>

            <!-- 活动标签 -->
            <div class="form-group">
              <label class="form-label" for="eventTags">
                活动标签
              </label>
              <div class="tags-input-container">
                <div class="tags-list">
                  <span
                    v-for="(tag, index) in newEvent.tags"
                    :key="index"
                    class="tag-chip"
                  >
                    {{ tag }}
                    <button
                      type="button"
                      class="tag-remove"
                      @click="removeTag(index)"
                    >
                      <i class="fas fa-times" />
                    </button>
                  </span>
                </div>
                <input
                  v-model="tagInput"
                  type="text"
                  class="form-control tag-input"
                  placeholder="输入标签后按回车添加"
                  @keydown.enter.prevent="addTag"
                />
              </div>
              <div class="form-help">
                回车添加标签，如：音乐、运动、学习等
              </div>
            </div>

            <!-- 封面图片（可选） -->
            <div class="form-group">
              <label class="form-label">
                封面图片（可选）
              </label>
              <div class="file-upload-container">
                <input
                  ref="coverFileInput"
                  type="file"
                  class="file-input"
                  accept="image/*"
                  @change="handleCoverImageSelect"
                />
                <div
                  class="file-upload-btn"
                  @click="$refs.coverFileInput.click()"
                >
                  <i class="fas fa-cloud-upload-alt" />
                  <span>选择图片</span>
                </div>
              </div>
              <div v-if="newEvent.cover_img" class="cover-preview">
                <img
                  :src="newEvent.cover_img"
                  alt="封面预览"
                  class="cover-preview-img"
                />
                <button
                  type="button"
                  class="remove-cover-btn"
                  @click="removeCoverImage"
                >
                  <i class="fas fa-times" />
                </button>
              </div>
              <div class="form-help">
                支持 jpg、png、gif 等图片格式，建议大小不超过2MB
              </div>
            </div>
          </form>
        </div>
        <div class="modal-actions">
          <button
            type="button"
            class="btn ghost"
            @click="handleCloseCreateEvent"
          >
            <i class="fas fa-arrow-left" /> 取消
          </button>
          <button
            type="button"
            class="btn primary"
            :disabled="!isFormValidForNewEvent || isSubmitting"
            @click="handleSubmitCreateEvent"
          >
            <i class="fas fa-plus" />
            {{ isSubmitting ? '创建中...' : '创建活动' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  // 替换/新增所有 API 导入
  createEvent, // 新增：创建活动
  updateEvent, // 新增：更新活动
  deleteEvent, // 新增：删除活动
  getEventList, // 替换原 getCampusEvents
  getEventDetail, // 保持不变 (假设详情API名称仍为 getEventDetail)
  getMyRegisteredEvents, // 保持不变
  registerForEvent, // 替换原 registerEvent
  cancelEventRegistration // 替换原 cancelRegister
} from '@/api/new/EventsApi.js'
import AppHeader from '@/components/AppHeader.vue'
import CapsuleCard from '@/components/CapsuleCard.vue'
import EventRegButton from '@/components/EventRegButton.vue'
import EventStatusBadge from '@/components/EventStatusBadge.vue'
import RegStatsCard from '@/components/RegStatsCard.vue'
import { formatRelative, formatStandard } from '@/utils/formatTime.js'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import EventMetaInfo from '../components/EventMetaInfo.vue'

// 路由实例
const router = useRouter()

// 原始数据
const eventsList = ref([])
const myRegEvents = ref([])
const totalEvents = ref(0)

// 筛选条件
const filter = ref({
  status: 'all',
  startTime: new Date(new Date().setMonth(new Date().getMonth() - 3)).toISOString().split('T')[0],
  endTime: new Date().toISOString().split('T')[0],
  sort: 'time',
  search: ''
})

// 视图与分页
const viewMode = ref('grid')
const currentPage = ref(1)
const pageSize = ref(10)

// 弹窗状态
const showDetailModal = ref(false)
const currentEvent = ref({})
const showMyRegModal = ref(false)
const showCreateModal = ref(false)
const regTab = ref('all')
const showCreateEventModal = ref(false)

// 活动创建表单数据
const newEvent = ref({
  name: '',
  description: '',
  date: '',
  location: '',
  tags: [],
  cover_img: ''
})

// 标签输入
const tagInput = ref('')

// 创建状态
const isSubmitting = ref(false)

// 文件上传相关
const coverFileInput = ref(null)

// 创建活动相关数据
const createEventData = ref({
  name: '',
  description: '',
  date: '',
  location: '',
  tags: [],
  cover_img: '',
  registerDeadline: '',
  tempTagInput: ''
})

// 表单验证
const formErrors = ref({
  name: '',
  description: '',
  date: '',
  location: ''
})

// 表单状态
const isSubmittingForm = ref(false)
const showAlert = ref(false)
const alertText = ref('')
const alertType = ref('success')
const alertIcon = ref('fas fa-check-circle')

// 图片预览
const previewImage = ref('')
const imageLinkInputRef = ref(null)

// 标签管理
const selectedTags = ref([])
const suggestedTags = ref(['校园活动', '毕业季', '文化节', '体育赛事', '学术讲座', '社团活动', '志愿者', '招聘会'])

// 计算属性 - 表单是否有效（用于createEventData）
const isFormValidForData = computed(() => {
  return createEventData.value.name.trim() &&
         createEventData.value.date &&
         createEventData.value.location.trim() &&
         !formErrors.value.name &&
         !formErrors.value.date &&
         !formErrors.value.location
})

// 计算属性 - 表单是否有效（用于newEvent）
const isFormValidForNewEvent = computed(() => {
  return (
    newEvent.value.name.trim().length >= 1 &&
    newEvent.value.name.trim().length <= 100 &&
    newEvent.value.description.trim().length >= 1 &&
    newEvent.value.date !== '' &&
    newEvent.value.location.trim().length >= 1
  )
})

// 加载状态
const isLoading = ref(false)
// OPTIMIZE: 需要确保在所有可能的错误路径中都正确重置loading状态
const isProcessing = ref({})

// 静态数据
// OPTIMIZE: 热门标签列表可考虑从后端获取
const hotTags = ref(['毕业季', '文化节', '校友分享', '体育比赛', '讲座', '社团活动'])

// 计算属性 - 修复：简化筛选逻辑，主要依赖后端筛选
const filteredEvents = computed(() => {
  // 如果后端已经返回筛选后的数据，直接使用
  if (!eventsList.value || eventsList.value.length === 0) return []
  
  // 前端只做简单的搜索筛选，其他筛选交给后端
  // OPTIMIZE: 可能需要添加搜索防抖机制，避免频繁请求
  const keyword = filter.value.search.toLowerCase()
  if (!keyword) return eventsList.value
  
  return eventsList.value.filter(event => {
    if (!event) return false
    
    return (event.name || '').toLowerCase().includes(keyword) ||
           (event.organizer || '').toLowerCase().includes(keyword) ||
           (event.desc || '').toLowerCase().includes(keyword) ||
           ((event.tags || []).some(tag => (tag || '').toLowerCase().includes(keyword)))
  })
})

// 统计计算
const myRegCount = computed(() => {
  return myRegEvents.value?.length || 0
})

const upcomingRegCount = computed(() => {
  return myRegEvents.value?.filter(event => event?.status === 'upcoming').length || 0
})

const endedRegCount = computed(() => {
  return myRegEvents.value?.filter(event => event?.status === 'ended').length || 0
})

const filteredMyRegEvents = computed(() => {
  if (!myRegEvents.value || myRegEvents.value.length === 0) return []
  
  switch (regTab.value) {
  case 'upcoming': 
    return myRegEvents.value.filter(e => e?.status === 'upcoming')
  case 'ended': 
    return myRegEvents.value.filter(e => e?.status === 'ended')
  default: 
    return myRegEvents.value
  }
})

const isDeadlinePassed = computed(() => {
  if (!currentEvent.value?.registerDeadline) return false
  return new Date(currentEvent.value.registerDeadline) < new Date()
})

// 表单验证
const isFormValid = computed(() => {
  return (
    newEvent.value.name.trim().length >= 1 &&
    newEvent.value.name.trim().length <= 100 &&
    newEvent.value.description.trim().length >= 1 &&
    newEvent.value.date !== '' &&
    newEvent.value.location.trim().length >= 1
  )
})

const totalPages = computed(() => {
  if (totalEvents.value === 0 || pageSize.value === 0) return 0
  return Math.ceil(totalEvents.value / pageSize.value)
})

const pageInfo = computed(() => {
  if (totalEvents.value === 0) {
    return '暂无活动'
  } else if (totalPages.value === 1) {
    return `共 ${totalEvents.value} 个活动`
  } else {
    return `第 ${currentPage.value} 页 / 共 ${totalPages.value} 页（共 ${totalEvents.value} 个活动）`
  }
})
// 页面初始化
onMounted(async() => {
  await Promise.all([fetchEventsList(), fetchMyRegEvents()])
})

// API调用方法 - 修复：适配后端数据结构
// 统一的事件数据处理函数
const processEventData = (event) => {
  if (!event) return {}
  
  return {
    ...event,
    // 格式化时间字段
    formattedDate: formatStandard(event.date),
    relativeDate: formatRelative(event.date),
    formattedCreatedAt: formatRelative(event.created_at),
    formattedUpdatedAt: formatRelative(event.updated_at),
    formattedDeadline: event.registerDeadline ? formatStandard(event.registerDeadline) : '未设置',
    
    // 设置默认值
    tags: event.tags || [],
    participant_count: event.participant_count || 0,
    cover_img: event.cover_img || '/default-cover.jpg',
    is_registered: event.is_registered || false,
    
    // 兼容前端其他组件可能需要的字段
    name: event.name || '未命名活动',
    description: event.description || '暂无描述',
    location: event.location || '地点待定'
  }
}
// 统一的API响应数据处理函数
const processApiResponse = (result) => {
  let list = []
  let total = 0

  console.log('processApiResponse 输入:', result)

  // 处理后端BaseResponse格式: { code, message, data: { list, total, page, page_size } }
  if (result && typeof result === 'object') {
    // 优先处理后端的标准响应格式
    if (result.data && typeof result.data === 'object') {
      // 后端返回的BaseResponse[data]格式
      if (result.data.list && Array.isArray(result.data.list)) {
        list = result.data.list || []
        total = result.data.total || list.length
      } else if (result.data.data && Array.isArray(result.data.data)) {
        // 嵌套一层的情况
        list = result.data.data || []
        total = result.data.total || list.length
      } else if (Array.isArray(result.data)) {
        // data直接是数组
        list = result.data || []
        total = result.total || list.length
      }
    }
    // 处理直接包含records的情况
    else if (result.records && Array.isArray(result.records)) {
      list = result.records || []
      total = result.total || list.length
    }
    // 处理直接包含list的情况
    else if (result.list && Array.isArray(result.list)) {
      list = result.list || []
      total = result.total || list.length
    }
    // 处理直接是数组的情况
    else if (Array.isArray(result)) {
      list = result
      total = result.length
    }
    // 如果是单个对象，也包装成数组
    else if (result.id || result.name) {
      list = [result]
      total = 1
    }
  }

  console.log('processApiResponse 输出:', { list, total })
  return { list, total }
}

/**
 * 1. 使用新的 getEventList API 获取活动列表
 */
const fetchEventsList = async () => {
  isLoading.value = true
  try {
    console.log('🚀 [fetchEventsList] 开始获取活动列表，参数:', {
      page: currentPage.value,
      size: pageSize.value,
      keyword: filter.value.search,
      status: filter.value.status,
      sort: filter.value.sort,
      startTime: filter.value.startTime,
      endTime: filter.value.endTime
    })

    const result = await getEventList({ // <--- 使用新的 API 函数
      page: currentPage.value,
      size: pageSize.value,
      keyword: filter.value.search,
      status: filter.value.status,
      sort: filter.value.sort,
      startTime: filter.value.startTime,
      endTime: filter.value.endTime
    })

    console.log('📥 [fetchEventsList] API返回原始结果:', result)

    const { list, total } = processApiResponse(result)

    console.log('📋 [fetchEventsList] 处理后的数据:', { list, total })

    eventsList.value = list.map(processEventData)
    totalEvents.value = total

    console.log('✅ [fetchEventsList] 最终eventsList:', eventsList.value)
    console.log('📊 [fetchEventsList] 总数:', totalEvents.value)

  } catch (error) {
    console.error('❌ [fetchEventsList] 加载活动列表失败：', error)
    eventsList.value = []
    totalEvents.value = 0
  } finally {
    isLoading.value = false
  }
}

/**
 * 2. 使用 getMyRegisteredEvents API 获取我的报名列表 (保持不变)
 */
const fetchMyRegEvents = async () => {
  try {
    console.log('🚀 [fetchMyRegEvents] 开始获取我的报名列表，参数:', {
      page: currentPage.value,
      size: pageSize.value
    })

    const result = await getMyRegisteredEvents({
      page: currentPage.value,
      size: pageSize.value
    })

    console.log('📥 [fetchMyRegEvents] API返回原始结果:', result)

    const { list } = processApiResponse(result)

    console.log('📋 [fetchMyRegEvents] 处理后的数据:', { list })

    myRegEvents.value = list.map(processEventData)

    console.log('✅ [fetchMyRegEvents] 最终myRegEvents:', myRegEvents.value)

  } catch (error) {
    console.error('❌ [fetchMyRegEvents] 加载我的报名列表失败：', error)
    myRegEvents.value = []
  }
}


// 辅助函数
const adaptEventToCapsule = (event) => {
  if (!event) return {}
  
  // 严格按照 CapsuleCard 组件的接口要求映射字段
  return {
    id: event.id || '',
    title: event.name || '未命名活动',
    time: event.date || new Date().toISOString(), // 使用原始的 ISO 时间字符串
    vis: 'public', // 活动默认都是公开的
    desc: event.description || '暂无描述',
    tags: event.tags || [],
    likes: event.participant_count || 0, // 使用参与人数作为点赞数
    views: (event.participant_count || 0) * 2, // 模拟浏览数
    location: event.location || '地点待定',
    img: event.cover_img || '' // 封面图片
    // 注意：不要传递额外的字段如 eventStatus, isRegistered, registerDeadline
    // 这些字段 CapsuleCard 组件不识别，会被忽略
  }
}
const isEventDisabled = (event) => {
  if (!event) return true
  // OPTIMIZE: 缺少对"进行中"但已超过报名截止时间的活动状态判断
  return event.status === 'ended' || new Date(event.registerDeadline) < new Date()
}

const getDisabledTip = (event) => {
  if (!event) return ''
  if (event.status === 'ended') return '活动已结束'
  if (new Date(event.registerDeadline) < new Date()) return '报名已截止'
  return ''
}

// 顶部导航相关方法
const handleGoHub = () => {
  router.push({ name: 'HubViews' })
}

const handleSearch = (keyword) => {
  filter.value.search = keyword
  currentPage.value = 1
  fetchEventsList() // 重新从后端获取数据
}

/**
 * 5. 使用 createEvent API 创建活动
 */
const handleCreateEvent = () => {
  console.log('🎯 [handleCreateEvent] 按钮被点击了!')
  try {
    // 打开活动创建弹窗
    showCreateEventModal.value = true
    console.log('✅ [handleCreateEvent] 弹窗状态已设置为:', showCreateEventModal.value)
  } catch (error) {
    console.error('❌ [handleCreateEvent] 创建活动出错:', error)
  }
}

// 关闭创建活动弹窗
const handleCloseCreateEvent = () => {
  showCreateEventModal.value = false
  resetCreateForm()
}

// 重置创建表单
const resetCreateForm = () => {
  newEvent.value = {
    name: '',
    description: '',
    date: '',
    location: '',
    tags: [],
    cover_img: ''
  }
  tagInput.value = ''
  // 重置文件输入
  if (coverFileInput.value) {
    coverFileInput.value.value = ''
  }
}

// 处理封面图片选择
const handleCoverImageSelect = (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 检查文件类型
  if (!file.type.startsWith('image/')) {
    alert('请选择图片文件')
    return
  }

  // 检查文件大小 (限制2MB)
  if (file.size > 2 * 1024 * 1024) {
    alert('图片大小不能超过2MB')
    return
  }

  // 读取文件并转换为base64或上传到服务器
  const reader = new FileReader()
  reader.onload = (e) => {
    newEvent.value.cover_img = e.target.result
    console.log('📷 图片读取成功:', file.name)
  }
  reader.onerror = () => {
    alert('图片读取失败，请重试')
  }
  reader.readAsDataURL(file)
}

// 移除封面图片
const removeCoverImage = () => {
  newEvent.value.cover_img = ''
  if (coverFileInput.value) {
    coverFileInput.value.value = ''
  }
}

// 添加标签
const addTag = () => {
  const tag = tagInput.value.trim()
  if (tag && !newEvent.value.tags.includes(tag) && newEvent.value.tags.length < 10) {
    newEvent.value.tags.push(tag)
    tagInput.value = ''
  }
}

// 移除标签
const removeTag = (index) => {
  newEvent.value.tags.splice(index, 1)
}

// 格式化日期为后端API兼容格式
const formatDateForAPI = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const pad = (num) => num.toString().padStart(2, '0')
  const year = date.getFullYear()
  const month = pad(date.getMonth() + 1)
  const day = pad(date.getDate())
  const hours = pad(date.getHours())
  const minutes = pad(date.getMinutes())
  const seconds = pad(date.getSeconds())
  const ms = date.getMilliseconds().toString().padStart(3, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}.${ms}+08:00`
}

// 提交创建活动表单
const handleSubmitCreateEvent = async () => {
  if (!isFormValidForNewEvent.value || isSubmitting.value) return

  // 检查用户是否已登录
  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('请先登录后再创建活动')
    return
  }

  isSubmitting.value = true

  try {
    console.log('🚀 [handleSubmitCreateEvent] 开始创建活动')

    const eventData = {
      name: newEvent.value.name.trim(),
      description: newEvent.value.description.trim(),
      date: formatDateForAPI(newEvent.value.date),
      location: newEvent.value.location.trim(),
      tags: newEvent.value.tags,
      ...(newEvent.value.cover_img.trim() && { cover_img: newEvent.value.cover_img.trim() })
    }

    console.log('📤 [handleSubmitCreateEvent] 发送创建请求:', eventData)

    const result = await createEvent(eventData)
    console.log('📥 [handleSubmitCreateEvent] 创建API返回:', result)

    // 创建成功
    alert(`活动创建成功! ID: ${result.id}`)
    handleCloseCreateEvent()
    await fetchEventsList() // 刷新列表

  } catch (error) {
    console.error('❌ [handleSubmitCreateEvent] 活动创建失败：', error)

    // 打印详细的422错误信息
    console.error('❌ [handleSubmitCreateEvent] 完整错误对象:', error)
    console.error('❌ [handleSubmitCreateEvent] error.data:', error.data)
    console.error('❌ [handleSubmitCreateEvent] error.fullResponse:', error.fullResponse)

    if (error.data && error.data.detail && Array.isArray(error.data.detail)) {
      console.error('❌ [handleSubmitCreateEvent] 详细验证错误:', error.data.detail)
      error.data.detail.forEach((validationError, index) => {
        console.error(`  验证错误 ${index + 1}:`, validationError)
        console.error(`    - type: ${validationError.type}`)
        console.error(`    - loc: ${JSON.stringify(validationError.loc)}`)
        console.error(`    - msg: ${validationError.msg}`)
        console.error(`    - input: ${JSON.stringify(validationError.input)}`)
      })

      // 显示具体验证错误
      const errorMessages = error.data.detail.map(err =>
        `${err.loc?.join('.') || '字段'}: ${err.msg}`
      ).join('\n')
      alert(`创建失败，请检查以下信息：\n${errorMessages}`)
    } else {
      alert(error.message || '活动创建失败，请检查数据或权限。')
    }
  } finally {
    isSubmitting.value = false
  }
}

const handleHeaderAction = (key) => {
  console.log('🎯 [handleHeaderAction] 按键被点击:', key)
  console.log('🎯 [handleHeaderAction] 按键类型:', typeof key)
  console.log('🎯 [handleHeaderAction] 调用栈:', new Error().stack)

  try {
    switch (key) {
    case 'create':
      console.log('🎯 [handleHeaderAction] 调用 handleCreateEvent')
      handleCreateEvent();
      break
    case 'myReg':
      console.log('🎯 [handleHeaderAction] 调用 handleShowMyReg')
      handleShowMyReg();
      break
    case 'refresh':
      console.log('🎯 [handleHeaderAction] 刷新页面')
      currentPage.value = 1
      filter.value.search = ''
      fetchEventsList()
      break
    default:
      console.warn('🎯 [handleHeaderAction] 未知按键:', key)
    }
  } catch (error) {
    console.error('🎯 [handleHeaderAction] 处理按键时出错:', error)
  }
}

// 筛选与视图相关方法
const handleFilterChange = () => {
  currentPage.value = 1
  fetchEventsList() // 所有筛选都重新从后端获取
}

const resetDateFilter = () => {
  filter.value.startTime = new Date(new Date().setMonth(new Date().getMonth() - 3)).toISOString().split('T')[0]
  filter.value.endTime = new Date().toISOString().split('T')[0]
  filter.value.search = ''
  filter.value.status = 'all'
  currentPage.value = 1
  fetchEventsList()
}

const handleFilterByTag = (tag) => {
  filter.value.search = tag
  currentPage.value = 1
  fetchEventsList()
}

const handleViewMode = (mode) => {
  viewMode.value = mode
}

// 分页相关方法
const handlePageChange = async(page) => {
  currentPage.value = page
  await fetchEventsList()
}

// 活动详情相关方法
const handleViewEvent = async(eventId) => {
  if (!eventId) return

  isLoading.value = true
  try {
    console.log('🚀 [handleViewEvent] 开始获取活动详情:', eventId)
    const event = await getEventDetail(eventId)
    console.log('📥 [handleViewEvent] 活动详情API返回:', event)

    // 使用统一的事件数据处理函数
    currentEvent.value = processEventData(event)
    showDetailModal.value = true

    console.log('✅ [handleViewEvent] 处理后的活动详情:', currentEvent.value)

  } catch (error) {
    console.error(`❌ [handleViewEvent] 查看活动(${eventId})详情失败：`, error)
    alert(error.message || '获取活动详情失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

const handleCloseDetail = () => {
  showDetailModal.value = false
  currentEvent.value = {}
}

// 报名/取消报名相关方法
/**
 * 3. 使用 registerForEvent API 报名活动
 */
const handleRegister = async(eventId) => {
  if (!eventId) return

  isProcessing.value[eventId] = true
  try {
    console.log('🚀 [handleRegister] 开始报名活动:', eventId)
    const result = await registerForEvent(eventId) // <--- 使用新的 API 函数
    console.log('📥 [handleRegister] 报名API返回:', result)

    // axios拦截器已经处理了成功的情况，直接走到这里就是成功
    alert('报名成功！')
    await Promise.all([fetchEventsList(), fetchMyRegEvents()])

  } catch (error) {
    console.error(`❌ [handleRegister] 报名活动(${eventId})失败：`, error)
    alert(error.message || '报名失败，请稍后重试')
  } finally {
    isProcessing.value[eventId] = false
  }
}

/**
 * 4. 使用 cancelEventRegistration API 取消报名活动
 */
const handleCancelReg = async(eventId) => {
  if (!eventId) return

  isProcessing.value[eventId] = true
  try {
    console.log('🚀 [handleCancelReg] 开始取消报名活动:', eventId)
    const result = await cancelEventRegistration(eventId) // <--- 使用新的 API 函数
    console.log('📥 [handleCancelReg] 取消报名API返回:', result)

    // axios拦截器已经处理了成功的情况，直接走到这里就是成功
    alert('取消报名成功！')
    await Promise.all([fetchEventsList(), fetchMyRegEvents()])

  } catch (error) {
    console.error(`❌ [handleCancelReg] 取消活动(${eventId})报名失败：`, error)
    alert(error.message || '取消报名失败，请稍后重试')
  } finally {
    isProcessing.value[eventId] = false
  }
}

// 我的报名列表相关方法
const handleShowMyReg = () => {
  showMyRegModal.value = true
}

const handleCloseMyReg = () => {
  showMyRegModal.value = false
}

const handleRegTabChange = (tab) => {
  regTab.value = tab
}

const handleClickRegTab = (tab) => {
  regTab.value = tab
  handleShowMyReg()
}

// “去发现活动”按钮点击处理，重定向到活动列表并关闭弹窗
const handleDiscoverEvents = () => {
  handleCloseMyReg()
  resetDateFilter()
  // 可选：滚动到页面顶部，确保用户看到活动列表
  window.scrollTo({ top: 0, behavior: 'smooth' })
}


// --- 新增的 API 占位函数 (用于未来集成) ---

/**
 * 6. 使用 updateEvent API 更新活动 (目前仅为占位函数)
 */
const handleUpdateEvent = async(eventId, data) => {
    if (!eventId) return
    console.log(`尝试更新活动 ${eventId} 的数据...`, data)
    try {
        // const result = await updateEvent(eventId, data) // <--- 使用新的 API 函数
        // if (result?.success) {
        //     alert('活动更新成功!')
        //     await fetchEventsList()
        // } else {
        //     alert('活动更新失败')
        // }
        console.warn('handleUpdateEvent 尚未完全实现，请在需要时调用 updateEvent API。')
    } catch (error) {
        console.error(`更新活动(${eventId})失败：`, error)
    }
}

/**
 * 7. 使用 deleteEvent API 删除活动 (目前仅为占位函数)
 */
const handleDeleteEvent = async(eventId) => {
    if (!eventId) return
    if (!confirm(`确定要删除活动 ${eventId} 吗?`)) return
    
    try {
        // const result = await deleteEvent(eventId) // <--- 使用新的 API 函数
        // if (result?.success) {
        //     alert('活动删除成功!')
        //     await fetchEventsList()
        // } else {
        //     alert('活动删除失败')
        // }
        console.warn('handleDeleteEvent 尚未完全实现，请在需要时调用 deleteEvent API。')
    } catch (error) {
        console.error(`删除活动(${eventId})失败：`, error)
    }
}

// 表单验证函数
const validateField = (field) => {
  formErrors.value[field] = ''

  if (field === 'name') {
    if (!createEventData.value.name.trim()) {
      formErrors.value.name = '活动名称不能为空'
    } else if (createEventData.value.name.length > 50) {
      formErrors.value.name = '活动名称不能超过50个字符'
    }
  }

  if (field === 'description') {
    if (createEventData.value.description.length > 1000) {
      formErrors.value.description = '活动描述不能超过1000个字符'
    }
  }

  if (field === 'date') {
    if (!createEventData.value.date) {
      formErrors.value.date = '活动时间不能为空'
    }
  }

  if (field === 'location') {
    if (!createEventData.value.location.trim()) {
      formErrors.value.location = '活动地点不能为空'
    } else if (createEventData.value.location.length > 200) {
      formErrors.value.location = '活动地点不能超过200个字符'
    }
  }
}

// 处理创建活动相关函数
const handleCreateEventFormSubmit = async () => {
  // 验证表单
  validateField('name')
  validateField('description')
  validateField('date')
  validateField('location')

  // 检查是否有错误
  const hasErrors = Object.values(formErrors.value).some(error => error !== '')
  if (hasErrors) {
    showAlertMessage('请检查表单中的错误', 'error')
    return
  }

  // 检查必填字段
  if (!createEventData.value.name.trim() || !createEventData.value.date || !createEventData.value.location.trim()) {
    showAlertMessage('请填写所有必填字段', 'error')
    return
  }

  isSubmittingForm.value = true

  try {
    // 调用API创建活动
    const eventData = {
      ...createEventData.value,
      tags: selectedTags.value // 使用selectedTags而不是createEventData.value.tags
    }

    const result = await createEvent(eventData)
    if (result) {
      showAlertMessage('活动创建成功！', 'success')
      // 延迟关闭模态框，让用户看到成功消息
      setTimeout(() => {
        // 重置表单
        resetCreateFormForData()
        // 关闭弹窗
        showCreateModal.value = false
        // 刷新活动列表
        fetchEventsList()
      }, 1500)
    } else {
      showAlertMessage('活动创建失败', 'error')
    }
  } catch (error) {
    console.error('创建活动失败：', error)
    showAlertMessage(error.message || '活动创建失败，请稍后重试', 'error')
  } finally {
    isSubmittingForm.value = false
  }
}

const handleCloseCreateModal = () => {
  showCreateModal.value = false
  resetCreateFormForData()
}

// 显示提示信息
const showAlertMessage = (message, type = 'error') => {
  alertText.value = message
  alertType.value = type
  alertIcon.value = type === 'success' ? 'fas fa-check-circle' :
    type === 'warning' ? 'fas fa-exclamation-triangle' : 'fas fa-exclamation-circle'
  showAlert.value = true

  setTimeout(() => {
    showAlert.value = false
  }, 5000)
}

// 触发图片链接输入框
const triggerImageLinkInput = () => {
  imageLinkInputRef.value?.focus()
}

// 更新图片预览
const updatePreviewImage = () => {
  const url = createEventData.value.cover_img
  if (url && (url.startsWith('http://') || url.startsWith('https://'))) {
    previewImage.value = url
  } else {
    previewImage.value = ''
  }
}

// 移除图片
const removeImage = () => {
  createEventData.value.cover_img = ''
  previewImage.value = ''
}

// 处理标签输入
const handleTagInput = (event) => {
  if (event.key === 'Enter') {
    event.preventDefault()
    addTagForData(createEventData.value.tempTagInput.trim())
  }
}

// 添加标签
const addTagForData = (tag) => {
  if (!tag) return

  if (selectedTags.value.length >= 5) {
    showAlertMessage('最多只能添加5个标签', 'error')
    return
  }

  if (selectedTags.value.includes(tag)) {
    showAlertMessage('标签已存在', 'error')
    return
  }

  selectedTags.value.push(tag)
  createEventData.value.tempTagInput = ''
}

// 移除标签
const removeTagForData = (index) => {
  selectedTags.value.splice(index, 1)
}

// 添加推荐标签
const addSuggestedTag = (tag) => {
  if (selectedTags.value.length < 5 && !selectedTags.value.includes(tag)) {
    selectedTags.value.push(tag)
  }
}

const resetCreateFormForData = () => {
  createEventData.value = {
    name: '',
    description: '',
    date: '',
    location: '',
    tags: [],
    cover_img: '',
    registerDeadline: '',
    tempTagInput: ''
  }
  selectedTags.value = []
  formErrors.value = {
    name: '',
    description: '',
    date: '',
    location: ''
  }
  previewImage.value = ''
  isSubmittingForm.value = false
  showAlert.value = false
  alertText.value = ''
  alertType.value = 'success'
  alertIcon.value = 'fas fa-check-circle'
}

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
.custom-capsule-card {
  border-radius: 20px !important;
  overflow: hidden;
  box-shadow: 0 6px 20px rgba(149, 157, 165, 0.08) !important;
  border: 1px solid rgba(230, 236, 240, 0.6) !important;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
  background: white !important;
}

.custom-capsule-card:hover {
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

/* 弹窗系统（全量视觉升级） */
.event-detail-modal, .my-reg-modal {
  position: fixed;
  inset: 0;
  display: none;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.event-detail-modal.active, .my-reg-modal.active {
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

.modal-panel {
  position: relative;
  width: 850px;
  max-width: 95%;
  max-height: 90vh;
  overflow-y: auto;
  background: white;
  border-radius: 24px;
  padding: 30px;
  box-shadow: 0 20px 60px rgba(17, 24, 39, 0.15);
  z-index: 1001;
  border: 1px solid rgba(230, 236, 240, 0.8);
  transform: translateY(30px) scale(0.96);
  opacity: 0;
  animation: panelSlideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* 弹窗滚动条美化 */
.modal-panel::-webkit-scrollbar {
  width: 6px;
}

.modal-panel::-webkit-scrollbar-track {
  background: rgba(230, 236, 240, 0.3);
  border-radius: 3px;
}

.modal-panel::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
}

.modal-panel::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

/* 弹窗头部（样式升级） */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 26px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(230, 236, 240, 0.6);
}

.modal-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #2d3748;
  line-height: 1.3;
}

.modal-close {
  background: transparent;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #a0aec0;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-close:hover {
  background: rgba(66, 153, 225, 0.1);
  color: #4299e1;
  transform: rotate(90deg);
}

/* 详情封面（样式升级） */
.detail-cover {
  width: 100%;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(149, 157, 165, 0.1);
  margin-bottom: 26px;
  position: relative;
}

.cover-img {
  width: 100%;
  height: auto;
  max-height: 400px;
  object-fit: cover;
  transition: all 0.5s ease;
}

.detail-cover:hover .cover-img {
  transform: scale(1.02);
}

/* 详情元信息（布局优化） */
.detail-meta {
  background: linear-gradient(135deg, #f8f9fa 0%, #f5f5f5 100%);
  padding: 24px;
  border-radius: 16px;
  margin-bottom: 26px;
  border: 1px solid rgba(230, 236, 240, 0.6);
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-tags {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-label {
  font-size: 14px;
  color: #718096;
  font-weight: 500;
}

.meta-value {
  font-size: 15px;
  color: #2d3748;
  font-weight: 400;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  line-height: 1.5;
}

.org-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(149, 157, 165, 0.15);
}

/* 标签样式（全量升级） */
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
  margin: 0 8px 12px 0;
  white-space: nowrap;
  display: inline-block;
}

.tag-item:hover {
  background: #4299e1;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.2);
}

/* 详情内容（样式升级） */
.detail-content {
  margin-bottom: 26px;
}

.content-title {
  font-size: 20px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.content-title::before {
  content: '';
  width: 4px;
  height: 20px;
  background: #4299e1;
  border-radius: 2px;
}

.content-text {
  font-size: 16px;
  color: #4a5568;
  line-height: 1.8;
  white-space: pre-line;
  background: rgba(248, 249, 250, 0.8);
  padding: 20px;
  border-radius: 14px;
  border: 1px solid rgba(230, 236, 240, 0.4);
}

/* 活动流程（样式升级） */
.detail-schedule {
  margin-bottom: 26px;
}

.schedule-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: rgba(248, 249, 250, 0.8);
  padding: 20px;
  border-radius: 14px;
  border: 1px solid rgba(230, 236, 240, 0.4);
}

.schedule-item {
  display: flex;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(230, 236, 240, 0.4);
}

.schedule-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.schedule-time {
  min-width: 100px;
  font-size: 15px;
  font-weight: 600;
  color: #4299e1;
  background: rgba(66, 153, 225, 0.1);
  padding: 8px 14px;
  border-radius: 10px;
  text-align: center;
}

.schedule-content {
  font-size: 15px;
  color: #4a5568;
  line-height: 1.6;
  flex: 1;
}

/* 报名信息（样式升级） */
.detail-reg {
  background: linear-gradient(135deg, #f0f8fb 0%, #e8f4f8 100%);
  padding: 20px;
  border-radius: 14px;
  border: 1px solid rgba(66, 153, 225, 0.15);
  margin-bottom: 26px;
}

.reg-tip {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  color: #2d3748;
  font-weight: 500;
  margin-bottom: 12px;
}

.reg-tip .success {
  color: #48bb78;
  font-size: 20px;
}

.reg-deadline {
  font-size: 14px;
  color: #718096;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 我的报名列表（样式升级） */
.reg-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 26px;
  background: linear-gradient(135deg, #f8f9fa 0%, #f5f5f5 100%);
  padding: 10px;
  border-radius: 16px;
  border: 1px solid rgba(230, 236, 240, 0.6);
}

.tab-btn {
  background: transparent;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 16px;
  color: #718096;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  flex: 1;
  font-weight: 500;
  position: relative;
  overflow: hidden;
}

.tab-btn::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: #4299e1;
  transform: scaleX(0);
  transition: transform 0.3s ease;
  border-radius: 3px;
}

.tab-btn.active {
  background: white;
  color: #4299e1;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(149, 157, 165, 0.08);
}

.tab-btn.active::after {
  transform: scaleX(1);
}

.tab-btn:hover:not(.active) {
  color: #4299e1;
  background: rgba(66, 153, 225, 0.05);
}

.reg-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.reg-item {
  display: flex;
  gap: 20px;
  padding: 20px;
  background: white;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid rgba(230, 236, 240, 0.6);
  align-items: center;
}

.reg-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(149, 157, 165, 0.08);
  border-color: rgba(66, 153, 225, 0.2);
}

.reg-img {
  width: 100px;
  height: 100px;
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(149, 157, 165, 0.08);
}

.list-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.reg-item:hover .list-img {
  transform: scale(1.08);
}

.reg-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reg-title {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  line-height: 1.4;
}

.reg-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #718096;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.reg-deadline {
  font-size: 13px;
  color: #a0aec0;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
}

/* 活动创建弹窗样式 */
.create-event-modal {
  position: fixed;
  inset: 0;
  display: none;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.create-event-modal.active {
  display: flex;
  align-items: center;
  justify-content: center;
  animation: modalFadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.create-event-form {
  max-height: 60vh;
  overflow-y: auto;
  padding: 10px 0;
}

/* 表单布局 */
.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.form-row .form-group {
  margin-bottom: 0;
}

.form-row .form-group.half {
  flex: 1;
}

/* 表单控件升级 */
.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #2d3748;
  font-weight: 600;
}

.form-label .required {
  color: #e53e3e;
  margin-left: 2px;
}

.form-control {
  width: 100%;
  padding: 12px 16px;
  border-radius: 14px;
  border: 2px solid #e2e8f0;
  background: white;
  font-size: 15px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  color: #2d3748;
  font-weight: 400;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 4px rgba(66, 153, 225, 0.1);
  transform: translateY(-1px);
}

.form-control:invalid {
  border-color: #e53e3e;
}

textarea.form-control {
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
}

/* 表单帮助文本 */
.form-help {
  margin-top: 6px;
  font-size: 12px;
  color: #718096;
  line-height: 1.4;
}

/* 文件上传样式 */
.file-upload-container {
  position: relative;
  width: 100%;
}

.file-input {
  display: none;
}

.file-upload-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px 20px;
  border: 2px dashed #cbd5e0;
  border-radius: 14px;
  background: rgba(66, 153, 225, 0.02);
  color: #718096;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.file-upload-btn:hover {
  border-color: #4299e1;
  background: rgba(66, 153, 225, 0.05);
  color: #4299e1;
  transform: translateY(-2px);
}

.file-upload-btn i {
  font-size: 20px;
}

/* 封面预览样式 */
.cover-preview {
  position: relative;
  margin-top: 12px;
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.cover-preview-img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
}

.remove-cover-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(237, 100, 166, 0.9);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  font-size: 12px;
}

.remove-cover-btn:hover {
  background: rgba(237, 100, 166, 1);
  transform: scale(1.1);
}

/* 标签输入样式 */
.tags-input-container {
  border: 2px solid #e2e8f0;
  border-radius: 14px;
  padding: 8px;
  background: white;
  transition: all 0.3s ease;
}

.tags-input-container:focus-within {
  border-color: #4299e1;
  box-shadow: 0 0 0 4px rgba(66, 153, 225, 0.1);
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(66, 153, 225, 0.1);
  color: #4299e1;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.tag-remove {
  background: none;
  border: none;
  color: #4299e1;
  cursor: pointer;
  padding: 2px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.tag-remove:hover {
  background: rgba(66, 153, 225, 0.2);
}

.tag-input {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  padding: 4px 8px !important;
  background: transparent !important;
}

/* 按钮系统（全量升级） */
.btn {
  padding: 14px 26px;
  border-radius: 16px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  font-size: 15px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.btn.primary {
  background: linear-gradient(90deg, #4299e1, #38b2ac);
  color: white;
  box-shadow: 0 6px 16px rgba(66, 153, 225, 0.2);
  border: 1px solid transparent;
}

.btn.primary:hover {
  background: linear-gradient(90deg, #3182ce, #319795);
  box-shadow: 0 8px 20px rgba(66, 153, 225, 0.25);
  transform: translateY(-3px);
}

.btn.ghost {
  background: transparent;
  color: #4299e1;
  border: 1px solid #e2e8f0;
}

.btn.ghost:hover {
  background: rgba(66, 153, 225, 0.05);
  border-color: #4299e1;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.1);
}
.btn.small {
  padding: 10px 18px;
  font-size: 14px;
  border-radius: 12px;
}

/* 弹窗操作按钮（布局优化） */
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding-top: 20px;
  margin-top: 10px;
  border-top: 1px solid rgba(230, 236, 240, 0.6);
}
/* 创建活动弹窗样式（与胶囊表单保持一致） */
.create-event-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
  display: none;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

.create-event-modal.active {
  display: flex;
  align-items: center;
  justify-content: center;
  animation: modalFadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.create-event-overlay {
  position: absolute;
  inset: 0;
  background: rgba(17, 24, 39, 0.6);
  backdrop-filter: blur(6px);
  transition: all 0.4s ease;
  opacity: 0;
  animation: overlayFadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.create-event-panel {
  position: relative;
  width: 680px;
  max-width: 95%;
  max-height: 90vh;
  overflow-y: auto;
  background: white;
  border-radius: 24px;
  padding: 30px;
  box-shadow: 0 20px 60px rgba(17, 24, 39, 0.15);
  z-index: 1001;
  border: 1px solid rgba(230, 236, 240, 0.8);
  transform: translateY(30px) scale(0.96);
  opacity: 0;
  animation: panelSlideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  /* 为新样式覆盖原有的通用样式 */
}

.create-event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 26px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(230, 236, 240, 0.6);
}

.create-event-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #2d3748;
  line-height: 1.3;
}

.create-event-close {
  background: transparent;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #a0aec0;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.create-event-close:hover {
  background: rgba(66, 153, 225, 0.1);
  color: #4299e1;
  transform: rotate(90deg);
}

.create-event-content {
  flex: 1;
  overflow-y: auto;
}

/* 表单样式 */
.capsule-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 表单提示信息 */
.form-alert {
  padding: 14px 18px;
  border-radius: 14px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  font-size: 15px;
  font-weight: 500;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.form-alert::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 4px;
}

.form-alert.success {
  background: rgba(72, 187, 120, 0.1);
  color: #2f855a;
  border: 1px solid rgba(72, 187, 120, 0.2);
}

.form-alert.success::before {
  background: #48bb78;
}

.form-alert.error {
  background: rgba(229, 62, 62, 0.1);
  color: #c53030;
  border: 1px solid rgba(229, 62, 62, 0.2);
}

.form-alert.error::before {
  background: #e53e3e;
}

.form-alert.warning {
  background: rgba(251, 191, 36, 0.1);
  color: #d69e2e;
  border: 1px solid rgba(251, 191, 36, 0.2);
}

.form-alert.warning::before {
  background: #f6e05e;
}

.alert-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.alert-icon {
  font-size: 20px;
}

.alert-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: inherit;
  padding: 4px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.alert-close:hover {
  background: rgba(0, 0, 0, 0.05);
  transform: scale(1.1);
}

/* 表单部分 */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.datetime-format-hint {
  font-size: 13px;
  color: #a0aec0;
  font-style: italic;
}

.section-icon {
  color: #4299e1;
  font-size: 18px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.required-badge {
  background: rgba(229, 62, 62, 0.1);
  color: #c53030;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.optional-badge {
  background: rgba(166, 176, 187, 0.1);
  color: #718096;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.form-input {
  padding: 14px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  font-size: 16px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  background: white;
  color: #2d3748;
  font-weight: 400;
}

.form-input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 4px rgba(66, 153, 225, 0.1);
  transform: translateY(-1px);
}

.form-input.input-error {
  border-color: #e53e3e;
  box-shadow: 0 0 0 4px rgba(229, 62, 62, 0.1);
}

.form-textarea {
  padding: 14px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  font-size: 16px;
  font-family: inherit;
  resize: vertical;
  min-height: 120px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  background: white;
  color: #2d3748;
}

.form-textarea:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 4px rgba(66, 153, 225, 0.1);
  transform: translateY(-1px);
}

.form-textarea.input-error {
  border-color: #e53e3e;
  box-shadow: 0 0 0 4px rgba(229, 62, 62, 0.1);
}

.form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #718096;
  margin-top: 6px;
}

.char-count {
  font-size: 13px;
}

.error-text {
  color: #e53e3e;
  font-weight: 500;
}

/* 上传区域 */
.upload-area {
  border: 2px dashed #e2e8f0;
  border-radius: 16px;
  padding: 32px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  background: #f8fafc;
  position: relative;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: #a0aec0;
}

.upload-area.has-image {
  border-color: #4299e1;
  background: rgba(66, 153, 225, 0.02);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.upload-icon {
  font-size: 36px;
  color: #a0aec0;
}

.upload-text {
  font-size: 18px;
  font-weight: 500;
  color: #4a5568;
  margin: 0;
}

.upload-hint {
  font-size: 14px;
  color: #a0aec0;
  margin: 0;
}

.link-input {
  width: 100%;
  max-width: 400px;
  margin-top: 12px;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  font-size: 15px;
}

.image-preview {
  position: relative;
  width: 100%;
  height: 200px;
  border-radius: 14px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.3s ease;
}

.remove-image:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: scale(1.1);
}

/* 标签部分 */
.tags-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tags-input-wrapper {
  position: relative;
}

.tags-input {
  padding: 14px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  font-size: 16px;
  width: 100%;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.tags-input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 4px rgba(66, 153, 225, 0.1);
  transform: translateY(-1px);
}

.tags-count {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 13px;
  color: #a0aec0;
  background: white;
  padding: 2px 6px;
  border-radius: 10px;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.tag-item {
  background: rgba(66, 153, 225, 0.1);
  color: #4299e1;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  border: 1px solid transparent;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.remove-tag {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.remove-tag:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.suggested-tags {
  margin-top: 12px;
}

.suggested-label {
  font-size: 14px;
  color: #718096;
  font-weight: 500;
  margin-right: 12px;
}

.suggested-tag {
  background: rgba(26, 138, 152, 0.08);
  color: #2c7a8f;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: inline-block;
  margin-right: 8px;
  margin-bottom: 8px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid transparent;
}

.suggested-tag:hover {
  background: #38b2ac;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(56, 178, 172, 0.2);
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding-top: 24px;
  margin-top: 8px;
  border-top: 1px solid rgba(230, 236, 240, 0.6);
}

.btn {
  padding: 14px 26px;
  border-radius: 16px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  font-size: 15px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  text-decoration: none;
  position: relative;
  overflow: hidden;
  border: 1px solid;
}

.btn-primary {
  background: linear-gradient(90deg, #4299e1, #3182ce);
  color: white;
  border-color: #4299e1;
  box-shadow: 0 6px 16px rgba(66, 153, 225, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(90deg, #3182ce, #2c5aae);
  border-color: #3182ce;
  box-shadow: 0 8px 20px rgba(66, 153, 225, 0.35);
  transform: translateY(-3px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.btn-secondary {
  background: white;
  color: #4a5568;
  border-color: #e2e8f0;
}

.btn-secondary:hover:not(:disabled) {
  background: #f7fafc;
  color: #2d3748;
  border-color: #cbd5e0;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
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

  .modal-panel {
    padding: 24px 20px;
    border-radius: 20px;
    max-height: 92vh;
  }

  .modal-header {
    margin-bottom: 20px;
    padding-bottom: 16px;
  }

  .modal-title {
    font-size: 20px;
  }

  .detail-cover {
    margin-bottom: 20px;
    border-radius: 12px;
  }

  .detail-meta {
    padding: 20px;
    margin-bottom: 20px;
  }

  .reg-tabs {
    flex-direction: column;
    gap: 8px;
    margin-bottom: 20px;
  }

  .tab-btn {
    padding: 10px 16px;
    font-size: 15px;
  }

  .reg-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .reg-img {
    width: 100%;
    height: 160px;
  }

  .reg-meta {
    flex-wrap: wrap;
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

  .content-title {
    font-size: 18px;
  }

  .content-text {
    font-size: 15px;
    padding: 16px;
  }

  .schedule-item {
    flex-direction: column;
    gap: 8px;
  }

  .schedule-time {
    min-width: auto;
    width: 100%;
  }

  .modal-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    padding: 12px 20px;
  }
}
</style>