// src/api/friendApi.js
// 好友相关API接口

import request from '@/utils/request'

/**
 * 发送好友请求
 * @param {number} targetUserId - 目标用户ID
 * @returns {Promise}
 */
export const sendFriendRequest = (targetUserId) => {
  return request({
    url: '/friends/requests',
    method: 'post',
    headers: {
      'Content-Type': 'application/json'
    },
    data: {
      target_user_id: targetUserId
    }
  })
}

/**
 * 获取好友请求列表
 * @param {Object} params - 查询参数
 * @param {string} params.type - 请求类型 (sent/received)
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.status - 请求状态 (pending/accepted/rejected)
 * @returns {Promise}
 */
export const getFriendRequests = (params = {}) => {
  return request({
    url: '/friends/requests',
    method: 'get',
    params
  })
}

/**
 * 处理好友请求
 * @param {number} requestId - 请求ID
 * @param {string} action - 操作 (accept/reject)
 * @returns {Promise}
 */
export const handleFriendRequest = (requestId, action) => {
  return request({
    url: `/friends/requests/${requestId}`,
    method: 'put',
    headers: {
      'Content-Type': 'application/json'
    },
    data: {
      action
    }
  })
}

/**
 * 获取好友列表
 * @returns {Promise}
 */
export const getFriends = () => {
  return request({
    url: '/friends',
    method: 'get'
  })
}