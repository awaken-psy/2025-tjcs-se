<template>
  <div class="user-view-page">
    <AppHeader
      page-title="个人中心"
      page-subtitle="查看与管理你的个人档案与账户信息"
      :show-search="false"
      :actions="[
        { key: 'edit', text: '编辑资料', icon: '✎', type: 'primary' },
        { key: 'logout', text: '退出登录', icon: '🚪', type: 'ghost' }
      ]"
      @go-hub="handleGoHub"
      @action-click="handleHeaderAction" 
    />

    <div class="user-view-main">
      
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
          { key: 'events', label: '校园活动', icon: '🎪' },
          { key:'user', label:'个人中心', icon:'👤' },
          {
            key: 'logout',
            label: isLogoutLoading ? '注销中...' : '注销',
            icon: '🔐',
            disabled: isLogoutLoading,
          },
        ]"
        current-active="user"
        tip-text="欢迎来到个人中心"
        @nav-change="handleNavChange" />

      <main class="content-area">
        
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>正在拉取用户信息...</p>
        </div>

        <div v-else class="profile-card">
          <div class="profile-cover"></div>
          
          <div class="profile-body">
            <div class="profile-header">
              <div class="avatar-wrapper">
                <img :src="userInfo.avatar" alt="用户头像" class="avatar" />
              </div>
              <div class="base-info">
                <h2 class="username">{{ userInfo.nickname }}</h2>
                <p class="user-id">ID: {{ userInfo.uid }}</p>
                <div class="user-badges">
                  <span v-for="role in userInfo.roles" :key="role" class="badge">{{ role }}</span>
                </div>
              </div>
            </div>

            <div class="info-section">
              <h3>个人简介</h3>
              <p class="bio-text">{{ userInfo.bio || '这个人很懒，什么都没有写...' }}</p>
            </div>

            <div class="stats-row">
              <div class="stat-item">
                <div class="stat-num">{{ userInfo.stats.capsules }}</div>
                <div class="stat-label">胶囊总数</div>
              </div>
              <div class="stat-item">
                <div class="stat-num">{{ userInfo.stats.days }}</div>
                <div class="stat-label">加入天数</div>
              </div>
              <div class="stat-item">
                <div class="stat-num">{{ userInfo.stats.friends }}</div>
                <div class="stat-label">好友</div>
              </div>
            </div>

            <hr class="divider" />

            <div class="detail-list">
              <div class="detail-item">
                <span class="label">📧 邮箱地址</span>
                <span class="value">{{ userInfo.email }}</span>
              </div>
              <div class="detail-item">
                <span class="label">📱 手机号码</span>
                <span class="value">{{ userInfo.phone }}</span>
              </div>
              <div class="detail-item">
                <span class="label">📍 所在地区</span>
                <span class="value">{{ userInfo.location }}</span>
              </div>
              <div class="detail-item">
                <span class="label">📅 注册时间</span>
                <span class="value">{{ userInfo.joinDate }}</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '@/components/AppHeader.vue' 
import Sidebar from '@/components/Sidebar.vue'     
import { useRouter } from 'vue-router'

// --- 状态定义 ---
const loading = ref(true)
const userInfo = ref({})

const router = useRouter()

// 侧边栏菜单配置 (保持与 MyCapsuleView 一致，但可以高亮 'profile')
const navItems = [
  { key: 'profile', label: '个人资料', icon: '👤', badge: null }, // 当前页
  { key: 'myCapsule', label: '我的胶囊', icon: '💊' },
  { key: 'hub', label: '中枢', icon: '🏠' },
  { key: 'map', label: '地图', icon: '🗺️' },
  { key: 'setting', label: '设置', icon: '⚙️' },
]

// --- 模拟 API ---
// 你可以在这里替换为真实的 axios/fetch 请求
const mockFetchUserInfo = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        uid: 'user_9527',
        nickname: '时光旅行者',
        avatar: 'https://api.dicebear.com/7.x/adventurer/svg?seed=Felix', // 随机头像API
        bio: '热爱记录生活，喜欢摄影和复古风格的设计。正在寻找埋藏在2015年的那颗胶囊。',
        email: 'time.traveler@example.com',
        phone: '138****0000',
        location: '中国 · 上海',
        joinDate: '2023-01-15',
        roles: ['胶囊体验官', 'Pro会员'],
        stats: {
          capsules: 42,
          days: 365,
          friends: 12
        }
      })
    }, 800) // 模拟 0.8秒 网络延迟
  })
}

