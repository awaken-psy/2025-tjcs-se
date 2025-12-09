// src/api/authenticationApi.js
// 认证相关API接口

import request from '@/utils/request'

/**
 * 发送验证码
 * @param {Object} emailData - 邮箱数据
 * @param {string} emailData.email - 邮箱地址
 * @returns {Promise}
 */
export const sendCode = (emailData) => {
  return request({
    url: '/auth/sendcode',
    method: 'post',
    data: emailData
  })
}

/**
 * 用户注册
 * @param {Object} registerData - 注册数据
 * @param {string} registerData.email - 邮箱
 * @param {string} registerData.password - 加密后的密码
 * @param {string} registerData.nickname - 昵称
 * @param {string} registerData.student_id - 学号
 * @param {string} registerData.verify_code - 验证码
 * @returns {Promise}
 */
export const register = (registerData) => {
  return request({
    url: '/auth/register',
    method: 'post',
    data: registerData
  })
}

/**
 * 用户登录
 * @param {Object} loginData - 登录数据
 * @param {string} loginData.email - 邮箱
 * @param {string} loginData.password - 加密后的密码
 * @returns {Promise}
 */
export const login = (loginData) => {
  return request({
    url: '/auth/login',
    method: 'post',
    data: loginData
  })
}

// logout 在pinia的user store中调用
/**
 * 退出登录
 * @returns {Promise}
 */
export const logout = () => {
  return request({
    url: '/auth/logout',
    method: 'post',
    headers: {
      'Content-Type': 'application/json'
    }
  })
}


/**
 * 刷新令牌
 * @param {string} refreshToken - 刷新令牌
 * @returns {Promise}
 */
export const refreshToken = (refreshToken) => {
  return request({
    url: '/auth/refresh',
    method: 'post',
    data: {
      refresh_token: refreshToken
    }
  })
}