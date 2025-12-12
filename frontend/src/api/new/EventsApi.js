// src/api/eventsApi.js
// 活动相关API接口

import request from '@/utils/request'

/**
 * 创建新活动
 * @param {Object} eventData - 活动数据
 * @param {string} eventData.name - 活动名称 
 * @param {string} eventData.description - 活动描述
 * @param {string} eventData.date - 活动时间 (ISO 8601 格式, 例如: "2024-05-20T19:00:00Z")
 * @param {string} eventData.location - 活动地点
 * @param {string[]} eventData.tags - 活动标签列表 (例如: ["音乐", "文化"])
 * @param {string} [eventData.cover_img] - 活动封面图 URL (可选)
 * @returns {Promise} - 返回新创建的活动对象
 */
export const createEvent = (eventData) => {
    return request({
        url: '/events/',  // 添加尾部斜杠避免307重定向
        method: 'post',
        data: eventData
    })
}

/**
 * 更新现有活动
 * @param {string} eventId - 要更新的活动ID
 * @param {Object} eventData - 活动更新数据
 * @param {string} [eventData.name] - 活动名称
 * @param {string} [eventData.description] - 活动描述
 * @param {string} [eventData.date] - 活动时间 (ISO 8601 格式)
 * @param {string} [eventData.location] - 活动地点
 * @param {string[]} [eventData.tags] - 活动标签列表
 * @param {string} [eventData.cover_img] - 活动封面图 URL
 * @returns {Promise} - 返回更新后的活动对象
 */
export const updateEvent = (eventId, eventData) => {
    return request({
        url: `/events/${eventId}`,
        method: 'put',
        data: eventData
    })
}


/**
 * 注册/报名活动
 * @param {string} eventId - 要注册的活动ID 
 * @returns {Promise} - 返回报名成功后的信息或状态
 */
export const registerForEvent = (eventId) => {
    return request({
        url: `/events/${eventId}/register`,
        method: 'post'
    })
}

/**
 * 取消活动报名 
 * @param {string} eventId - 要取消报名的活动ID 
 * @returns {Promise} - 返回取消报名成功后的信息或状态
 */
export const cancelEventRegistration = (eventId) => {
    return request({
        url: `/events/${eventId}/cancel`,
        method: 'post'
    })
}

/**
 * 获取活动列表
 * @param {Object} [params] - 查询参数 (所有参数均为可选)
 * @param {number} [params.page] - 页码
 * @param {number} [params.size] - 每页数量
 * @param {string} [params.keyword] - 搜索关键词
 * @param {string} [params.status] - 活动状态过滤 
 * @param {string} [params.sort] - 排序方式 
 * @param {string} [params.startTime] - 开始时间过滤 (ISO 8601 格式)
 * @param {string} [params.endTime] - 结束时间过滤 (ISO 8601 格式)
 * @returns {Promise} - 返回活动列表数据，通常包含列表数组和分页信息
 */
export const getEventList = (params = {}) => {
    return request({
        url: '/events/',  // 添加尾部斜杠避免307重定向
        method: 'get',
        params: params
    })
}


/**
 * 获取活动详情 
 * @param {string} eventId - 要获取详情的活动ID
 * @returns {Promise}
 */
export const getEventDetail = (eventId) => {
    return request({
        url: `/events/${eventId}`,
        method: 'get'
    })
}

/**
 * 获取当前用户已报名的活动列表
 * @param {Object} [params] - 查询参数 (可选)
 * @param {number} [params.page] - 页码
 * @param {number} [params.page_size] - 每页数量
 * @returns {Promise} - 返回已注册活动的列表数据
 */
export const getMyRegisteredEvents = (params = {}) => {
    return request({
        url: '/events/my-registered',
        method: 'get',
        params: params
    })
}

/**
 * 删除特定活动 
 * @param {string} eventId - 要删除的活动ID
 * @returns {Promise} - 返回删除成功后的信息或状态 (通常是空对象或成功状态码)
 */
export const deleteEvent = (eventId) => {
    return request({
        url: `/events/${eventId}`,
        method: 'delete'
    })
}