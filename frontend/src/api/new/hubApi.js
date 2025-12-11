// src/api/new/hubApi.js
// 中枢页相关API接口

import request from '@/utils/request'

/**
 * 获取用户基础信息
 * @returns {Promise} 用户数据（头像、昵称、统计等）
 */
export const getUserInfo = () => {
  return request({
    url: '/hub/user-info',
    method: 'get'
  })
}

/**
 * 获取附近胶囊列表
 * @param {Object} params - 查询参数
 * @param {number} params.lat - 纬度
 * @param {number} params.lng - 经度
 * @param {number} params.range - 搜索范围（米）
 * @param {number} params.page - 页码
 * @param {number} params.size - 每页数量
 * @returns {Promise} 附近胶囊列表
 */
export const getNearbyCapsules = (params = {}) => {
  return request({
    url: '/hub/nearby-capsules',
    method: 'get',
    params: {
      lat: params.lat || 39.9005,
      lng: params.lng || 116.302,
      range: params.range || 500,
      page: params.page || 1,
      size: params.size || 10
    }
  })
}

/**
 * 获取校园活动列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.size - 每页数量
 * @param {string} params.status - 活动状态筛选
 * @param {string} params.keyword - 搜索关键词
 * @returns {Promise} 校园活动列表
 */
export const getCampusEvents = (params = {}) => {
  // 临时返回空数据，等待后端实现events接口
  return Promise.resolve({
    success: true,
    data: {
      events: [],
      total: 0
    },
    message: "校园活动功能开发中"
  })
}

/**
 * 获取最近用户动态
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.size - 每页数量
 * @returns {Promise} 最近动态列表
 */
export const getRecentActivities = (params = {}) => {
  return request({
    url: '/hub/recent-activities',
    method: 'get',
    params: {
      page: params.page || 1,
      size: params.size || 10
    }
  })
}

/**
 * 获取用户统计数据
 * @returns {Promise} 用户统计信息
 */
export const getUserStats = () => {
  // 用户统计信息已包含在getUserInfo中
  return getUserInfo()
}

/**
 * 获取推荐胶囊
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 推荐数量限制
 * @returns {Promise} 推荐胶囊列表
 */
export const getRecommendedCapsules = (params = {}) => {
  // 临时返回空数据，推荐算法待实现
  return Promise.resolve({
    success: true,
    data: {
      capsules: [],
      total: 0
    },
    message: "推荐系统开发中"
  })
}