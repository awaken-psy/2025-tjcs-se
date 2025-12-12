// src/api/interactionsApi.js
// 胶囊相关API接口

import request from '@/utils/request'

/**
 * 点赞胶囊
 * @param {string} capsuleId - 胶囊ID
 * @returns {Promise}
 */
export const likeCapsule = (capsuleId) => {
  return request({
    url: `/interactions/${capsuleId}/like`,
    method: 'post'
  })
}

/**
 * 评论胶囊
 * @param {string} capsuleId - 胶囊ID
 * @param {Object} commentData - 评论数据
 * @param {string} commentData.content - 评论内容
 * @param {string} commentData.parent_id - 父评论ID
 * @returns {Promise}
 */
export const commentCapsule = (capsuleId, commentData) => {
  return request({
    url: `/interactions/${capsuleId}/comments`,
    method: 'post',
    data: commentData
  })
}

/**
 * 获取胶囊评论列表
 * @param {string} capsuleId - 胶囊ID
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.sort - 排序方式
 * @returns {Promise}
 */
export const getCapsuleComments = (capsuleId, params = {}) => {
  return request({
    url: `/interactions/${capsuleId}/comments`,
    method: 'get',
    params
  })
}

/**
 * 收藏胶囊
 * @param {string} capsuleId - 胶囊ID
 * @returns {Promise}
 */
export const collectCapsule = (capsuleId) => {
  return request({
    url: `/interactions/${capsuleId}/collect`,
    method: 'post'
  })
}

/**
 * 提交举报
 * @param {Object} reportData - 举报数据
 * @param {string} reportData.target_type - 举报目标类型
 * @param {string} reportData.target_id - 举报目标ID
 * @param {string} reportData.reason - 举报原因
 * @param {string} reportData.description - 举报描述
 * @returns {Promise}
 */
export const submitReport = (reportData) => {
  return request({
    url: '/reports/',
    method: 'post',
    data: reportData
  })
}