// src/api/userStatusApi.js
// 用户状态相关API接口

import request from '@/utils/request'

/**
 * 用户注册
 * @param {Object} data - 注册数据
 * @param {string} data.email - 邮箱
 * @param {string} data.password - 密码
 * @param {string} data.nickname - 昵称
 * @param {string} data.student_id - 学号
 * @returns {Promise}
 */
export const registerUser = (data) => {
  return request({
    url: '/auth/register',
    method: 'post',
    headers: {
      'Content-Type': 'application/json'
    },
    data: data
  })
}

/**
 * 用户登录
 * @param {Object} data - 登录数据
 * @param {string} data.email - 邮箱
 * @param {string} data.password - 密码
 * @returns {Promise}
 */
export const loginUser = (data) => {
  return request({
    url: '/auth/login',
    method: 'post',
    headers: {
      'Content-Type': 'application/json'
    },
    data: data
  })
}

/**
 * 退出登录
 * @returns {Promise}
 */
export const logoutUser = () => {
  return request({
    url: '/auth/logout',
    method: 'post',
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

/**
 * 刷新认证令牌
 * @param {string} refreshToken - 刷新令牌
 * @returns {Promise}
 */
export const refreshAuthToken = (refreshToken) => {
  return request({
    url: '/auth/refresh',
    method: 'post',
    headers: {
      'Authorization': `Bearer ${refreshToken}`
    }
  })
}