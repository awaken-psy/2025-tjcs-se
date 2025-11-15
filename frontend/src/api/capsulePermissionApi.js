// src/api/capsulePermissionApi.js
// 胶囊权限相关API接口

import request from '@/utils/request'

/**
 * 获取待审核胶囊列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.sort - 排序方式
 * @returns {Promise}
 */
export const getPendingCapsules = (params = {}) => {
  return request({
    url: '/admin/capsules/pending',
    method: 'get',
    params
  })
}

/**
 * 审核胶囊（批准或拒绝）
 * @param {string} capsuleId - 胶囊ID
 * @param {string} action - 审核操作 (approve/reject)
 * @param {string} reason - 审核原因/备注
 * @returns {Promise}
 */
export const reviewCapsule = (capsuleId, action, reason = '') => {
  return request({
    url: `/admin/capsules/${capsuleId}/review`,
    method: 'post',
    headers: {
      'Content-Type': 'application/json'
    },
    data: {
      action,
      reason
    }
  })
}

/**
 * 获取举报列表
 * @param {Object} params - 查询参数
 * @param {string} params.status - 举报状态 (pending/processed)
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.target_type - 举报目标类型 (capsule/user/comment等)
 * @param {string} params.reason - 举报原因筛选
 * @returns {Promise}
 */
export const getReports = (params = {}) => {
  return request({
    url: '/admin/reports',
    method: 'get',
    params
  })
}