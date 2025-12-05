// src/api/capsuleApi.js
// 胶囊相关API：创建、获取、我的胶囊列表
import request from '../../utils/request.js'

/**
 * 创建胶囊
 * @param {Object} data - 胶囊表单数据
 * @returns {Promise<Object>} 创建结果
 */
export const createCapsule = async (data) => {
  console.log('🚀 [CAPSULE DEBUG] createCapsule called with data:', data)

  // 只校验必填项
  if (!data.title || !data.content || !data.visibility) {
    console.error('❌ [CAPSULE DEBUG] Validation failed: missing required fields')
    throw new Error('标题、内容、可见性为必填项')
  }

  // 构造新API格式的数据对象
  const payload = {
    title: data.title,
    content: data.content,
    visibility: data.visibility,
    tags: data.tags || [],
    location: (data.lat && data.lng) ? {
      latitude: data.lat,
      longitude: data.lng,
      address: data.location || ''
    } : null,
    unlock_conditions: data.unlock_conditions || null,
    media_files: data.media_files || []
  }

  console.log('📦 [CAPSULE DEBUG] 发送到后端的胶囊数据（新API格式）:', payload)
  console.log('🔐 [CAPSULE DEBUG] Current localStorage token:', localStorage.getItem('user_token') ? 'EXISTS' : 'MISSING')

  try {
    const result = await request({
      url: '/capsules/',  // 添加尾部斜杠避免307重定向
      method: 'post',
      data: payload
    })
    console.log('✅ [CAPSULE DEBUG] 胶囊创建成功:', result)
    return result
  } catch (error) {
    console.error('❌ [CAPSULE DEBUG] 胶囊创建失败:', error)
    throw error
  }
}

/**
 * 获取我的胶囊列表
 * @param {Object} params - 可选参数
 * @returns {Promise<Array>} 胶囊列表
 */
export const getMyCapsules = async (params = {}) => {
  console.log('🔍 [CAPSULE DEBUG] getMyCapsules called with params:', params)
  console.log('🔐 [CAPSULE DEBUG] Current localStorage token:', localStorage.getItem('user_token') ? 'EXISTS' : 'MISSING')

  try {
    const result = await request({
      url: '/capsules/my',
      method: 'get',
      params
    })
    console.log('✅ [CAPSULE DEBUG] 获取我的胶囊成功:', result)
    return result
  } catch (error) {
    console.error('❌ [CAPSULE DEBUG] 获取我的胶囊失败:', error)
    throw error
  }
}

/**
 * 获取单个胶囊详情
 * @param {String|Number} capsuleId
 * @returns {Promise<Object>} 胶囊详情
 */
export const getCapsuleDetail = async (capsuleId) => {
  console.log('🔍 [CAPSULE DEBUG] getCapsuleDetail called with ID:', capsuleId)
  console.log('🔐 [CAPSULE DEBUG] Current localStorage token:', localStorage.getItem('user_token') ? 'EXISTS' : 'MISSING')

  try {
    const result = await request({
      url: `/capsules/${capsuleId}`,
      method: 'get'
    })
    console.log('✅ [CAPSULE DEBUG] 获取胶囊详情成功:', result)
    return result
  } catch (error) {
    console.error('❌ [CAPSULE DEBUG] 获取胶囊详情失败:', error)
    throw error
  }
}