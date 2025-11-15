// src/api/userApi.js
// 用户相关API接口

import request from '@/utils/request'

/**
 * 获取当前用户信息
 * @returns {Promise}
 */
export const getCurrentUser = () => {
  return request({
    url: '/users/me',
    method: 'get'
  })
}

/**
 * 更新当前用户信息
 * @param {Object} userData - 用户数据
 * @param {string} userData.nickname - 昵称
 * @param {string} userData.avatar - 头像URL
 * @param {string} userData.bio - 个人简介
 * @returns {Promise}
 */
export const updateCurrentUser = (userData) => {
  return request({
    url: '/users/me',
    method: 'put',
    headers: {
      'Content-Type': 'application/json'
    },
    data: userData
  })
}

/**
 * 获取用户访问历史
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.sort - 排序方式
 * @param {string} params.type - 历史类型 (view/like/comment等)
 * @returns {Promise}
 */
export const getUserHistory = (params = {}) => {
  return request({
    url: '/users/me/history',
    method: 'get',
    params
  })
}

/**
 * 搜索用户
 * @param {Object} params - 查询参数
 * @param {string} params.q - 搜索关键词
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise}
 */
export const searchUsers = (params = {}) => {
  return request({
    url: '/users/search',
    method: 'get',
    params
  })
}