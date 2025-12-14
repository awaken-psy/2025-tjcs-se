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

// ⭐️ 统一后的全局前置导航守卫 (推荐保留这一个)
router.beforeEach((to, from, next) => {
    // 实例化 Store 并获取登录状态
    const userStore = useUserStore()
    const isLogin = userStore.isLogin // 使用 store/user.js 中的 isLogin getter
    const token = localStorage.getItem('access_token') // 也可以直接使用 token 来判断

    // 假设：只要 isLogin 为 false 或 token 不存在，就视为未登录
    const isUserNotLoggedIn = !isLogin || !token

    // 定义白名单，不需要登录即可访问
    const publicPages = ['Login'] // 使用路由的 name 更安全

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
        // 如果用户尝试访问登录页，重定向到 HubViews
        if (to.name === 'Login') {
            console.log('🔓 [路由守卫] 用户已登录，从登录页重定向到hub页')
            next({ name: 'HubViews' })
        }
        // 如果用户尝试访问根路径 '/'，重定向到 HubViews
        else if (to.path === '/') {
            next({ name: 'HubViews' })
        }
        // 访问其他页面，放行
        else {
            next()
        }
    }
})


export default router


