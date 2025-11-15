// src/api/capsuleInteractionApi.js
// 胶囊交互相关API接口

import request from '@/utils/request'

/**
 * 点赞胶囊
 * @param {number} capsuleId - 胶囊ID
 * @returns {Promise}
 */
export const likeCapsule = (capsuleId) => {
  return request({
    url: `/capsules/${capsuleId}/like`,
    method: 'post'
  })
}

/**
 * 添加胶囊评论
 * @param {number} capsuleId - 胶囊ID
 * @param {string} content - 评论内容
 * @param {string} parentId - 父评论ID (可选，用于回复评论)
 * @returns {Promise}
 */
export const addCapsuleComment = (capsuleId, content, parentId = null) => {
  return request({
    url: `/capsules/${capsuleId}/comments`,
    method: 'post',
    headers: {
      'Content-Type': 'application/json'
    },
    data: {
      content,
      parent_id: parentId
    }
  })
}

/**
 * 获取胶囊评论列表
 * @param {number} capsuleId - 胶囊ID
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.sort - 排序方式
 * @returns {Promise}
 */
export const getCapsuleComments = (capsuleId, params = {}) => {
  return request({
    url: `/capsules/${capsuleId}/comments`,
    method: 'get',
    params
  })
}

/**
 * 收藏胶囊
 * @param {number} capsuleId - 胶囊ID
 * @returns {Promise}
 */
export const collectCapsule = (capsuleId) => {
  return request({
    url: `/capsules/${capsuleId}/collect`,
    method: 'post'
  })
}

/**
 * 举报内容
 * @param {string} targetType - 举报目标类型 (capsule/user/comment等)
 * @param {string} targetId - 举报目标ID
 * @param {string} reason - 举报原因
 * @param {string} description - 详细描述
 * @returns {Promise}
 */
export const reportContent = (targetType, targetId, reason, description = '') => {
  return request({
    url: '/reports',
    method: 'post',
    headers: {
      'Content-Type': 'application/json'
    },
    data: {
      target_type: targetType,
      target_id: targetId,
      reason,
      description
    }
  })
}