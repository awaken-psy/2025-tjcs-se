// src/api/capsulesApi.js
// 胶囊相关API接口

import request from '@/utils/request'

/**
 * 创建胶囊
 * @param {Object} capsuleData - 胶囊数据
 * @param {string} capsuleData.title - 胶囊标题
 * @param {string} capsuleData.content - 胶囊内容
 * @param {string} capsuleData.visibility - 可见性 (private/public)
 * @param {Array} capsuleData.tags - 标签数组
 * @param {Object} capsuleData.location - 位置信息
 * @param {number} capsuleData.location.latitude - 纬度
 * @param {number} capsuleData.location.longitude - 经度
 * @param {string} capsuleData.location.address - 地址描述
 * @param {Object} capsuleData.unlock_conditions - 解锁条件
 * @param {string} capsuleData.unlock_conditions.type - 解锁类型
 * @param {string} capsuleData.unlock_conditions.value - 解锁值
 * @param {number} capsuleData.unlock_conditions.radius - 解锁半径
 * @param {string} capsuleData.unlock_conditions.event_id - 事件ID
 * @param {boolean} capsuleData.unlock_conditions.is_unlocked - 是否已解锁
 * @param {Array} capsuleData.media_files - 媒体文件ID数组
 * @returns {Promise}
 */
export const createCapsule = (capsuleData) => {
  return request({
    url: '/capsules/',  // 添加尾部斜杠避免307重定向
    method: 'post',
    data: capsuleData
  })
}

/**
 * 获取我的胶囊列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.status - 胶囊状态
 * @returns {Promise}
 */
export const getMyCapsules = (params = {}) => {
  return request({
    url: '/capsules/my',
    method: 'get',
    params
  })
}

/**
 * 浏览胶囊
 * @param {Object} params - 查询参数
 * @param {string} params.mode - 浏览模式
 * @param {string} params.tags - 标签筛选
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise}
 */
export const browseCapsules = (params = {}) => {
  return request({
    url: '/capsules/browse',
    method: 'get',
    params
  })
}

/**
 * 获取胶囊详情
 * @param {string} capsuleId - 胶囊ID
 * @returns {Promise}
 */
export const getCapsuleDetail = (capsuleId) => {
 
  return request({
    url: `/capsules/${capsuleId}`,
    method: 'get'
  })
}

/**
 * 更新胶囊
 * @param {string} capsuleId - 胶囊ID
 * @param {Object} capsuleData - 胶囊数据
 * @param {string} capsuleData.title - 胶囊标题
 * @param {string} capsuleData.content - 胶囊内容
 * @param {string} capsuleData.visibility - 可见性
 * @param {Array} capsuleData.tags - 标签数组
 * @returns {Promise}
 */
export const updateCapsule = (capsuleId, capsuleData) => {
  return request({
    url: `/capsules/${capsuleId}`,
    method: 'put',
    data: capsuleData
  })
}

/**
 * 删除胶囊
 * @param {string} capsuleId - 胶囊ID
 * @returns {Promise}
 */
export const deleteCapsule = (capsuleId) => {
  return request({
    url: `/capsules/${capsuleId}`,
    method: 'delete'
  })
}

/**
 * 创建胶囊草稿
 * @param {Object} draftData - 草稿数据
 * @param {string} draftData.title - 草稿标题
 * @param {string} draftData.content - 草稿内容
 * @param {string} draftData.visibility - 可见性
 * @returns {Promise}
 */
export const createCapsuleDraft = (draftData) => {
  return request({
    url: '/capsules/drafts',
    method: 'post',
    data: draftData
  })
}

//TODO:newapi
/**
 * 点赞/取消点赞胶囊
 * @param {string} capsuleId - 胶囊ID
 * @returns {Promise}
 */
export const likeCapsule = (capsuleId) => {
  return request({
    url: `/capsules/${capsuleId}/like`, // 假设的API路径
    method: 'post' // 或 put
  })
}

/**
 * 获取胶囊地图标记数据
 * @param {Object} params - 查询参数
 * @param {number} params.lat - 纬度
 * @param {number} params.lng - 经度
 * @param {number} params.range - 搜索范围（米）
 * @returns {Promise}
 */
export const getCapsuleMarkers = (params = {}) => {
  // 使用附近胶囊API获取地图标记数据
  return request({
    url: '/hub/nearby-capsules',
    method: 'get',
    params: {
      lat: params.lat || 31.2921302, // 默认位置：上海
      lng: params.lng || 121.2152746,
      range: params.range || 1000,
      page: 1,
      limit: 100
    }
  }).then(response => {
    // 将附近胶囊数据转换为地图标记格式
    const capsules = response.capsules || []
    return capsules.map(capsule => ({
      id: capsule.id,
      title: capsule.title,
      lat: capsule.location?.latitude,
      lng: capsule.location?.longitude,
      visibility: capsule.visibility,
      is_unlocked: capsule.is_unlocked,
      can_unlock: capsule.can_unlock,
      creator_nickname: capsule.creator_nickname,
      created_at: capsule.created_at,
      distance: capsule.location?.distance
    }))
  })
}

/**
 * 获取热力图数据
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export const getHeatmapData = (params = {}) => {
  // 暂时返回模拟数据，后续可以对接专门的热力图API
  return Promise.resolve([
    { lat: 31.2921302, lng: 121.2152746, intensity: 0.8 },
    { lat: 31.2931302, lng: 121.2162746, intensity: 0.6 },
    { lat: 31.2911302, lng: 121.2142746, intensity: 0.4 }
  ])
}

/**
 * 获取用户当前位置
 * @returns {Promise}
 */
export const getUserLocation = () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      resolve({ lat: 31.2921302, lng: 121.2152746 }) // 默认位置
      return
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          lat: position.coords.latitude,
          lng: position.coords.longitude
        })
      },
      (error) => {
        console.warn('获取用户位置失败:', error)
        resolve({ lat: 31.2921302, lng: 121.2152746 }) // 默认位置
      },
      {
        timeout: 10000,
        enableHighAccuracy: true,
        maximumAge: 300000 // 5分钟缓存
      }
    )
  })
}