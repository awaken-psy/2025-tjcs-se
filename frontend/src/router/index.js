import EventsView from '@/views/EventsView.vue'
// src/router/index.js
// Vue Router 配置文件，负责管理前端路由
import { createRouter, createWebHashHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'

import HubView from '@/views/HubView.vue'

import MapView from '@/views/MapView.vue'

const routes = [
  {
    path: '/events',
    name: 'Events',
    component: EventsView
  },
  {
    path: '/',
    redirect: '/hubviews'
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView
  },
  {
    path: '/hubviews',
    name: 'HubViews',
    component: HubView
  },
  {
    path: '/map',
    name: 'Map',
    component: MapView
  },
  // 已移除创建胶囊独立路由，统一用弹窗组件方式
  {
    path: '/my-capsule',
    name: 'MyCapsule',
    component: () => import('@/views/MyCapsuleView.vue')
  },
  {
    path: '/test-location',
    name: 'TestLocation',
    component: () => import('@/views/TestLocationView.vue')
  },
  {
    path: '/test-position',
    name: 'TestPosition',
    component: () => import('@/views/TestLocationView.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes: routes
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
