// src/api/capsuleApi.js
// 胶囊相关API：创建、获取、我的胶囊列表
import request from '../utils/request.js'

/**
 * 创建胶囊
 * @param {Object} data - 胶囊表单数据
 * @returns {Promise<Object>} 创建结果
 */
export const createCapsule = async(data) => {
  // 只校验必填项
  if (!data.title || !data.content || !data.visibility) {
    throw new Error('标题、内容、可见性为必填项')
  }
  
  // 构造后端需要的数据对象 - 严格匹配后端模型
  const payload = {
    title: data.title,
    content: data.content,
    visibility: data.visibility,
    tags: data.tags || [],
    location: data.location || '',
    lat: data.lat || 0,
    lng: data.lng || 0,
    createTime: data.createTime,
    updateTime: data.updateTime,
    imageUrl: data.imageUrl || '',  // 只发送imageUrl，不发送image
    likes: data.likes || 0,
    views: data.views || 0
    // 注意：完全移除以下字段
    // - image (File对象无法序列化)
    // - status (后端自动设置)
    // - userId, userEmail, userName (后端自动获取)
  }
  
  console.log('发送到后端的胶囊数据:', payload)
  
  return await request({
    url: '/capsule/create',
    method: 'post',
    data: payload
  })
}

/**
 * 获取我的胶囊列表
 * @param {Object} params - 可选参数
 * @returns {Promise<Array>} 胶囊列表
 */
export const getMyCapsules = async(params = {}) => {
  return await request({
    url: '/capsule/my',
    method: 'get',
    params
  })
}

/**
 * 获取单个胶囊详情
 * @param {String|Number} capsuleId
 * @returns {Promise<Object>} 胶囊详情
 */
export const getCapsuleDetail = async(capsuleId) => {
  return await request({
    url: `/capsule/detail/${capsuleId}`,
    method: 'get'
  })
}