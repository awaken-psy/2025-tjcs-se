// src/api/capsulesApi.js
// 胶囊相关API接口

import request from '@/utils/request'

/**
 * 创建胶囊
 * @param {Object} capsuleData - 胶囊数据
 * @param {string} capsuleData.title - 胶囊标题
 * @param {string} capsuleData.content - 胶囊内容
 * @param {string} capsuleData.visibility - 可见性 (private/public)
 * @param {Array} capsuleData.tags - 标签数组
 * @param {Object} capsuleData.location - 位置信息
 * @param {number} capsuleData.location.latitude - 纬度
 * @param {number} capsuleData.location.longitude - 经度
 * @param {string} capsuleData.location.address - 地址描述
 * @param {Object} capsuleData.unlock_conditions - 解锁条件
 * @param {string} capsuleData.unlock_conditions.type - 解锁类型
 * @param {string} capsuleData.unlock_conditions.value - 解锁值
 * @param {number} capsuleData.unlock_conditions.radius - 解锁半径
 * @param {string} capsuleData.unlock_conditions.event_id - 事件ID
 * @param {boolean} capsuleData.unlock_conditions.is_unlocked - 是否已解锁
 * @param {Array} capsuleData.media_files - 媒体文件ID数组
 * @returns {Promise}
 */
export const createCapsule = (capsuleData) => {
  console.log('请求体', capsuleData)
  return request({
    url: '/capsules',
    method: 'post',
    data: capsuleData
  })
}

/**
 * 获取我的胶囊列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.status - 胶囊状态
 * @returns {Promise}
 */
export const getMyCapsules = (params = {}) => {
  return request({
    url: '/capsules/my',
    method: 'get',
    params
  })
}

/**
 * 浏览胶囊
 * @param {Object} params - 查询参数
 * @param {string} params.mode - 浏览模式
 * @param {string} params.tags - 标签筛选
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise}
 */
export const browseCapsules = (params = {}) => {
  return request({
    url: '/capsules/browse',
    method: 'get',
    params
  })
}

/**
 * 获取胶囊详情
 * @param {string} capsuleId - 胶囊ID
 * @returns {Promise}
 */
export const getCapsuleDetail = (capsuleId) => {
  return request({
    url: `/capsules/${capsuleId}`,
    method: 'get'
  })
}

/**
 * 更新胶囊
 * @param {string} capsuleId - 胶囊ID
 * @param {Object} capsuleData - 胶囊数据
 * @param {string} capsuleData.title - 胶囊标题
 * @param {string} capsuleData.content - 胶囊内容
 * @param {string} capsuleData.visibility - 可见性
 * @param {Array} capsuleData.tags - 标签数组
 * @returns {Promise}
 */
export const updateCapsule = (capsuleId, capsuleData) => {
  return request({
    url: `/capsules/${capsuleId}`,
    method: 'put',
    data: capsuleData
  })
}

/**
 * 删除胶囊
 * @param {string} capsuleId - 胶囊ID
 * @returns {Promise}
 */
export const deleteCapsule = (capsuleId) => {
  return request({
    url: `/capsules/${capsuleId}`,
    method: 'delete'
  })
}

/**
 * 创建胶囊草稿
 * @param {Object} draftData - 草稿数据
 * @param {string} draftData.title - 草稿标题
 * @param {string} draftData.content - 草稿内容
 * @param {string} draftData.visibility - 可见性
 * @returns {Promise}
 */
export const createCapsuleDraft = (draftData) => {
  return request({
    url: '/capsules/drafts',
    method: 'post',
    data: draftData
  })
}

//TODO:newapi
/**
 * 点赞/取消点赞胶囊
 * @param {string} capsuleId - 胶囊ID
 * @returns {Promise}
 */
export const likeCapsule = (capsuleId) => {
  return request({
    url: `/capsules/${capsuleId}/like`, // 假设的API路径
    method: 'post' // 或 put
  })
}