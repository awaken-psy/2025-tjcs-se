// src/router/index.js
// Vue Router 配置文件，负责管理前端路由
import { createRouter, createWebHashHistory } from 'vue-router'
// ⭐️ 导入用户状态 Store
import { useUserStore } from '@/store/user'

import EventsView from '@/views/EventsView.vue'
import LoginView from '@/views/LoginView.vue'
import HubView from '@/views/HubView.vue'
import MapView from '@/views/MapView.vue'
import TimeLineView from '@/views/TimeLineView.vue'

const routes = [
  {
    path: '/events',
    name: 'Events',
    component: EventsView,
  },
  {
    path: '/',
    //redirect: '/hubviews'
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
  },
  {
    path: '/hubviews',
    name: 'HubViews',
    component: HubView,
  },
  {
    path: '/map',
    name: 'Map',
    component: MapView,
  },
  // 已移除创建胶囊独立路由，统一用弹窗组件方式
  {
    path: '/my-capsule',
    name: 'MyCapsule',
    component: () => import('@/views/MyCapsuleView.vue'),
  },
  {
    path: '/test-location',
    name: 'TestLocation',
    component: () => import('@/views/TestLocationView.vue'),
  },
  {
    path: '/timeline',
    name: 'TimeLine',
    component: () => import('@/views/TimeLineView.vue'), 
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes: routes,
})

// ⭐️ 全局前置导航守卫
router.beforeEach((to, from, next) => {
  // 实例化 Store 并获取登录状态
  const userStore = useUserStore()
  const isLogin = userStore.isLogin // 使用 store/user.js 中的 isLogin getter

  // 1. 如果用户未登录
  if (!isLogin) {
    // 如果目标不是登录页，则重定向到登录页
    if (to.name !== 'Login') {
      next({ name: 'Login' })
    } else {
      // 目标已经是登录页，放行
      next()
    }
  }
  // 2. 如果用户已登录
  else {
    // 如果用户尝试访问根路径 '/'
    if (to.path === '/') {
      // 直接导航到 HubView
      next({ name: 'HubViews' })
    }
    // 如果用户尝试访问登录页 '/login'
    else if (to.name === 'Login') {
      // 避免重复登录，重定向到 HubView
      next({ name: 'HubViews' })
    }
    // 访问其他页面，放行
    else {
      next()
    }
  }
})

// 全局前置守卫：确保用户必须登录后才能访问受保护的页面
router.beforeEach((to, from, next) => {
  // 定义不需要登录就能访问的页面（白名单）
  const publicPages = ['/login']

  // 检查目标路由是否需要认证
  const requiresAuth = !publicPages.includes(to.path)

  if (requiresAuth) {
    // 检查用户是否已登录
    const token = localStorage.getItem('access_token')

    if (!token) {
      // 未登录，重定向到登录页，并保存原来要访问的页面
      console.log(`🔒 [路由守卫] 用户未登录，从 ${to.path} 重定向到登录页`)
      next({
        path: '/login',
        query: {
          redirect: to.fullPath // 保存原始访问路径，登录后可以跳转回来
        }
      })
      return
    }
  }

  // 如果是登录页面但用户已经登录，重定向到hub页面
  if (to.path === '/login') {
    const token = localStorage.getItem('access_token')
    if (token) {
      console.log('🔓 [路由守卫] 用户已登录，从登录页重定向到hub页')
      next('/hubviews')
      return
    }
  }

  // 允许正常导航
  next()
})

export default router
