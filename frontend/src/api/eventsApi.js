// src/api/eventsApi.js
// 校园活动相关API接口

import request from '@/utils/request'
import { getCampusEvents as hubGetCampusEvents } from './hubApi.js'

/**
 * 获取校园活动列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.size - 每页数量
 * @param {string} params.keyword - 搜索关键词
 * @param {string} params.status - 活动状态过滤
 * @param {string} params.sort - 排序方式
 * @param {string} params.startTime - 开始时间过滤
 * @param {string} params.endTime - 结束时间过滤
 * @returns {Promise}
 */
export const getCampusEvents = (params = {}) => {
  return request({
    url: `/events`,
    method: 'get'
  })
}

/**
 * 获取活动详情
 * @param {string} eventId - 活动ID
 * @returns {Promise}
 */
export const getEventDetail = (eventId) => {
  return request({
    url: `/events/${eventId}`,
    method: 'get'
  })
}

/**
 * 报名活动
 * @param {string} eventId - 活动ID
 * @returns {Promise}
 */
export const registerEvent = (eventId) => {
  return request({
    url: `/events/${eventId}/register`,
    method: 'post'
  })
}

/**
 * 取消报名
 * @param {string} eventId - 活动ID
 * @returns {Promise}
 */
export const cancelRegister = (eventId) => {
  return request({
    url: `/events/${eventId}/cancel`,
    method: 'post'
  })
}

/**
 * 获取我已报名的活动列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise}
 */
export const getMyRegisteredEvents = (params = {}) => {
  return request({
    url: '/events/my-registered',
    method: 'get',
    params
  })
}

/**
 * 创建活动
 * @param {Object} eventData - 活动数据
 * @param {string} eventData.name - 活动名称
 * @param {string} eventData.description - 活动描述
 * @param {string} eventData.date - 活动时间
 * @param {string} eventData.location - 活动地点
 * @param {Array} eventData.tags - 活动标签
 * @param {string} eventData.cover_img - 封面图片
 * @returns {Promise}
 */
export const createEvent = (eventData) => {
  return request({
    url: '/events',
    method: 'post',
    data: eventData
  })
}

/**
 * 更新活动
 * @param {string} eventId - 活动ID
 * @param {Object} eventData - 活动数据
 * @returns {Promise}
 */
export const updateEvent = (eventId, eventData) => {
  return request({
    url: `/events/${eventId}`,
    method: 'put',
    data: eventData
  })
}

/**
 * 删除活动
 * @param {string} eventId - 活动ID
 * @returns {Promise}
 */
export const deleteEvent = (eventId) => {
  return request({
    url: `/events/${eventId}`,
    method: 'delete'
  })
}