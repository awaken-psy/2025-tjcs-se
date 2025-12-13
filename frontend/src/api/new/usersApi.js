// src/api/usersApi.js
// 用户相关API接口


import request from '@/utils/request'

/**
 * 获取当前用户信息
 * @returns {Promise}
 */
/*响应示例:
{
        "user_id": 123,
        "email": "user@example.com",
        "nickname": "用户昵称",
        "avatar": "https://example.com/avatar.jpg",
        "bio": "个人简介",
        "stats": {
            "created_capsules": 15,
            "unlocked_capsules": 42,
            "collected_capsules": 8,
            "friends_count": 23
        },
        "created_at": "2024-01-01T00:00:00Z"
    }*/
export const getCurrentUser = () => {
  return request({
    url: '/users/me',
    method: 'get'
  })
}



/**
 * 更新当前用户信息
 * @param {Object} userData - 用户数据
 * @param {string} userData.nickname - 昵称
 * @param {string} userData.avatar - 头像URL
 * @param {string} userData.bio - 个人简介
 * @returns {Promise}
 */
export const updateCurrentUser = (userData) => {
  return request({
    url: '/users/me',
    method: 'put',
    data: userData
  })
}

/**
 * 获取用户历史记录
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.sort - 排序方式
 * @param {string} params.type - 记录类型
 * @returns {Promise}
 */
/*响应示例:
{
        "history": [
            {
                "capsule_id": "capsule_123",
                "title": "胶囊标题",
                "unlocked_at": "2024-01-15T10:30:00Z",
                "view_duration": 120
            }
        ]
    }*/
export const getUserHistory = (params = {}) => {
  return request({
    url: '/users/me/history',
    method: 'get',
    params
  })
}

/**
 * 搜索用户
 * @param {Object} params - 查询参数
 * @param {string} params.q - 搜索关键词
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise}
 */
/*响应示例:
{
        "users": [
            {
                "user_id": 123,
                "nickname": "用户昵称",
                "avatar": "https://example.com/avatar.jpg",
                "is_friend": false,
                "friend_status": "none"
            }
        ]
    }*/
export const searchUsers = (params = {}) => {
  return request({
    url: '/users/search',
    method: 'get',
    params
  })
}