// src/api/eventsApi.js
// 活动相关API接口

import request from '@/utils/request' // 确保路径正确指向您的 request.js 文件

/**
 * 创建新活动
 * @param {Object} eventData - 活动数据
 * @param {string} eventData.name - 活动名称 (例如: "校园音乐节")
 * @param {string} eventData.description - 活动描述
 * @param {string} eventData.date - 活动时间 (ISO 8601 格式, 例如: "2024-05-20T19:00:00Z")
 * @param {string} eventData.location - 活动地点
 * @param {string[]} eventData.tags - 活动标签列表 (例如: ["音乐", "文化"])
 * @param {string} [eventData.cover_img] - 活动封面图 URL (可选)
 * @returns {Promise<Object>} - 返回新创建的活动对象
 */
export const createEvent = (eventData) => {
    return request({
        // 对应您的 URL: http://123.60.47.101:8000/api/v1/events
        // 假设 request.js 中的 baseURL 为 '/api'，这里填写 '/v1/events'
        url: '/v1/events',
        method: 'post',
        data: eventData // 将活动数据作为请求体发送
    })
}

/**
 * 更新现有活动 (PUT 请求)
 * @param {string} eventId - 要更新的活动ID (对应示例中的 '$' 占位符)
 * @param {Object} eventData - 活动更新数据
 * @param {string} [eventData.name] - 活动名称
 * @param {string} [eventData.description] - 活动描述
 * @param {string} [eventData.date] - 活动时间 (ISO 8601 格式)
 * @param {string} [eventData.location] - 活动地点
 * @param {string[]} [eventData.tags] - 活动标签列表
 * @param {string} [eventData.cover_img] - 活动封面图 URL
 * @returns {Promise<Object>} - 返回更新后的活动对象
 */
export const updateEvent = (eventId, eventData) => {
    return request({
        // URL 结构：/v1/events/{eventId}
        // 您的示例 URL 是 '.../api/v1/events/$'，这里用 eventId 替代 '$'
        url: `/v1/events/${eventId}`,
        method: 'put', // 注意这里是 PUT 方法
        data: eventData // 将更新数据作为请求体发送
    })
}


/**
 * 注册/报名活动 (POST 请求)
 * @param {string} eventId - 要注册的活动ID (对应示例中的 '$' 占位符)
 * @returns {Promise<Object>} - 返回报名成功后的信息或状态
 */
export const registerForEvent = (eventId) => {
    return request({
        // URL 结构：/v1/events/{eventId}/register
        // 假设 request.js 中的 baseURL 已经处理了 '/api' 部分
        url: `/v1/events/${eventId}/register`,
        method: 'post'
        // 注意：您的示例中没有 data，表示这是一个空请求体的 POST 请求
    })
}

/**
 * 取消活动报名 (POST 请求)
 * @param {string} eventId - 要取消报名的活动ID (对应示例中的 '$' 占位符)
 * @returns {Promise<Object>} - 返回取消报名成功后的信息或状态
 */
export const cancelEventRegistration = (eventId) => {
    return request({
        // URL 结构：/v1/events/{eventId}/cancel
        // 假设 request.js 中的 baseURL 已经处理了 '/api' 部分
        url: `/v1/events/${eventId}/cancel`,
        method: 'post' // 您的示例中使用的是 POST 方法
        // 注意：您的示例中没有 data，表示这是一个空请求体的 POST 请求
    })
}

/**
 * 获取活动列表 (GET 请求)
 * @param {Object} [params] - 查询参数 (所有参数均为可选)
 * @param {number} [params.page] - 页码
 * @param {number} [params.size] - 每页数量
 * @param {string} [params.keyword] - 搜索关键词
 * @param {string} [params.status] - 活动状态过滤 (例如: 'active', 'finished')
 * @param {string} [params.sort] - 排序方式 (例如: 'date_desc', 'popularity_asc')
 * @param {string} [params.startTime] - 开始时间过滤 (ISO 8601 格式)
 * @param {string} [params.endTime] - 结束时间过滤 (ISO 8601 格式)
 * @returns {Promise<Object>} - 返回活动列表数据，通常包含列表数组和分页信息
 */
export const getEventList = (params = {}) => {
    return request({
        // URL 结构：/v1/events
        // 假设 request.js 中的 baseURL 已经处理了 '/api' 部分
        url: '/v1/events',
        method: 'get',
        params: params // axios/request 会自动将这个对象序列化为 URL 查询参数 (?page=...&size=...)
    })
}


/**
 * 获取活动详情 (GET 请求)
 * @returns {Promise<Object>} - 返回活动列表数据
 */
export const getAllEvents = () => {
    return request({
        // URL 结构：/v1/events/ (您的示例中 URL 结尾有斜杠)
        // 假设 request.js 中的 baseURL 已经处理了 '/api' 部分
        url: '/v1/events/',
        method: 'get'
        // 没有 params，表示请求体和查询参数都为空
    })
}

/**
 * 获取当前用户已报名的活动列表 (GET 请求)
 * (该接口通常需要用户已登录，request.js 中的拦截器应自动附加认证信息)
 * @param {Object} [params] - 查询参数 (可选)
 * @param {number} [params.page] - 页码
 * @param {number} [params.page_size] - 每页数量
 * @returns {Promise<Object>} - 返回已注册活动的列表数据
 */
export const getMyRegisteredEvents = (params = {}) => {
    return request({
        // URL 结构：/v1/events/my-registered
        // 假设 request.js 中的 baseURL 已经处理了 '/api' 部分
        url: '/v1/events/my-registered',
        method: 'get',
        params: params // axios/request 会自动将这个对象序列化为 URL 查询参数 (?page=...&page_size=...)
    })
}

/**
 * 删除特定活动 (DELETE 请求)
 * @param {string} eventId - 要删除的活动ID
 * @returns {Promise<Object>} - 返回删除成功后的信息或状态 (通常是空对象或成功状态码)
 */
export const deleteEvent = (eventId) => {
    return request({
        // URL 结构：/v1/events/{eventId}
        // 我们需要将 eventId 拼接到 URL 后面以指定删除目标
        url: `/v1/events/${eventId}`,
        method: 'delete'
    })
}