
// ===============================
// 1. 页面级引用（在vue页面直接import）
//    例：import { loginByEmail } from '@/api/auth'
// 2. 专属API文件（本文件只负责LoginView相关接口）
// 3. 格式规范层（所有接口返回/入参有注释和类型说明，必要时有格式化函数）
// 4. 请求适配层（所有请求都通过统一request.js发起，便于全局拦截和联调）
// ===============================
import request from '@/utils/request.js'

/**
 * 辅助函数：格式化登录/注册后端返回的用户数据（如有需要可扩展）
 * @param {Object} data - 后端返回的原始数据
 * @returns {Object} 统一格式的用户信息
 */
export const formatAuthUser = (data) => {
  return {
    token: data.token || '',
    userInfo: {
      id: data.userInfo?.id || '',
      email: data.userInfo?.email || '',
      nickname: data.userInfo?.nickname || '',
      avatar: data.userInfo?.avatar || '',
      role: data.userInfo?.role || 'user', // 新增权限字段，默认普通用户
      // 可扩展更多字段
    }
  }
}

/**
 * 1. 发送邮箱验证码（注册/找回密码）
 * @param {String} email - 目标邮箱
 * @param {String} type - 验证码类型（register/forgot）
 * @returns {Promise<Object>} 发送结果
 */
export const sendEmailCode = async(email, type = 'register') => {
  return request({
    url: '/auth/send-code',
    method: 'post',
    data: { email, type }
  })
}

/**
 * 2. 邮箱注册
 * @param {Object} params - 注册参数
 * @param {String} params.email - 邮箱
 * @param {String} params.code - 验证码
 * @param {String} params.password - 密码
 * @param {String} [params.nickname] - 昵称（可选）
 * @returns {Promise<Object>} 注册结果（含token和用户信息）
 */
export const registerByEmail = async(params) => {
  return request({
    url: '/auth/register',
    method: 'post',
    data: params
  })
}

/**
 * 3. 邮箱登录
 * @param {String} email - 邮箱
 * @param {String} password - 密码
 * @returns {Promise<Object>} 登录结果（含token和用户信息）
 */
export const loginByEmail = async(email, password) => {
  return request({
    url: '/auth/login',
    method: 'post',
    data: { email, password }
  })
}

/**
 * 4. 找回密码（重置密码邮件）
 * @param {String} email - 邮箱
 * @returns {Promise<Object>} 发送结果
 */
export const sendForgotPassword = async(email) => {
  return request({
    url: '/auth/forgot',
    method: 'post',
    data: { email }
  })
}

/**
 * 5. 重置密码
 * @param {Object} params - 重置参数
 * @param {String} params.email - 邮箱
 * @param {String} params.code - 验证码
 * @param {String} params.newPassword - 新密码
 * @returns {Promise<Object>} 重置结果
 */
export const resetPassword = async(params) => {
  return request({
    url: '/auth/reset',
    method: 'post',
    data: params
  })
}
