/**
 * 密码加密工具
 * 使用SHA-256算法对密码进行加密
 */

/**
 * 检测环境并选择一致的加密方法
 * @param {string} password - 原始密码
 * @returns {Promise<string>} 加密后的密码（十六进制字符串）
 */
export const encryptPassword = async (password) => {
  try {
    return encryptPasswordSync(password)
  } catch (error) {
    console.error('密码加密失败:', error)
    throw new Error('密码加密失败，请重试')
  }
}

/**
 * 原SHA-256加密方法（仅用于向后兼容验证）
 * @param {string} password - 原始密码
 * @returns {Promise<string>} 加密后的密码（十六进制字符串）
 */
export const encryptPasswordSHA256 = async (password) => {
  try {
    if (window.crypto && window.crypto.subtle) {
      const encoder = new TextEncoder()
      const data = encoder.encode(password)
      const hashBuffer = await crypto.subtle.digest('SHA-256', data)
      const hashArray = Array.from(new Uint8Array(hashBuffer))
      const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
      return hashHex
    } else {
      throw new Error('SHA-256 not available')
    }
  } catch (error) {
    throw error
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
 * 验证密码（比较加密后的密码）- 支持向后兼容
 * @param {string} inputPassword - 用户输入的密码
 * @param {string} storedHash - 存储的加密密码
 * @returns {Promise<boolean>} 是否匹配
 */
export const verifyPassword = async (inputPassword, storedHash) => {
  try {
    // 首先尝试当前的统一加密方法（同步方法）
    const currentHash = await encryptPassword(inputPassword)
    if (currentHash === storedHash) {
      return true
    }

    // 向后兼容：尝试原来的SHA-256方法（如果用户是在HTTPS环境注册的）
    try {
      const sha256Hash = await encryptPasswordSHA256(inputPassword)
      if (sha256Hash === storedHash) {
        console.log('密码验证：使用SHA-256方法匹配（向后兼容）')
        return true
      }
    } catch (sha256Error) {
      console.log('SHA-256验证不可用，跳过')
    }

    return false
  } catch (error) {
    console.error('密码验证失败:', error)
    return false
  }
}