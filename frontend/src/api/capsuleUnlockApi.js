// src/api/capsuleUnlockApi.js
// 胶囊解锁相关API接口

import request from '@/utils/request'

/**
 * 获取周围的可解锁胶囊
 * @param {Object} params - 查询参数
 * @param {number} params.lat - 纬度
 * @param {number} params.lng - 经度
 * @param {number} params.radius - 搜索半径(米)
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise}
 */
export const getNearbyUnlockableCapsules = (params = {}) => {
  return request({
    url: '/unlock/nearby',
    method: 'get',
    params
  })
}

/**
 * 验证胶囊解锁条件
 * @param {string} capsuleId - 胶囊ID
 * @param {Object} currentLocation - 当前位置
 * @param {number} currentLocation.latitude - 纬度
 * @param {number} currentLocation.longitude - 经度
 * @returns {Promise}
 */
export const verifyUnlockCondition = (capsuleId, currentLocation) => {
  return request({
    url: `/unlock/${capsuleId}`,
    method: 'post',
    headers: {
      'Content-Type': 'application/json'
    },
    data: {
      current_location: currentLocation
    }
  })
}