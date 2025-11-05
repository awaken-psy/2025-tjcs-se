/**
 * 工具函数作用：
 * 统一项目中时间格式化逻辑，避免重复代码，支持：
 * 1. 标准日期格式化（如"2024年06月15日 22:30"）
 * 2. 相对时间格式化（如"刚刚"、"3小时前"、"2天前"）
 * 
 * 函数列表：
 * 1. formatStandard(isoStr)：将ISO时间字符串转为标准格式
 * 2. formatRelative(isoStr)：将ISO时间字符串转为相对时间
 * 
 * 调用方式：
 * import { formatStandard, formatRelative } from '@/utils/formatTime.js';
 * const standardTime = formatStandard('2024-06-15T22:30:00');
 * const relativeTime = formatRelative('2024-06-15T22:30:00');
 */

/**
 * 标准日期格式化
 * @param {String} isoStr - ISO格式时间字符串（如"2024-06-15T22:30:00"）
 * @returns {String} 格式化后的时间（如"2024年06月15日 22:30"）
 */
export const formatStandard = (isoStr) => {
  try {
    if (!isoStr) return ''
    const date = new Date(isoStr)
    if (isNaN(date.getTime())) return isoStr
    const y = date.getFullYear()
    const m = String(date.getMonth() + 1).padStart(2, '0')
    const d = String(date.getDate()).padStart(2, '0')
    const h = String(date.getHours()).padStart(2, '0')
    const min = String(date.getMinutes()).padStart(2, '0')
    return `${y}年${m}月${d}日 ${h}:${min}`
  } catch (error) {
    console.warn('时间格式化失败：', error)
    return isoStr
  }
}

/**
 * 相对时间格式化
 * @param {String} isoStr - ISO格式时间字符串（如"2024-06-15T22:30:00"）
 * @returns {String} 相对时间（如"刚刚"、"3小时前"、"2天前"）
 */
export const formatRelative = (isoStr) => {
  try {
    if (!isoStr) return ''
    const date = new Date(isoStr)
    if (isNaN(date.getTime())) return isoStr
    const now = new Date()
    const diffMs = now - date
    const diffSec = Math.floor(diffMs / 1000)
    const diffMin = Math.floor(diffSec / 60)
    const diffHour = Math.floor(diffMin / 60)
    const diffDay = Math.floor(diffHour / 24)
    const diffWeek = Math.floor(diffDay / 7)
    if (diffSec < 60) return '刚刚'
    if (diffMin < 60) return `${diffMin}分钟前`
    if (diffHour < 24) return `${diffHour}小时前`
    if (diffDay < 7) return `${diffDay}天前`
    if (diffWeek < 4) return `${diffWeek}周前`
    return formatStandard(isoStr)
  } catch (error) {
    console.warn('相对时间格式化失败：', error)
    return isoStr
  }
}
