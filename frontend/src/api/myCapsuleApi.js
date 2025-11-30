/**
 * 我的胶囊页专属API：支持CRUD、图片上传、标签管理、模拟数据、分页筛选
 * 仅供MyCapsuleView.vue使用，不影响其他页面
 */
import request from '../utils/request.js'

// 导入新API的函数
import { getMyCapsules as newGetMyCapsules } from './new/capsulesApi.js'

/**
 * 获取我的胶囊列表（分页、筛选，使用新API）
 * @param {Object} params - { page?: number, page_size?: number, status?: string }
 * @returns {Promise<Array>} 胶囊列表
 */
export const getMyCapsules = async (params = {}) => {
  // 使用新API，但保持参数兼容性
  const newParams = {
    page: params.page || 1,
    limit: params.page_size || params.limit || 20,
    ...params
  }
  return await newGetMyCapsules(newParams)
}

// 壳子函数：创建胶囊，实际调用 new/capsulesApi.js 的 createCapsule
import { createCapsule as mapCreateCapsule } from './new/capsulesApi.js'
// import { createCapsule as mapCreateCapsule } from './mapApi.js'
//qhz修改
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
 * 编辑已有胶囊（新API格式）
 * @param {Object} data - { id, title?, content?, visibility?, tags? }
 * @returns {Promise<Object>}
 */
export const editCapsule = async (data) => {
  if (!data.id) throw new Error('缺少胶囊id')

  // 构造新API格式的更新数据
  const updatePayload = {}
  if (data.title !== undefined) updatePayload.title = data.title
  if (data.content !== undefined) updatePayload.content = data.content
  if (data.visibility !== undefined) updatePayload.visibility = data.visibility
  if (data.tags !== undefined) updatePayload.tags = data.tags

  return await request({
    url: `/capsules/${data.id}`,
    method: 'put',
    data: updatePayload
  })
}

/**
 * 删除胶囊（新API格式）
 * @param {String|Number} capsuleId
 * @returns {Promise<Object>}
 */
export const deleteCapsule = async (capsuleId) => {
  return await request({
    url: `/capsules/${capsuleId}`,
    method: 'delete'
  })
}

/**
 * 上传胶囊图片（新API格式）
 * @param {File} file
 * @returns {Promise<Object>}
 */
export const uploadCapsuleImage = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('type', 'image')

  // 注意：不要手动设置Content-Type，让浏览器自动设置boundary
  return await request({
    url: '/upload',
    method: 'post',
    data: formData
  })
}
