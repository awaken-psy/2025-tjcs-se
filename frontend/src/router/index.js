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

export default router
