// src/api/unlockApi.js
// 解锁相关API接口

import request from '@/utils/request'

/**
 * 检查可解锁胶囊
 * @param {Object} params - 查询参数
 * @param {Object} params.user_location - 用户当前位置
 * @param {number} params.user_location.latitude - 纬度
 * @param {number} params.user_location.longitude - 经度
 * @param {string} params.user_location.address - 地址（可选）
 * @param {number} params.max_distance_meters - 最大查询距离
 * @param {string} params.current_time - 当前时间（可选）
 * @param {string} params.password - 解锁密码（可选）
 * @returns {Promise}
 */
export const checkUnlockableCapsules = async (params = {}) => {
  return await request({
    url: '/unlock/check',
    method: 'post',
    data: {
      user_location: {
        latitude: params.user_location?.latitude || params.lat || 0,
        longitude: params.user_location?.longitude || params.lng || 0,
        address: params.user_location?.address || '',
      },
      max_distance_meters: params.max_distance_meters || 1000,
      current_time: params.current_time,
      password: params.password, // 新增 password 字段
    },
  })
}

// src/api/unlockApi.js
/**
 * 解锁胶囊
 * @param {Object} params - 解锁参数
 * @param {string} params.capsule_id - 胶囊ID
 * @param {Object} params.user_location - 用户当前位置（可选）
 * @param {Object} params.current_location - 用户当前位置（可选，优先使用）
 * @param {number} params.user_location?.latitude - 纬度
 * @param {number} params.user_location?.longitude - 经度
 * @param {string} params.current_time - 当前时间（可选）
 * @param {string} params.password - 解锁密码（可选）
 * @returns {Promise}
 */
export const unlockCapsule = async (params = {}) => {
  // 优先使用 current_location，如果没有则使用 user_location
  const locationData = params.current_location || params.user_location

  return await request({
    url: `/unlock/${params.capsule_id}`,
    method: 'post',
    data: {
      current_location: locationData, // 确保字段名正确
      current_time: params.current_time,
      password: params.password, // 新增 password 字段
    },
  })
}

/**
 * 获取附近的可解锁项目（兼容旧版本）
 * @param {Object} params - 查询参数
 * @param {number} params.lat - 纬度
 * @param {number} params.lng - 经度
 * @param {number} params.radius - 搜索半径
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.password - 解锁密码（可选）
 * @returns {Promise}
 */
export const getNearbyUnlocks = (params = {}) => {
  // 转换为新的API格式
  return checkUnlockableCapsules({
    user_location: {
      latitude: params.lat || 0,
      longitude: params.lng || 0,
      address: '',
    },
    max_distance_meters: params.radius || 1000,
    password: params.password, // 传递 password
  })
}

/**
 * 获取附近胶囊（直接调用后端/unlock/nearby API）
 * @param {Object} params - 查询参数
 * @param {number} params.latitude - 纬度
 * @param {number} params.longitude - 经度
 * @param {number} params.radius_meters - 搜索半径（米）
 * @param {number} params.page - 页码
 * @param {number} params.limit - 每页数量
 * @returns {Promise}
 */
export const getNearbyCapsulesDirect = (params = {}) => {
  return request({
    url: '/unlock/nearby',
    method: 'get',
    params: {
      latitude: params.latitude || params.lat || 39.9005,
      longitude: params.longitude || params.lng || 116.302,
      radius_meters: params.radius_meters || params.radius || 10000,
      page: params.page || 1,
      limit: params.limit || params.page_size || 10
    }
  })
}

/**
 * 解锁项目（兼容旧版本）
 * @param {Object} currentLocation - 当前位置信息
 * @param {number} currentLocation.latitude - 纬度
 * @param {number} currentLocation.longitude - 经度
 * @param {string} capsuleId - 胶囊ID（可选）
 * @param {string} password - 解锁密码（可选）
 * @returns {Promise}
 */
export const unlockItem = async (
  currentLocation,
  capsuleId = null,
  password = null
) => {
  if (capsuleId) {
    return await unlockCapsule({
      capsule_id: capsuleId,
      user_location: currentLocation,
      password: password, // 传递 password
    })
  } else {
    // 如果没有提供胶囊ID，先检查可解锁的胶囊
    const checkResult = await checkUnlockableCapsules({
      user_location: currentLocation,
      max_distance_meters: 100,
      password: password, // 传递 password
    })

    if (checkResult.success && checkResult.unlockable_count > 0) {
      // 自动解锁第一个可解锁的胶囊
      const firstCapsule = checkResult.unlockable_capsules[0]
      return await unlockCapsule({
        capsule_id: firstCapsule.capsule_id,
        user_location: currentLocation,
        password: password, // 传递 password
      })
    }

    return {
      success: false,
      message: '附近没有可解锁的胶囊',
    }
  }
}
