// src/api/adminApi.js
// 管理后台相关API接口

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
 * 审核胶囊
 * @param {string} capsuleId - 胶囊ID
 * @param {Object} reviewData - 审核数据
 * @param {string} reviewData.action - 审核动作 (approve/reject)
 * @param {string} reviewData.reason - 拒绝原因
 * @returns {Promise}
 */
export const reviewCapsule = (capsuleId, reviewData) => {
  return request({
    url: `/admin/capsules/${capsuleId}/review`,
    method: 'post',
    data: reviewData
  })
}

/**
 * 获取举报列表
 * @param {Object} params - 查询参数
 * @param {string} params.status - 举报状态
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.target_type - 目标类型
 * @param {string} params.reason - 举报原因
 * @returns {Promise}
 */
export const getReports = (params = {}) => {
  return request({
    url: '/admin/reports',
    method: 'get',
    params
  })
}