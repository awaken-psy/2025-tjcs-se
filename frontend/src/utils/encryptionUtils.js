/**
 * 密码加密工具
 * 使用SHA-256算法对密码进行加密
 */

/**
 * 密码加密函数
 * @param {string} password - 原始密码
 * @returns {Promise<string>} 加密后的密码（十六进制字符串）
 */
export const encryptPassword = async (password) => {
  try {
    // 将字符串转换为Uint8Array
    const encoder = new TextEncoder()
    const data = encoder.encode(password)
    
    // 使用SHA-256算法进行哈希
    const hashBuffer = await crypto.subtle.digest('SHA-256', data)
    
    // 将ArrayBuffer转换为十六进制字符串
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
    
    return hashHex
  } catch (error) {
    console.error('密码加密失败:', error)
    throw new Error('密码加密失败，请重试')
  }
}

/**
 * 同步版本的密码加密（用于不支持Promise的环境）
 * @param {string} password - 原始密码
 * @returns {string} 加密后的密码（十六进制字符串）
 */
export const encryptPasswordSync = (password) => {
  // 简单的同步哈希实现（生产环境建议使用更安全的库）
  let hash = 0
  for (let i = 0; i < password.length; i++) {
    const char = password.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32bit integer
  }
  return Math.abs(hash).toString(16)
}

/**
 * 验证密码（比较加密后的密码）
 * @param {string} inputPassword - 用户输入的密码
 * @param {string} storedHash - 存储的加密密码
 * @returns {Promise<boolean>} 是否匹配
 */
export const verifyPassword = async (inputPassword, storedHash) => {
  const inputHash = await encryptPassword(inputPassword)
  return inputHash === storedHash
}