// --- 生命周期 ---
onMounted(async () => {
  try {
    loading.value = true
    // 调用模拟接口
    const data = await mockFetchUserInfo()
    userInfo.value = data
  } catch (error) {
    console.error('获取用户信息失败', error)
  } finally {
    loading.value = false
  }
})

// #region 侧边栏和顶部处理
// --- 事件处理 ---
const handleGoHub = () => {
  router.push('/hubviews')
}

const handleHeaderAction = (key) => {
  if (key === 'edit') {
    console.log('点击编辑资料')
      // 这里可以弹窗或跳转到编辑页
    //TODO: 实现编辑资料功能
  } else if (key === 'logout') {
    handleLogout()
  }
}

const handleNavChange = async (key) => {
  const routeMap = {
    myCapsule: '/my-capsule',
    hub: '/hubviews',
    map: '/map',
    create: '/capsules',
    timeline: '/timeline',
    events: '/events',
    logout: '/logout',
    user: '/user',
  }

  if (key === 'create') {
    handleOpenCreateForm()
    return
  }

  if (key === 'logout') {
    // 使用logout API实现注销
    await handleLogout()
    return
  }

  router.push(routeMap[key])
}

// #region logout逻辑
const isLogoutLoading = ref(false)

// 注销处理函数
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
      'saved_login_email',
    ]
    keysToRemove.forEach((key) => {
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
      query: { from: 'logout' },
    })
  }
}
// #endregion
// #endregion
</script>

<style scoped>
/* 复用 MyCapsuleView 的基础变量 
  注意：如果你的项目中没有全局定义 CSS 变量，请确保在这里定义或在 main.css 中定义
*/
.user-view-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f8fafc; /* 浅灰背景 */
}

.user-view-main {
  display: flex; /* 关键：让 Sidebar 和 Content 并排 */
  flex: 1;
  overflow: hidden; /* 防止整个页面滚动，只让内容区滚动 */
}

/* 内容区域样式 */
.content-area {
  flex: 1;
  padding: 30px;
  overflow-y: auto; /* 内容过长时滚动 */
  display: flex;
  justify-content: center; /* 卡片居中 */
  align-items: flex-start;
}

/* --- 加载状态 --- */
.loading-state {
  margin-top: 100px;
  text-align: center;
  color: var(--muted, #64748b);
}

/* --- 个人信息卡片组件样式 --- */
.profile-card {
  width: 100%;
  max-width: 800px; /* 限制最大宽度 */
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.02);
}

/* 顶部封面图 */
.profile-cover {
  height: 160px;
  background: linear-gradient(135deg, #6c8cff 0%, #809eff 100%); /* 这里的颜色使用了你的主题色 */
  opacity: 0.9;
}

.profile-body {
  padding: 0 40px 40px;
  position: relative;
}

/* 头像区域 */
.profile-header {
  display: flex;
  align-items: flex-end;
  margin-bottom: 25px;
  margin-top: -50px; /* 让头像上浮，盖住封面图 */
  gap: 20px;
}

.avatar-wrapper {
  padding: 4px;
  background: white;
  border-radius: 50%;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: #eee;
  display: block;
}

.base-info {
  padding-bottom: 10px; /* 对齐微调 */
}

.username {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.user-id {
  font-size: 14px;
  color: #94a3b8;
  margin: 4px 0 8px;
}

.user-badges {
  display: flex;
  gap: 8px;
}

.badge {
  background: #eff6ff;
  color: #6c8cff; /* Accent Color */
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
}

/* 简介部分 */
.info-section h3 {
  font-size: 16px;
  color: #334155;
  margin-bottom: 10px;
}

.bio-text {
  color: #64748b;
  line-height: 1.6;
  font-size: 15px;
  background: #f8fafc;
  padding: 15px;
  border-radius: 8px;
  margin: 0;
}

/* 统计数据 */
.stats-row {
  display: flex;
  justify-content: space-around;
  margin: 30px 0;
  text-align: center;
}

.stat-num {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 4px;
}

.divider {
  border: none;
  border-top: 1px solid #f1f5f9;
  margin: 20px 0;
}

/* 详细列表 */
.detail-list {
  display: grid;
  grid-template-columns: 1fr 1fr; /* 两列布局 */
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-item .label {
  font-size: 12px;
  color: #94a3b8;
}

.detail-item .value {
  font-size: 15px;
  color: #334155;
  font-weight: 500;
}
</style>