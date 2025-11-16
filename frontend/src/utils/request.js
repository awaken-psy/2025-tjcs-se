// ===============================
// 4. 请求适配层（全局axios实例，所有API都通过此发起）
// ===============================
import axios from 'axios'

const request = axios.create({
  //baseURL: '/api', // 统一前缀，所有API都走/api
  baseURL:'https://m1.apifoxmock.com/m1/7397469-7130026-default',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(config => {
  const token = localStorage.getItem('user_token')
  if (token) config.headers.Authorization = `Bearer ${token}`

  // 如果是 FormData，让浏览器自动设置 Content-Type
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }

  return config
}, error => Promise.reject(error))

// 响应拦截器（适配统一响应模型）
request.interceptors.response.use(response => {
  const result = response.data

  // 检查是否为统一响应格式
  if (result && typeof result === 'object' && 'code' in result) {
    // 业务成功
    if (result.code === 200) {
      return result.data  // 直接返回业务数据
    } else {
      // 业务逻辑错误
      const error = new Error(result.message || '请求失败')
      error.code = result.code
      error.data = result.data
      return Promise.reject(error)
    }
  }

  // 如果不是统一格式，保持原样返回（兼容性）
  return result
}, error => {
  // 网络错误或服务器错误
  const errorMessage = error.response?.data?.message || error.message || '网络错误'
  const errorCode = error.response?.status || 500

  const customError = new Error(errorMessage)
  customError.code = errorCode
  customError.data = error.response?.data

  return Promise.reject(customError)
})

export default request

