// src/store/user.js
// 用户相关状态管理（Pinia 示例）
import { defineStore } from 'pinia'
import { logout as callLogoutApi } from '@/api/new/authenticationApi'
import router from '@/router' // 🔥 修复：导入router

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: null,
    token: null,
    refreshToken: null,
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
    userAvatar: (state) => state.userInfo?.avatar || '',
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
     * @param {string} token - JWT token (Access Token)
     * @param {Object} userInfo - 用户信息
     * @param {string} refreshToken - 刷新token
     */
    login(token, userInfo, refreshToken = null) {
      this.token = token
      this.userInfo = userInfo
      if (refreshToken) {
        this.refreshToken = refreshToken
      }

      // 写入 LocalStorage，适配请求拦截器和持久化读取
      localStorage.setItem('access_token', token)
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken)
      }
      // 建议：如果你需要在登录组件中移除 'user_info' 的手动写入，Store 应负责写入
      // localStorage.setItem('user_info', JSON.stringify(userInfo))
    },

    /**
     * 用户退出登录
     */
    async logout() {
      try {
        // 1. 异步调用后端 API 立即废弃 Refresh Token
        await callLogoutApi()
      } catch (error) {
        // 即使 API 调用失败（例如网络错误），我们仍应在前端退出，
        // 因为用户已经选择了退出，不能阻止其退出操作。
        console.error('Logout API 调用失败，但仍执行前端退出:', error)
      }

      // 2. 清除前端状态
      this.token = null
      this.userInfo = null
      this.refreshToken = null

      // 3. 清除本地存储
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')

      // 4. 重定向到登录页
      router.push('/login')
    },

    /**
     * 更新token (用于无感刷新)
     * @param {string} newToken - 新的token
     * @param {string} newRefreshToken - 新的刷新token
     */
    updateToken(newToken, newRefreshToken = null) {
      this.token = newToken
      localStorage.setItem('access_token', newToken) // 关键：同步写入给请求拦截器

      if (newRefreshToken) {
        this.refreshToken = newRefreshToken
        localStorage.setItem('refresh_token', newRefreshToken) // 写入新的 refresh token
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
    },
  },

  // 持久化配置
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'user-store',
        storage: localStorage,
        paths: ['userInfo', 'token', 'refreshToken'],
      },
    ],
  },
})
