// ===============================
// 4. 请求适配层（全局axios实例，所有API都通过此发起）
// ===============================
import axios from 'axios'

const request = axios.create({
  baseURL: '/api', // 统一前缀，所有API都走/api
  //baseURL:'http://127.0.0.1:4523/m1/7397469-7130026-default', // 注释掉外部 mock 服务器
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    //console.log('✅ [REQUEST DEBUG] Authorization header added')
  } else {
    console.log('❌ [REQUEST DEBUG] No token found in localStorage')
  }

  // 详细记录请求信息
  console.group(`📡 [REQUEST DETAILS] ${config.method?.toUpperCase()} ${config.url}`)
  console.log('📋 请求方法:', config.method?.toUpperCase())
  console.log('🌐 请求URL:', config.url)
  console.log('🔑 认证头:', config.headers.Authorization ? '已设置' : '未设置')
  
  // 记录请求参数
  if (config.method === 'get' && config.params) {
    console.log('📊 GET请求参数:', config.params)
  } else if (config.data) {
    console.log('📦 请求体数据:', config.data)
  }
  
  console.log('📄 请求头:', config.headers)
  console.groupEnd()

  // 如果是 FormData，让浏览器自动设置 Content-Type
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }

  return config
}, error => Promise.reject(error))



// 响应拦截器（适配统一响应模型）
request.interceptors.response.use(response => {
  const result = response.data
  
  // 详细记录响应信息
  console.group(`✅ [RESPONSE DETAILS] ${response.config.method?.toUpperCase()} ${response.config.url}`)
  console.log('📊 响应状态码:', response.status)
  console.log('📋 响应头:', response.headers)
  console.log('📦 完整响应数据:', result)
  
  // 检查是否为统一响应格式
  if (result && typeof result === 'object' && 'code' in result) {
    console.log('🔢 业务状态码:', result.code)
    console.log('📝 业务消息:', result.message)
    
    // 业务成功
    if (result.code === 200) {
      console.log('🎯 返回数据部分:', result.data)
      console.log('✅ 请求成功')
      console.groupEnd()
      return result.data // 只返回数据部分
    } else {
      // 业务逻辑错误 - 创建错误对象，包含完整响应信息
      console.log('❌ 业务逻辑错误')
      console.groupEnd()
      const error = new Error(result.message || '请求失败')
      error.code = result.code
      error.data = result.data // 保留数据，即使有错误
      error.fullResponse = result // 保存完整响应对象
      return Promise.reject(error)
    }
  }

  console.log('⚠️ 非统一响应格式，返回原始数据')
  console.groupEnd()
  // 如果不是统一格式，保持原样返回（兼容性）
  return result
}, error => {
  // 详细记录错误信息
  console.group(`❌ [ERROR DETAILS] ${error.config?.method?.toUpperCase()} ${error.config?.url}`)
  
  // 网络错误或服务器错误（HTTP状态码非2xx）
  console.error('🚨 错误类型:', error.name || 'Unknown Error')
  console.error('📝 错误消息:', error.message)
  
  if (error.response) {
    // 服务器返回了错误状态码
    console.error('🔴 HTTP状态码:', error.response.status)
    console.error('📋 响应头:', error.response.headers)
    console.error('📦 错误响应数据:', error.response.data)
    
    const responseData = error.response.data

    // 尝试从响应数据中提取错误信息
    if (responseData && typeof responseData === 'object') {
      // 如果响应数据已经是统一格式
      if ('code' in responseData && 'message' in responseData) {
        console.error('🔢 业务状态码:', responseData.code)
        console.error('📝 业务消息:', responseData.message)
        console.error('📊 业务数据:', responseData.data)
      } else {
        // 其他格式的错误响应（FastAPI的HTTPException返回detail字段）
        console.error('📋 错误详情:', responseData.detail || responseData.message || responseData.error)
      }
    }
  } else if (error.request) {
    // 请求发出但没有收到响应
    console.error('🌐 网络状态: 请求已发出但未收到响应')
    console.error('📡 请求对象:', error.request)
  } else {
    // 其他错误
    console.error('⚡ 错误来源: 请求配置错误或其他客户端错误')
    console.error('🔧 错误堆栈:', error.stack)
  }
  
  console.groupEnd()

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
        // 其他格式的错误响应（FastAPI的HTTPException返回detail字段）
        errorMessage = responseData.message || responseData.detail || responseData.error || `服务器错误 (${error.response.status})`
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

  return Promise.reject(customError)
})

export default request