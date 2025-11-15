// src/api/capsuleRelatedApi.js
// 胶囊相关API接口

import request from '@/utils/request'

/**
 * 创建胶囊
 * @param {Object} data - 胶囊数据
 * @param {string} data.title - 胶囊标题
 * @param {string} data.content - 胶囊内容
 * @param {string} data.visibility - 可见性 (public/private/friend)
 * @param {Array<string>} data.tags - 标签列表
 * @param {Object} data.location - 位置信息
 * @param {number} data.location.latitude - 纬度
 * @param {number} data.location.longitude - 经度
 * @param {string} data.location.address - 地址描述
 * @param {Object} data.unlock_conditions - 解锁条件
 * @param {string} data.unlock_conditions.type - 解锁类型 (time/location/event)
 * @param {string} data.unlock_conditions.value - 解锁值
 * @param {number} data.unlock_conditions.radius - 解锁半径(米)
 * @param {string} data.unlock_conditions.event_id - 事件ID
 * @param {boolean} data.unlock_conditions.is_unlocked - 是否已解锁
 * @param {Array<string>} data.media_files - 媒体文件ID列表
 * @returns {Promise}
 */
export const createCapsule = (data) => {
  return request({
    url: '/capsules',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    data: data
  })
}

/**
 * 获取我的胶囊列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.status - 胶囊状态 (draft/published/archived等)
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
 * 多模式浏览胶囊
 * @param {Object} params - 查询参数
 * @param {string} params.mode - 浏览模式 (recent/popular/nearby/timeline/map等)
 * @param {string} params.tags - 标签筛选，多个标签用逗号分隔
 * @param {string} params.start_date - 开始日期筛选
 * @param {string} params.end_date - 结束日期筛选
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
 * @param {number} capsuleId - 胶囊ID
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
 * @param {number} capsuleId - 胶囊ID
 * @param {Object} data - 更新数据
 * @param {string} data.title - 胶囊标题
 * @param {string} data.content - 胶囊内容
 * @param {string} data.visibility - 可见性 (public/private/friend)
 * @param {Array<string>} data.tags - 标签列表
 * @returns {Promise}
 */
export const updateCapsule = (capsuleId, data) => {
  return request({
    url: `/capsules/${capsuleId}`,
    method: 'put',
    headers: {
      'Content-Type': 'application/json'
    },
    data: data
  })
}

/**
 * 删除胶囊
 * @param {number} capsuleId - 胶囊ID
 * @returns {Promise}
 */
export const deleteCapsule = (capsuleId) => {
  return request({
    url: `/capsules/${capsuleId}`,
    method: 'delete'
  })
}

/**
 * 保存胶囊草稿
 * @param {Object} data - 草稿数据
 * @param {string} data.title - 胶囊标题
 * @param {string} data.content - 胶囊内容
 * @param {string} data.visibility - 可见性 (public/private/friend)
 * @returns {Promise}
 */
export const saveCapsuleDraft = (data) => {
  return request({
    url: '/capsules/drafts',
    method: 'post',
    headers: {
      'Content-Type': 'application/json'
    },
    data: data
  })
}