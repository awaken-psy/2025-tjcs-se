// src/api/hubApi.js
// 中枢页接口封装：用户信息、附近胶囊、校园活动、最近动态
import request from '../utils/request.js'

/**
 * 获取用户基础信息
 * @returns {Promise<Object>} 用户数据（头像、昵称、统计等）
 */
export const getUserInfo = async() => {
  try {
    const data = await request({ url: '/hub/user-info', method: 'get' })
    return data
  } catch (error) {
    // ...existing code...
    return {
      id: 'u_1001',
      name: '时光旅行者',
      avatar: 'https://picsum.photos/id/237/200/200',
      stats: {
        totalCapsules: 12,
        pendingCapsules: 3,
        followers: 128,
        activeToday: 124
      },
      bio: '热爱记录校园生活的时光旅行者，用胶囊珍藏每一个美好瞬间～'
    }
  }
}

/**
 * 获取附近胶囊列表
 * @param {Object} params - { lat, lng, range }
 * @returns {Promise<Array>} 附近胶囊列表
 */
export const getNearbyCapsules = async(params = { lat: 39.9005, lng: 116.302, range: 500 }) => {
  try {
    const data = await request({ url: '/hub/nearby-capsules', method: 'get', params })
    return data
  } catch (error) {
    // ...existing code...
    return [
      {
        id: 'c_2001',
        title: '图书馆通宵回忆',
        time: '2024-06-15T22:30:00',
        vis: 'public',
        desc: '毕业前的最后一个夜晚，在图书馆度过了四年最难忘的时光...',
        tags: ['学习', '图书馆', '毕业'],
        likes: 42,
        views: 328,
        location: '图书馆西侧',
        distance: '28m',
        img: 'https://picsum.photos/id/24/300/200',
        unlockType: 'location'
      },
      // ...更多模拟数据...
    ]
  }
}

/**
 * 获取校园活动列表
 * @param {Object} params - { page, size }
 * @returns {Promise<Array>} 校园活动列表
 */
export const getCampusEvents = async(params = { page: 1, size: 10 }) => {
  try {
    const res = await request({ url: '/events/list', method: 'get', params })
    // 兼容 res.data.list、res.list 两种结构
    const list = res.data?.list || res.list || []
    return list.map(ev => ({
      id: ev.id,
      name: ev.name,
      date: ev.date,
      desc: ev.description,
      tags: ev.tags,
      coverImg: ev.cover_img,
      location: ev.location,
      participantCount: ev.participant_count
    }))
  } catch (error) {
    // ...existing code...
    return []
  }
}

/**
 * 获取最近用户动态
 * @returns {Promise<Array>} 最近动态列表
 */
export const getRecentActivities = async() => {
  try {
    const data = await request({ url: '/hub/recent-activities', method: 'get' })
    return data
  } catch (error) {
    // ...existing code...
    return [
      {
        id: 'act_4001',
        time: '2024-10-24T14:30:00',
        user: '时光旅行者',
        userAvatar: 'https://picsum.photos/id/237/40/40',
        action: '创建胶囊',
        details: '图书馆通宵回忆',
        relatedId: 'c_2001'
      },
      // ...更多模拟数据...
    ]
  }
}
