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
  console.log('🔍 [REQUEST DEBUG] URL:', config.url)
  console.log('🔍 [REQUEST DEBUG] Method:', config.method)
  console.log('🔍 [REQUEST DEBUG] Token from localStorage:', token ? `${token.substring(0, 20)}...` : 'NO TOKEN')

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    console.log('✅ [REQUEST DEBUG] Authorization header added')
  } else {
    console.log('❌ [REQUEST DEBUG] No token found in localStorage')
  }

  // 检查并打印请求体/参数
  console.log('发出请求配置')
  console.log('URL:', config.url)
  console.log('Method:', config.method)

  // 打印请求体 (适用于 POST/PUT/PATCH 等)
  if (config.data) {
    // 检查是否是 FormData 对象
    if (config.data instanceof FormData) {
      console.log(
        'Request Body:',
        'FormData object (contents not directly printable)'
      )
      // 如果需要查看 FormData 的内容，你需要手动迭代它：
      // for (let [key, value] of config.data.entries()) {
      //   console.log(`${key}: ${value}`);
      // }
    } else {
      console.log('Request Body:', config.data)
    }
  }

  // 打印 URL 查询参数 (适用于 GET 等)
  if (config.params) {
    console.log('URL Parameters:', config.params)
  }


  // 如果是 FormData，让浏览器自动设置 Content-Type
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }

  return config
}, error => Promise.reject(error))



// 响应拦截器（适配统一响应模型）
request.interceptors.response.use(response => {
  const result = response.data
  console.log('🔍 [RESPONSE DEBUG] Status:', response.status)
  console.log('🔍 [RESPONSE DEBUG] Response data:', result)

  // 检查是否为统一响应格式
  if (result && typeof result === 'object' && 'code' in result) {
    // 业务成功
    if (result.code === 200) {
      console.log('✅ [RESPONSE DEBUG] 请求成功:', result)
      return result.data // 只返回数据部分
    } else {
      // 业务逻辑错误 - 创建错误对象，包含完整响应信息
      console.log('❌ [RESPONSE DEBUG] 业务逻辑错误:', result)
      const error = new Error(result.message || '请求失败')
      error.code = result.code
      error.data = result.data // 保留数据，即使有错误
      error.fullResponse = result // 保存完整响应对象
      return Promise.reject(error)
    }
  }

  // 如果不是统一格式，保持原样返回（兼容性）
  return result
}, error => {
  // 网络错误或服务器错误（HTTP状态码非2xx）
  console.error('❌ [ERROR DEBUG] 网络请求错误:', error)
  console.error('❌ [ERROR DEBUG] Error status:', error.response?.status)
  console.error('❌ [ERROR DEBUG] Error data:', error.response?.data)

  let errorMessage = '网络错误'
  let errorCode = 500
  let errorData = null

  if (error.response) {
    // 服务器返回了错误状态码
    console.error('❌ [ERROR DEBUG] 服务器返回错误状态码:', error.response.status)
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
})

export default request

