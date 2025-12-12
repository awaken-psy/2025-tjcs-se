<template>
  <!-- 中央中枢页：项目核心枢纽，整合所有功能入口，支持快速跳转与数据预览 -->
  <div class="hub-page">
    <!-- 顶部导航（复用共用组件） -->
    <AppHeader
      page-title="时光胶囊 · 校园"
      :page-subtitle="`欢迎回来，${userInfo.name} | 系统已为你准备当日推荐`"
      :show-search="true"
      search-placeholder="搜索地点/标签/用户，例如：图书馆、毕业季..."
      :actions="[
        { key: 'create', text: '快速创建', icon: '✚', type: 'primary' },
        { 
          key: 'notif', 
          text: '通知', 
          icon: '🔔', 
          type: 'ghost', 
          badge: { count: userInfo.stats?.pendingCapsules || 0, color: '#f59e0b' } 
        },
        { key: 'user', text: '我的主页', icon: '👤', type: 'ghost' }
      ]"
      @go-hub="handleGoHub"
      @search="handleSearch"
      @action-click="handleHeaderAction"
    />

    <!-- 主体内容：侧边导航 + 主内容区 -->
    <div class="hub-main">
      <!-- 侧边导航（复用共用组件） -->
      <Sidebar
        :nav-items="[
          { 
            key: 'hub', 
            label: '中枢', 
            icon: '🏠', 
            badge: { count: userInfo.stats?.pendingCapsules || 0, color: '#f59e0b' } 
          },
          { key: 'map', label: '地图', icon: '🗺️' },
          { key: 'create', label: '创建胶囊', icon: '✚' },
          { key: 'myCapsule', label: '我的胶囊', icon: '👤' },
          { key: 'events', label: '校园活动', icon: '🎪' },
          { key: 'logout', label: isLogoutLoading ? '注销中...' : '注销', icon: '🔐', disabled: isLogoutLoading }
        ]"
        current-active="hub"
        tip-text="提示：点击「创建胶囊」可前往编辑页，或使用右上角的快速创建"
        @nav-change="handleNavChange"
      />

      <!-- 主内容区：数据统计 + 功能模块 -->
      <div class="hub-content">
        <!-- 1. 数据统计卡片（复用共用组件） -->
        <div class="stats-grid">
          <StatsCard
            title="总胶囊数"
            value="1,248"
            trend="+12% 较上月"
            trend-type="up"
            icon="📦"
          />
          <StatsCard
            title="待审核"
            :value="userInfo.stats?.pendingCapsules || 0"
            trend="-2 较昨日"
            trend-type="down"
            icon="⏳"
          />
          <StatsCard
            title="注册用户"
            value="856"
            trend="+5% 较上周"
            trend-type="up"
            icon="👥"
          />
          <StatsCard
            title="今日活跃"
            :value="userInfo.stats?.activeToday || 0"
            trend="+8% 较昨日"
            trend-type="up"
            icon="🔥"
          />
        </div>

        <!-- 2. 欢迎卡片（个性化推荐） -->
        <div class="welcome-card">
          <div class="welcome-art">
            <div class="art-icon">
              校园
            </div>
          </div>
          <div class="welcome-content">
            <h3 class="welcome-title">
              你好，{{ userInfo.name }} 👋
            </h3>
            <p class="welcome-desc">
              {{ userInfo.bio || '你可以从这里快速进入地图、创建胶囊或查看附近的惊喜。系统已为你准备好当日推荐与附近解锁提示。' }}
            </p>
            <div class="welcome-actions">
              <button 
                class="btn primary" 
                @click="handleNavChange('map')"
              >
                前往地图
              </button>
              <button 
                class="btn ghost" 
                @click="showCapsuleForm = true"
              >
                创建胶囊
              </button>
            </div>
          </div>
        </div>

        <!-- 3. 本周主题活动（CTA横幅） -->
        <div class="cta-banner">
          <div class="cta-content">
            <h4 class="cta-title">
              本周主题：毕业季回忆征集
            </h4>
            <p class="cta-desc">
              为毕业生与校友准备的专题活动，投稿将有机会出现在校庆展示中，还有限定徽章可拿～
            </p>
          </div>
          <div class="cta-actions">
            <button 
              class="btn ghost" 
              @click="handleNavChange('events')"
            >
              查看活动
            </button>
            <button 
              class="btn primary"
              @click="handleNavChange('events')"
            >
              立即投稿
            </button>
          </div>
        </div>

        <!-- 4. 附近胶囊列表（复用胶囊卡片组件） -->
        <div class="card-module">
          <div class="module-header">
            <h3 class="module-title">
              附近的胶囊
            </h3>
            <p class="module-subtitle">
              显示离你最近的{{ nearbyCapsules.length }}个胶囊
            </p>
          </div>
          <div class="capsule-list">
            <CapsuleCard
              v-for="capsule in nearbyCapsules"
              :key="capsule.id"
              :capsule="capsule"
              view-mode="list"
              @view="handleViewCapsule"
              @like="handleLikeCapsule"
            />
          </div>
        </div>

        <!-- 5. 校园活动轮播 -->
        <div class="card-module">
          <div class="module-header">
            <h3 class="module-title">
              校园活动
            </h3>
            <button 
              class="btn ghost small" 
              @click="handleNavChange('events')"
            >
              查看全部
            </button>
          </div>
          <div class="events-carousel">
            <div 
              v-for="event in campusEvents"
              :key="event.id"
              class="event-card"
              @click="handleViewEvent(event.id)"
            >
              <img 
                :src="event.coverImg" 
                :alt="event.name"
                class="event-cover"
              >
              <div class="event-info">
                <h4 class="event-name">
                  {{ event.name }}
                </h4>
                <p class="event-date">
                  {{ formatStandard(event.date) }}
                </p>
                <p class="event-desc">
                  {{ event.desc }}
                </p>
                <div class="event-tags">
                  <span 
                    v-for="(tag, idx) in event.tags"
                    :key="idx"
                    class="event-tag"
                  >
                    {{ tag }}
                  </span>
                </div>
                <div class="event-participant">
                  <i class="fas fa-users" />
                  {{ event.participantCount }} 人已报名
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 6. 最近动态 -->
        <div class="card-module">
          <div class="module-header">
            <h3 class="module-title">
              最近动态
            </h3>
            <button class="btn ghost small">
              查看全部
            </button>
          </div>
          <div class="activities-list">
            <div 
              v-for="activity in recentActivities"
              :key="activity.id"
              class="activity-item"
              @click="handleViewRelated(activity.relatedId)"
            >
              <img 
                :src="activity.userAvatar" 
                :alt="activity.user"
                class="activity-avatar"
              >
              <div class="activity-content">
                <p class="activity-text">
                  <span class="activity-user">{{ activity.user }}</span>
                  <span class="activity-action">{{ activity.action }}</span>
                  <span class="activity-details">{{ activity.details }}</span>
                </p>
                <p class="activity-time">
                  {{ formatRelative(activity.time) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <CapsuleForm
    :is-show="showCapsuleForm"
    @close="showCapsuleForm = false"
    @success="onCapsuleCreated"
  />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import CapsuleForm from '@/components/CapsuleForm.vue'
const showCapsuleForm = ref(false)
const onCapsuleCreated = () => {
  showCapsuleForm.value = false
  // 可选：刷新数据等
}
import { useRouter } from 'vue-router'
import { routeJump } from '@/utils/routeUtils'
import { formatStandard, formatRelative } from '@/utils/formatTime.js'
// 复用共用组件
import AppHeader from '@/components/AppHeader.vue'
import Sidebar from '@/components/Sidebar.vue'
import CapsuleCard from '@/components/CapsuleCard.vue'
import StatsCard from '@/components/StatsCard.vue'
// 引入页面专属API

import {
  getUserInfo,
  getNearbyCapsules,
  getCampusEvents,
  getRecentActivities
} from '@/api/new/hubApi.js'
// 引入认证API
import { logout } from '@/api/new/authenticationApi'
// 引入用户状态
import { useUserStore } from '@/store/user'

/**
 * 页面作用：
 * 1. 项目核心枢纽，整合所有功能入口（地图、创建胶囊等）
 * 2. 展示用户个性化数据（附近胶囊、待审核数、个人统计）
 * 3. 提供活动推荐、主题征集等运营入口，提升用户参与度
 * 
 * 依赖API：
 * 1. getUserInfo() - 获取用户基础信息与统计数据
 * 2. getNearbyCapsules() - 获取附近胶囊列表（需用户位置）
 * 3. getCampusEvents() - 获取校园活动列表
 * 4. getRecentActivities() - 获取用户最近动态
 * 
 * 页面状态：
 * - userInfo：用户信息（头像、昵称、统计等）
 * - nearbyCapsules：附近胶囊列表
 * - campusEvents：校园活动列表
 * - recentActivities：最近动态列表
 */

const router = useRouter()
const userInfo = ref({})
const nearbyCapsules = ref([])
const campusEvents = ref([])
const recentActivities = ref([])
// 新增：页面状态控制
const isPageActive = ref(true)
const isLoading = ref(false)
// 注销加载状态
const isLogoutLoading = ref(false)

/**
 * 页面初始化：加载所有依赖数据
 */
onMounted(async() => {
  // 登录校验：未登录则跳转到登录页
  // 🔴 修正：使用 'access_token' 或 'refresh_token' 进行校验
  const token = localStorage.getItem('access_token') // <--- 更改为 access_token
  if (!token) {
    router.replace({ path: '/login', query: { from: 'hub' } }) 
    return
  }
  
  // 仅在有 Token 时才加载数据
  await loadPageData()
})

/**
 * 加载页面数据
 */
const loadPageData = async () => {
  if (!isPageActive.value) return
  
  isLoading.value = true
  try {
    // 每次都主动向后端拉取用户信息，并同步到localStorage
    const userData = await getUserInfo()
    if (!isPageActive.value) return
    
    localStorage.setItem('user_info', JSON.stringify(userData))
    
    // 使用Promise.allSettled而不是Promise.all，避免一个失败影响全部
    const [nearbyResult, eventsResult, activitiesResult] = await Promise.allSettled([
      getNearbyCapsules(),
      getCampusEvents(),
      getRecentActivities()
    ])
    
    if (!isPageActive.value) return
    
    // 处理各个请求结果
    userInfo.value = userData
    
    if (nearbyResult.status === 'fulfilled') {
      nearbyCapsules.value = nearbyResult.value
    } else {
      console.warn('获取附近胶囊失败:', nearbyResult.reason)
      nearbyCapsules.value = getFallbackCapsules()
    }
    
    if (eventsResult.status === 'fulfilled') {
      campusEvents.value = eventsResult.value
    } else {
      console.warn('获取校园活动失败:', eventsResult.reason)
      campusEvents.value = getFallbackEvents()
    }
    
    if (activitiesResult.status === 'fulfilled') {
      recentActivities.value = activitiesResult.value
    } else {
      console.warn('获取最近动态失败:', activitiesResult.reason)
      recentActivities.value = getFallbackActivities()
    }
    
  } catch (error) {
    if (!isPageActive.value) return
    console.error('中枢页初始化失败：', error)
    // 极端错误降级：确保页面至少显示基础结构
    setFallbackData()
  } finally {
    if (isPageActive.value) {
      isLoading.value = false
    }
  }
}

/**
 * 设置降级数据
 */
const setFallbackData = () => {
  userInfo.value = { 
    name: '校园用户', 
    bio: '用时光胶囊记录校园回忆',
    stats: {
      pendingCapsules: 0,
      activeToday: 0
    }
  }
  nearbyCapsules.value = getFallbackCapsules()
  campusEvents.value = getFallbackEvents()
  recentActivities.value = getFallbackActivities()
}

/**
 * 获取降级胶囊数据
 */
const getFallbackCapsules = () => {
  return [{
    id: 'c_default', 
    title: '校园初印象', 
    time: new Date().toISOString(), 
    vis: 'public', 
    desc: '第一次踏入校园的心情', 
    tags: ['校园'], 
    likes: 0, 
    views: 0, 
    location: '学校大门', 
    distance: '50m', 
    img: 'https://picsum.photos/id/1018/300/200'
  }]
}

/**
 * 获取降级活动数据
 */
const getFallbackEvents = () => {
  return [{
    id: 'event_default',
    name: '校园迎新活动',
    date: new Date().toISOString(),
    desc: '欢迎新同学加入校园大家庭',
    tags: ['迎新', '活动'],
    participantCount: 120,
    coverImg: 'https://picsum.photos/id/1025/300/200'
  }]
}

/**
 * 获取降级动态数据
 */
const getFallbackActivities = () => {
  return [{
    id: 'act_default',
    user: '系统',
    userAvatar: 'https://picsum.photos/id/64/40/40',
    action: '发布了',
    details: '校园迎新活动',
    time: new Date().toISOString(),
    relatedId: 'event_default'
  }]
}

/**
 * 页面卸载时标记
 */
onUnmounted(() => {
  isPageActive.value = false
})

/**
 * 顶部导航：点击品牌区域，刷新当前页面（中枢页）
 */
const handleGoHub = () => {
  if (!isPageActive.value) return
  routeJump('/hubviews')
}

/**
 * 顶部导航：搜索功能（后续可扩展为全局搜索）
 * @param {String} keyword - 搜索关键词
 */
const handleSearch = (keyword) => {
  if (!isPageActive.value) return
  alert(`正在搜索：${keyword}（后续可对接全局搜索接口）`)
}

/**
 * 顶部导航：功能按钮点击（创建胶囊、通知、我的主页）
 * @param {String} key - 按钮唯一标识
 */
const handleHeaderAction = (key) => {
  if (!isPageActive.value) return
  
  switch (key) {
  case 'create':
    showCapsuleForm.value = true
    break
  case 'notif':
    alert('查看通知（后续可对接通知接口）')
    break
  case 'user':
    routeJump('/my-capsule')
    break
  }
}

/**
 * 侧边导航：导航项切换（跳转对应页面）
 * @param {String} key - 导航项唯一标识
 */
const handleNavChange = async (key) => {
  if (!isPageActive.value) return
  
  const routeMap = {
    hub: '/hubviews',
    map: '/map',
    myCapsule: '/my-capsule',
    events: '/events',
    logout: '/login'
  }
  
  if (key === 'logout') {
    // 使用logout API实现注销
    await handleLogout()
    return
  }
  
  if (key === 'map') {
    routeJump('/map')
    return
  }
  
  if (key === 'create') {
    showCapsuleForm.value = true
    return
  }
  
  routeJump(routeMap[key] || '/hubviews')
}

/**
 * 注销处理函数
 */
const handleLogout = async () => {
  // 防止重复点击
  if (isLogoutLoading.value) return
  
  // 标记注销加载状态
  isLogoutLoading.value = true

  try {
    // 调用logout API通知后端清除会话
    await logout()
    console.log('注销API调用成功')

  } catch (error) {
    console.error('注销API调用失败:', error)
    // 即使API调用失败，也要继续执行清理逻辑
  } finally {
    // 清理所有本地存储数据和 Pinia 状态
    const keysToRemove = [
      'user_token', 
      'user_info', 
      'access_token', 
      'refresh_token', 
      'saved_login_email'
    ]
    keysToRemove.forEach(key => {
      localStorage.removeItem(key)
    })
    localStorage.removeItem('user-store')
    // 彻底清空 Pinia 用户状态
    const userStore = useUserStore()
    userStore.logout()
    // 重置加载状态
    isLogoutLoading.value = false

    // 立即跳转到登录页
    router.replace({ 
      path: '/login', 
      query: { from: 'logout' } 
    })
  }
}

/**
 * 胶囊卡片：查看胶囊详情
 * @param {String} capsuleId - 胶囊ID
 */
const handleViewCapsule = (capsuleId) => {
  if (!isPageActive.value) return
  alert(`查看胶囊详情：${capsuleId}（后续对接胶囊详情页）`)
}

/**
 * 胶囊卡片：点赞胶囊
 * @param {String} capsuleId - 胶囊ID
 */
const handleLikeCapsule = (capsuleId) => {
  if (!isPageActive.value) return
  // 前端临时更新点赞数（后续对接点赞接口）
  const capsule = nearbyCapsules.value.find(c => c.id === capsuleId)
  if (capsule) {
    capsule.likes = (capsule.likes || 0) + 1
  }
}

/**
 * 校园活动：查看活动详情
 * @param {String} eventId - 活动ID
 */
const handleViewEvent = (eventId) => {
  if (!isPageActive.value) return
  alert(`查看活动详情：${eventId}（后续对接活动详情页）`)
}

/**
 * 最近动态：查看关联内容（胶囊/活动）
 * @param {String} relatedId - 关联内容ID（胶囊ID/活动ID）
 */
const handleViewRelated = (relatedId) => {
  if (!isPageActive.value) return
  if (!relatedId) return
  if (relatedId.startsWith('c_')) {
    handleViewCapsule(relatedId)
  } else if (relatedId.startsWith('event_')) {
    handleViewEvent(relatedId)
  }
}
</script>

<style scoped>
/* 页面整体样式：统一使用全局设计令牌，确保风格一致 */
.hub-page {
  background-color: var(--bg);
  min-height: 100vh;
}

/* 主体内容布局 */
.hub-main {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 20px;
  padding: 20px;
}

/* 主内容区容器 */
.hub-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

/* 欢迎卡片样式 */
.welcome-card {
  background: var(--card);
  border-radius: var(--radius);
  padding: 24px;
  box-shadow: var(--shadow);
  display: flex;
  gap: 20px;
  align-items: center;
}

.welcome-art {
  width: 180px;
  height: 120px;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, #f0f4ff, #e8f0ff);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent);
  font-weight: 700;
  font-size: 24px;
  box-shadow: 0 8px 20px rgba(108, 140, 255, 0.1);
}

.welcome-content {
  flex: 1;
}

.welcome-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.welcome-desc {
  color: var(--muted);
  line-height: 1.5;
  margin-bottom: 16px;
}

.welcome-actions {
  display: flex;
  gap: 12px;
}

/* CTA横幅样式 */
.cta-banner {
  background: linear-gradient(90deg, rgba(108, 140, 255, 0.08), rgba(255, 138, 101, 0.04));
  border-radius: var(--radius);
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(108, 140, 255, 0.1);
}

.cta-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 6px;
}

.cta-desc {
  color: var(--muted);
  max-width: 500px;
}

.cta-actions {
  display: flex;
  gap: 12px;
}

/* 模块通用样式（胶囊列表、活动轮播、动态列表） */
.card-module {
  background: var(--card);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.module-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.module-subtitle {
  font-size: 13px;
  color: var(--muted);
  margin: 0;
}

/* 胶囊列表样式（列表视图） */
.capsule-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 活动轮播样式 */
.events-carousel {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 8px;
  scrollbar-width: thin;
}

.events-carousel::-webkit-scrollbar {
  height: 6px;
}

.events-carousel::-webkit-scrollbar-thumb {
  background: rgba(108, 140, 255, 0.2);
  border-radius: 3px;
}

.event-card {
  min-width: 280px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: #f8fafc;
  box-shadow: var(--shadow);
  transition: transform 0.2s;
  cursor: pointer;
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.event-cover {
  width: 100%;
  height: 140px;
  object-fit: cover;
}

.event-info {
  padding: 12px;
}

.event-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.event-date {
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 8px;
}

.event-desc {
  font-size: 13px;
  color: #374151;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
  margin-bottom: 8px;
}

.event-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.event-tag {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 4px;
  background: var(--accent-light);
  color: var(--accent);
}

.event-participant {
  font-size: 12px;
  color: var(--muted);
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 最近动态样式 */
.activities-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: var(--radius-sm);
  transition: background 0.2s;
  cursor: pointer;
}

.activity-item:hover {
  background: var(--accent-light);
}

.activity-avatar {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  object-fit: cover;
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-size: 14px;
  line-height: 1.5;
}

.activity-user {
  font-weight: 600;
  color: #1e293b;
}

.activity-action {
  color: var(--accent);
  margin: 0 4px;
}

.activity-details {
  color: var(--muted);
}

.activity-time {
  font-size: 12px;
  color: var(--muted);
  margin-top: 4px;
}

/* 按钮通用样式（复用全局设计） */
.btn {
  background: var(--accent);
  color: white;
  padding: 10px 16px;
  border-radius: var(--radius-sm);
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 14px;
}

.btn:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
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

.btn.small {
  padding: 6px 12px;
  font-size: 13px;
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

/* 响应式适配 */
@media (max-width: 1024px) {
  .hub-main {
    grid-template-columns: 1fr;
  }
  
  .welcome-card {
    flex-direction: column;
    text-align: center;
  }
  
  .welcome-actions {
    justify-content: center;
  }
  
  .cta-banner {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .cta-actions {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .event-card {
    min-width: 100%;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .module-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>