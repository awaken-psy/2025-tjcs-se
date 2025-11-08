// src/api/user.js
// 用户相关 API 示例
import axios from 'axios'

// 获取用户信息
export function getUserInfo(userId) {
  return axios.get(`/api/user/${userId}`)
}
