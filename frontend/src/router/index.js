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

// src/router/index.js (只展示 beforeEach 部分)

router.beforeEach((to, from, next) => {
    // 实例化 Store
    const userStore = useUserStore()
    
    // ⭐️ 核心修改 1: 仅从 Store 获取持久化的 isLogin 状态
    //    由于 Pinia 持久化（在 user.js 中已配置）会在应用启动时恢复 token，
    //    userStore.isLogin 此时会正确反映用户的真实登录状态（即 !!state.token）。
    const isLogin = userStore.isLogin 
    
    // ⭐️ 核心修改 2: 仅依赖 isLogin 判断是否未登录
    const isUserNotLoggedIn = !isLogin 

    // 定义白名单，不需要登录即可访问
    const publicPages = ['Login'] 

    // 检查目标路由是否需要认证
    const requiresAuth = !publicPages.includes(to.name)

    // --- 1. 未登录处理 ---
    if (isUserNotLoggedIn) {
        // 如果需要认证，则重定向到登录页
        if (requiresAuth) {
            console.log(`🔒 [路由守卫] 用户未登录，从 ${to.fullPath} 重定向到登录页`)
            next({
                name: 'Login',
                query: {
                    redirect: to.fullPath // 保存原始访问路径
                }
            })
        } else {
            // 目标是白名单页面（Login），放行
            next()
        }
    }
    // --- 2. 已登录处理 ---
    else {
        // 如果用户尝试访问登录页或根路径，重定向到 HubViews
        if (to.name === 'Login' || to.path === '/') {
            console.log('🔓 [路由守卫] 用户已登录，从登录页/根路径重定向到hub页')
            next({ name: 'HubViews' })
        }
        // 访问其他页面，放行
        else {
            next()
        }
    }
})

export default router
