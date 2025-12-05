// src/store/user.js
// 用户相关状态管理（Pinia 示例）
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: null,
    token: null,
    refreshToken: null
  }),
  
  getters: {
    // 用户角色相关
    role: (state) => state.userInfo?.role,
    isAdmin: (state) => state.userInfo?.role === 'admin',
    isUser: (state) => state.userInfo?.role === 'user',
    
    // 登录状态
    isLogin: (state) => !!state.token,
    
    // 用户信息
    userId: (state) => state.userInfo?.user_id || null,
    userEmail: (state) => state.userInfo?.email || '',
    userNickname: (state) => state.userInfo?.nickname || '',
    userAvatar: (state) => state.userInfo?.avatar || ''
  },
  
  actions: {
    /**
     * 设置用户信息
     * @param {Object} info - 用户信息
     */
    setUserInfo(info) {
      this.userInfo = info
    },
    
    /**
     * 用户登录
     * @param {string} token - JWT token
     * @param {Object} userInfo - 用户信息
     * @param {string} refreshToken - 刷新token
     */
    login(token, userInfo, refreshToken = null) {
      this.token = token
      this.userInfo = userInfo
      if (refreshToken) {
        this.refreshToken = refreshToken
      }
    },
    
    /**
     * 用户退出登录
     */
    logout() {
      this.token = null
      this.userInfo = null
      this.refreshToken = null
      
      // 清除本地存储
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
    },
    
    /**
     * 更新token
     * @param {string} newToken - 新的token
     * @param {string} newRefreshToken - 新的刷新token
     */
    updateToken(newToken, newRefreshToken = null) {
      this.token = newToken
      if (newRefreshToken) {
        this.refreshToken = newRefreshToken
      }
    },
    
    /**
     * 更新用户信息
     * @param {Object} newInfo - 新的用户信息
     */
    updateUserInfo(newInfo) {
      if (this.userInfo) {
        this.userInfo = { ...this.userInfo, ...newInfo }
      } else {
        this.userInfo = newInfo
      }
    }
  },
  
  // 持久化配置
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'user-store',
        storage: localStorage,
        paths: ['userInfo', 'token', 'refreshToken']
      }
    ]
  }
})

