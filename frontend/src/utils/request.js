// ===============================
// 4. 请求适配层（全局axios实例，所有API都通过此发起）
// ===============================
import { refreshToken as callRefreshTokenApi } from '@/api/new/authenticationApi'
import { useUserStore } from '@/store/user'
import axios from 'axios'


const request = axios.create({
  baseURL: '/api', // 统一前缀，所有API都走/api
  //baseURL:'http://127.0.0.1:4523/m1/7397469-7130026-default', // 注释掉外部 mock 服务器
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})


// Token 刷新并发控制状态
// 锁状态：防止并发请求同时触发多次 token 刷新
let isRefreshing = false
// 队列：存储所有因 token 过期而失败的请求
let failedQueue = []

// 添加失败的请求到队列，并在刷新成功后重试或失败后拒绝
const processQueue = (error, token = null) => {
  failedQueue.forEach(p => {
    if (error) {
      p.reject(error)
    } else {
      // 使用新 token 重新发起请求
      p.resolve(token)
    }
  })
  failedQueue = []
}


// 请求拦截器
request.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  // 如果是 FormData，让浏览器自动设置 Content-Type
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }

  return config
}, error => Promise.reject(error))


// 响应拦截器
request.interceptors.response.use(
  response => {
    const result = response.data

    // 检查是否为统一响应格式
    if (result && typeof result === 'object' && 'code' in result) {
      // 业务成功
      if (result.code === 200) {
        console.log('请求成功:', result)
        return result.data  // 直接返回业务数据
      } else {
        // 业务逻辑错误
        const error = new Error(result.message || '请求失败')
        error.code = result.code
        error.data = result.data 
        error.fullResponse = result 
        return Promise.reject(error)
      }
    }

    // 如果不是统一格式，保持原样返回
    return result
  }, 
  async error => {
    const originalRequest = error.config
    const userStore = useUserStore()

    // 刷新令牌逻辑
    // 检查：是否是 401 错误，且不是刷新 token 接口本身 (避免死循环)
    if (error.response?.status === 401 && originalRequest.url !== '/auth/refresh') {
      
      // 步骤 1: 如果当前正在刷新 token，则将当前请求加入队列等待
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
        .then(token => {
          // 拿到新 token 后，更新请求头并重新发起请求
          originalRequest.headers.Authorization = `Bearer ${token}`
          return request(originalRequest)
        })
        .catch(err => Promise.reject(err))
      }

      // 步骤 2: 首次遇到 401，开始刷新 token
      isRefreshing = true
      
      // 获取 refresh_token
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        // 没有刷新 token，强制退出登录
        userStore.logout()
        processQueue(new Error('未找到刷新令牌，请重新登录'))
        return Promise.reject(error)
      }

      try {
        // 步骤 3: 调用刷新 API
        const responseData = await callRefreshTokenApi(refreshToken) // 注意这里获取的是 data 部分
        
        const newAccessToken = responseData.access_token 
        const newRefreshToken = responseData.refresh_token 
        
        if (!newAccessToken) {
          throw new Error('刷新接口未返回 access_token')
        }

        // 步骤 4: 更新 Store 和 LocalStorage
        userStore.updateToken(newAccessToken, newRefreshToken)
        
        // 步骤 5: 处理等待队列，通知所有等待请求重试
        processQueue(null, newAccessToken)
        
        // 步骤 6: 使用新 token 重新发起原始请求
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
        return request(originalRequest)
        
      } catch (refreshError) {
        // 刷新 token 失败 (Refresh Token 也可能已过期)
        userStore.logout() 
        processQueue(refreshError)
        return Promise.reject(new Error('会话过期，请重新登录'))
      } finally {
        isRefreshing = false
      }
    }

    // --- 原始错误处理逻辑 (位于刷新逻辑之后) ---
    console.error('网络请求错误:', error)

    let errorMessage = '网络错误'
    let errorCode = 500
    let errorData = null

    if (error.response) {
      // 服务器返回了错误状态码
      const responseData = error.response.data

      // 尝试从响应数据中提取错误信息
      if (responseData && typeof responseData === 'object') {
        // 如果响应数据已经是统一格式
        if ('code' in responseData && 'message' in responseData) {
          errorMessage = responseData.message
          errorCode = responseData.code
          errorData = responseData.data
        } else {
          // 其他格式的错误响应
          errorMessage = responseData.message || responseData.error || `服务器错误 (${error.response.status})`
          errorCode = error.response.status
          errorData = responseData
        }
      } else {
        errorMessage = `请求失败 (${error.response.status})`
        errorCode = error.response.status
      }
    } else if (error.request) {
      // 请求发出但没有收到响应
      errorMessage = '网络连接失败，请检查网络设置'
      errorCode = 'NETWORK_ERROR'
    } else {
      // 其他错误
      errorMessage = error.message || '未知错误'
    }

    const customError = new Error(errorMessage)
    customError.code = errorCode
    customError.data = errorData
    customError.originalError = error

    console.error('请求拦截器捕获错误:', customError)
    return Promise.reject(customError)
  }
)

export default request