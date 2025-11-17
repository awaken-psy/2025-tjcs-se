// src/api/unlockApi.js
// 解锁相关API接口

import request from '@/utils/request'

/**
 * 获取附近的可解锁项目
 * @param {Object} params - 查询参数
 * @param {number} params.lat - 纬度
 * @param {number} params.lng - 经度
 * @param {number} params.radius - 搜索半径
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise}
 */
export const getNearbyUnlocks = (params = {}) => {
  return request({
    url: '/unlock/nearby',
    method: 'get',
    params
  })
}

/**
 * 解锁项目
 * @param {Object} currentLocation - 当前位置信息
 * @param {number} currentLocation.latitude - 纬度
 * @param {number} currentLocation.longitude - 经度
 * @returns {Promise}
 */
export const unlockItem = (currentLocation) => {
  return request({
    url: '/unlock/',
    method: 'post',
    data: {
      current_location: currentLocation
    }
  })
}