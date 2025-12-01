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
    url: '/capsules',
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

<<<<<<< HEAD
/**
 * 获取附近胶囊
 * @param {Object} params - 查询参数
 * @param {number} params.latitude - 纬度
 * @param {number} params.longitude - 经度
 * @param {number} params.radius_meters - 搜索半径（米）
 * @returns {Promise}
 */
export const getNearbyCapsules = (params) => {
  return request({
    url: '/capsules/nearby',
    method: 'get',
    params
  })
}

/**
 * 获取胶囊地理标记数据（兼容旧API）
 * @param {Object} params - 查询参数
 * @param {number} params.lat - 纬度
 * @param {number} params.lng - 经度
 * @param {number} params.range - 搜索范围（米）
 * @returns {Promise}
 */
export const getCapsuleMarkers = (params = { lat: 39.9005, lng: 116.302, range: 1000 }) => {
  // 转换参数格式适配新API
  return getNearbyCapsules({
    latitude: params.lat,
    longitude: params.lng,
    radius_meters: params.range
  }).then(result => {
    // 转换响应格式兼容旧代码
    if (result && result.capsules) {
      return result.capsules.map(capsule => ({
        id: capsule.id,
        title: capsule.title,
        lat: capsule.location?.latitude || params.lat,
        lng: capsule.location?.longitude || params.lng,
        time: capsule.created_at,
        vis: capsule.visibility,
        desc: capsule.title,
        tags: [],
        likes: 0,
        views: 0,
        location: capsule.location?.address || '未知位置',
        distance: capsule.location?.distance ? `${Math.round(capsule.location.distance)}m` : '计算中',
        img: 'https://picsum.photos/id/24/300/200',
        unlockType: 'location'
      }))
    }
    return []
  }).catch(() => {
    // 返回默认演示数据作为兼容
    return [
      {
        id: 1,
        title: '图书馆通宵回忆',
        lat: 39.900820,
        lng: 116.301950,
        time: '2024-06-15T22:30:00',
        vis: 'public',
        desc: '毕业前的最后一个夜晚，在图书馆度过了四年最难忘的时光...',
        tags: ['学习', '图书馆', '毕业'],
        likes: 42,
        views: 328,
        location: '图书馆西侧',
        distance: '100m',
        img: 'https://picsum.photos/id/24/300/200',
        unlockType: 'location'
      }
    ]
  })
}

/**
 * 获取热力图数据
 * @returns {Promise}
 */
export const getHeatmapData = () => {
  // 暂时返回模拟数据，可以后续扩展为真实API
  return Promise.resolve([
    [116.301950, 39.900820, 8],
    [116.303100, 39.901250, 6],
    [116.302050, 39.899780, 10],
    [116.299850, 39.902100, 4],
    [116.304200, 39.900320, 7],
    [116.302500, 39.901500, 5],
    [116.301200, 39.900100, 3]
  ])
}

/**
 * 获取用户位置
 * @returns {Promise}
 */
export const getUserLocation = () => {
  // 暂时返回默认位置，可以后续扩展为真实定位API
  return Promise.resolve({
    lat: 39.900500,
    lng: 116.302000
=======
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
>>>>>>> 261fedc (修改胶囊列表，详情弹窗等内容，更改capsuleform)
  })
}