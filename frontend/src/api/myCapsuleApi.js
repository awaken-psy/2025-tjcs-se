/**
 * 我的胶囊页专属API：支持CRUD、图片上传、标签管理、模拟数据、分页筛选
 * 仅供MyCapsuleView.vue使用，不影响其他页面
 */
import request from '../utils/request.js'

/**
 * 获取我的胶囊列表（分页、筛选，真实后端）
 * @param {Object} params - { userId?: string }
 * @returns {Promise<Array>} 胶囊列表
 */
// 获取我的胶囊列表（真实后端，参数userId可选，后端会自动识别当前用户）
export const getMyCapsules = async (params = {}) => {
  return await request({
    url: '/capsule/my',
    method: 'get',
    params
  })
}

// 壳子函数：创建胶囊，实际调用 mapApi.js 的 createCapsule
import { createCapsule as mapCreateCapsule } from './new/mapApi.js'

/**
 * 创建新胶囊（壳子函数，复用mapApi.js的实现）
 * @param {Object} data
 * @returns {Promise<Object>}
 */
export const createCapsule = async (data) => {
  // 如果mapApi.js中有createCapsule则直接调用，否则留空实现
  if (typeof mapCreateCapsule === 'function') {
    return await mapCreateCapsule(data)
  } else {
    // TODO: mapApi.js未实现createCapsule时的兜底逻辑
    throw new Error('mapApi.js未实现createCapsule')
  }
}

/**
 * 编辑已有胶囊（真实后端）
 * @param {Object} data - { id, ... }
 * @returns {Promise<Object>}
 */
// 编辑已有胶囊（真实后端，id为必填，其他字段按需传递）
export const editCapsule = async (data) => {
  if (!data.id) throw new Error('缺少胶囊id')
  return await request({
    url: `/capsule/edit/${data.id}`,
    method: 'post',
    data
  })
}

/**
 * 删除胶囊（真实后端）
 * @param {String|Number} capsuleId
 * @returns {Promise<Object>}
 */
export const deleteCapsule = async (capsuleId) => {
  return await request({
    url: `/capsule/delete/${capsuleId}`,
    method: 'post'
  })
}

/**
 * 上传胶囊图片（真实后端）
 * @param {File} file
 * @returns {Promise<Object>}
 */
export const uploadCapsuleImage = async (file) => {
  const formData = new FormData()
  formData.append('img', file)
  return await request({
    url: '/capsule/upload-img',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
