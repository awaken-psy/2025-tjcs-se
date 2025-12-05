// src/api/mapApi.js
// 地图页接口封装：胶囊地理数据、热力图、定位、上报位置
import request from '../utils/request.js'

/**
 * 获取校园胶囊地理标记数据（含经纬度、可见性等）
 * @param {Object} params - { lat, lng, range }
 * @returns {Promise<Array>} 胶囊地理数据列表
 */
export const getCapsuleMarkers = async (params = { lat: 39.9005, lng: 116.302, range: 1000 }) => {
  try {
    // 后端接口：/map/capsule-markers
    const data = await request({
      url: '/map/capsule-markers',
      method: 'get',
      params
    })
    return data
  } catch (error) {
    // 直接返回与后端一致的内置演示数据
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
      },
      {
        id: 2,
        title: '操场星空',
        lat: 39.900200,
        lng: 116.303000,
        time: '2024-07-10T21:00:00',
        vis: 'public',
        desc: '夏夜的操场，和朋友们一起数星星，聊梦想。',
        tags: ['操场', '星空', '梦想'],
        likes: 18,
        views: 120,
        location: '操场',
        distance: '100m',
        img: 'https://picsum.photos/id/1018/300/200',
        unlockType: 'location'
      },
      {
        id: 3,
        title: '实验室的清晨',
        lat: 39.901000,
        lng: 116.302500,
        time: '2024-09-01T06:00:00',
        vis: 'private',
        desc: '清 晨六点，实验室的灯已经亮起，奋斗的青春最美。',
        tags: ['实验', '清晨', '奋斗'],
        likes: 8,
        views: 60,
        location: '实验楼',
        distance: '100m',
        img: 'https://picsum.photos/id/1025/300/200',
        unlockType: 'time'
      },
      {
        id: 4,
        title: '食堂美食记',
        lat: 39.900600,
        lng: 116.302800,
        time: '2024-10-01T12:00:00',
        vis: 'friend',
        desc: '和同学们一起打卡食堂新菜，味道 棒极了！',
        tags: ['美食', '食堂', '同学'],
        likes: 25,
        views: 200,
        location: '第一食堂',
        distance: '100m',
        img: 'https://picsum.photos/id/1040/300/200',
        unlockType: 'location'
      }
    ]
  }
}

/**
 * 获取校园热力图数据（用于展示胶囊分布密度）
 * @returns {Promise<Array>} 热力图数据（格式：[[lng, lat, count], ...]）
 */
export const getHeatmapData = async () => {
  try {
    const data = await request({
      url: '/map/heatmap-data',
      method: 'get'
    })
    return data
  } catch (error) {
    // ...existing code...
    return [
      [116.301950, 39.900820, 8],
      [116.303100, 39.901250, 6],
      [116.302050, 39.899780, 10],
      [116.299850, 39.902100, 4],
      [116.304200, 39.900320, 7],
      [116.302500, 39.901500, 5],
      [116.301200, 39.900100, 3]
    ]
  }
}

/**
 * 获取用户当前位置的精确经纬度（可选后端辅助定位）
 * @returns {Promise<Object>} 用户位置（lat, lng）
 */
export const getUserLocation = async () => {
  try {
    const data = await request({
      url: '/map/user-location',
      method: 'get'
    })
    return data
  } catch (error) {
    // ...existing code...
    return {
      lat: 39.900500,
      lng: 116.302000
    }
  }
}

/**
 * 上报胶囊位置（创建胶囊时使用）
 * @param {Object} data - { capsuleId, lat, lng }
 * @returns {Promise<Object>} 上报结果
 */
export const reportCapsuleLocation = async (data) => {
  try {
    const result = await request({
      url: '/map/report-location',
      method: 'post',
      data
    })
    return result
  } catch (error) {
    // ...existing code...
    return {
      code: 200,
      message: '位置上报成功',
      data: {
        capsuleId: data.capsuleId,
        lat: data.lat,
        lng: data.lng,
        distance: Math.floor(Math.random() * 500) + 10
      }
    }
  }
}

/**
 * 创建胶囊（共用接口，供其他API调用）
 * @param {Object} data - 胶囊表单数据
 * @returns {Promise<Object>} 创建结果
 */
export const createCapsule = async (data) => {
  console.log('🚀 [MAP API DEBUG] createCapsule called with data:', data)

  // 只校验必填项
  if (!data.title || !data.content || !data.visibility) {
    console.error('❌ [MAP API DEBUG] Validation failed: missing required fields')
    throw new Error('标题、内容、可见性为必填项')
  }

  // 构造新API格式的数据对象
  const payload = {
    title: data.title,
    content: data.content,
    visibility: data.visibility,
    tags: data.tags || [],
    location: (data.location?.latitude && data.location?.longitude) ? {
      latitude: data.location.latitude,
      longitude: data.location.longitude,
      address: data.location.address || ''
    } : null,
    unlock_conditions: data.unlock_conditions || null,
    media_files: data.media_files || []
  }

  console.log('📦 [MAP API DEBUG] 发送到后端的胶囊数据（新API格式）:', payload)
  console.log('🔐 [MAP API DEBUG] Current localStorage token:', localStorage.getItem('user_token') ? 'EXISTS' : 'MISSING')

  try {
    // 使用统一的request方法，确保认证和错误处理
    const result = await request({
      url: '/capsules/',  // 添加尾部斜杠避免307重定向
      method: 'post',
      data: payload
    })
    console.log('✅ [MAP API DEBUG] 胶囊创建成功:', result)
    return result
  } catch (error) {
    console.error('❌ [MAP API DEBUG] 胶囊创建失败:', error)
    throw error
  }
}
