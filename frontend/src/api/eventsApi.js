// src/api/eventsApi.js
// 校园活动页接口封装：专注校园活动的列表、详情、报名、取消报名、我的报名
import request from '../utils/request.js'
import { getCampusEvents as hubGetCampusEvents } from './hubApi.js'

const formatEventData = (event) => {
  return {
    id: event.id,
    name: event.name,
    time: event.date,
    description: event.description,
    tags: typeof event.tags === 'string' ? event.tags.split(',') : (event.tags || []),
    coverImg: event.cover_img,
    location: event.location,
    participantCount: event.participant_count,
    isRegistered: event.is_registered || false,
  }
}

// 套壳函数，实际调用 hubApi.js 的 getCampusEvents
export const getCampusEvents = async(params = { page: 1, size: 10, keyword: '' }) => {
  return await hubGetCampusEvents(params)
}

export const getEventDetail = async(eventId) => {
  try {
    const res = await request({
      url: `/events/detail/${eventId}`,
      method: 'get'
    })
    return formatEventData(res.data)
  } catch (error) {
    console.error('获取活动详情失败：', error)
    return null
  }
}

export const registerEvent = async(eventId) => {
  try {
    const res = await request({
      url: `/events/register/${eventId}`,
      method: 'post'
    })
    return res.data
  } catch (error) {
    console.error('报名失败：', error)
    return { code: 500, message: '报名失败', data: {} }
  }
}

export const cancelRegister = async(eventId) => {
  try {
    const res = await request({
      url: `/events/cancel/${eventId}`,
      method: 'post'
    })
    return res.data
  } catch (error) {
    console.error('取消报名失败：', error)
    return { code: 500, message: '取消报名失败', data: {} }
  }
}

export const getMyRegisteredEvents = async(params = { page: 1, size: 10 }) => {
  try {
    const res = await request({
      url: '/events/my-registered',
      method: 'get',
      params
    })
    const list = Array.isArray(res.data?.list) ? res.data.list : []
    return {
      list: list.map(formatEventData),
      total: res.data?.total || list.length
    }
  } catch (error) {
    console.error('获取已报名活动失败：', error)
    return { list: [], total: 0 }
  }
}
