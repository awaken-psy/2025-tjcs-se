// src/store/user.js
// 用户相关状态管理（Pinia 示例）
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: null
  }),
  getters: {
    role: (state) => state.userInfo?.role || 'guest', // 便于直接访问权限
    isAdmin: (state) => state.userInfo?.role === 'admin',
    isUser: (state) => state.userInfo?.role === 'user',
    isGuest: (state) => state.userInfo?.role === 'guest',
  },
  actions: {
    setUserInfo(info) {
      this.userInfo = info
    },
    login(token, userInfo) {
      // 可扩展token存储逻辑
      this.userInfo = userInfo
    }
  }
})
