// ===============================
// 4. 请求适配层（全局axios实例，所有API都通过此发起）
// ===============================
import axios from 'axios'

const request = axios.create({
  baseURL: '/api', // 统一前缀，所有API都走/api
  timeout: 10000
})

// 请求拦截器（可全局注入token、统一header等）
request.interceptors.request.use(config => {
  // 自动携带token
  const token = localStorage.getItem('user_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
}, error => Promise.reject(error))

// 响应拦截器（统一处理返回结构、错误码等）
request.interceptors.response.use(response => {
  return response.data
}, error => Promise.reject(error))

export default request
