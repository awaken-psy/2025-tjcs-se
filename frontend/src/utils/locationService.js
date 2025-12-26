/**
 * 高德地图定位服务工具函数
 * 强化浏览器高精度定位请求，优化定位精度
 */

// 高德地图安全配置（与全局初始化保持一致）
window._AMapSecurityConfig = {
  securityJsCode: '089b94688ce3d90e53d1f90e2480c1c9'
}

/**
 * 获取高精度当前位置（强化浏览器精准定位请求）
 * @returns {Promise<Object>} 返回定位结果
 */
export const getCurrentLocation = () => {
  return new Promise((resolve) => {
    console.log('🚀 开始高精度定位流程（浏览器原生+高德增强）...')

    // 优先尝试浏览器原生高精度定位
    if (navigator.geolocation) {
      console.log('📍 尝试浏览器原生高精度定位...')
      const nativeOptions = {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 0
      }
      navigator.geolocation.getCurrentPosition(
        (nativeResult) => {
          const acc = nativeResult.coords.accuracy
          // 检查坐标是否有效（排除明显异常值）
          const isValidCoord = nativeResult.coords.latitude && nativeResult.coords.longitude &&
            nativeResult.coords.latitude >= -90 && nativeResult.coords.latitude <= 90 &&
            nativeResult.coords.longitude >= -180 && nativeResult.coords.longitude <= 180

          if (isValidCoord && typeof acc === 'number' && acc < 1000 && acc > 0) {
            console.log('✅ 浏览器原生定位成功，精度:', acc, '米', nativeResult.coords)
            resolve({
              success: true,
              longitude: nativeResult.coords.longitude,
              latitude: nativeResult.coords.latitude,
              accuracy: acc,
              altitude: nativeResult.coords.altitude,
              heading: nativeResult.coords.heading,
              speed: nativeResult.coords.speed,
              timestamp: nativeResult.timestamp,
              source: 'Browser High Accuracy Geolocation',
              locationType: 'browser_gps',
              note: acc < 30 ? '高精度' : acc < 100 ? '中等精度' : '较低精度',
              warning: acc > 100 ? '当前定位精度较低，建议在空旷环境下重试' : undefined
            })
          } else {
            console.warn('⚠️ 浏览器原生定位精度不足（', acc, '米）或坐标无效，fallback 到高德定位')
            tryAMapGeolocation(resolve)
          }
        },
        (nativeError) => {
          console.warn('⚠️ 浏览器原生定位失败， fallback 到高德定位:', nativeError)
          tryAMapGeolocation(resolve, nativeError)
        },
        nativeOptions
      )
    } else {
      tryAMapGeolocation(resolve)
    }
  })
}

// 封装高德定位，自动判断精度
function tryAMapGeolocation(resolve, nativeError) {
  if (typeof AMap !== 'undefined') {
    AMap.plugin('AMap.Geolocation', () => {
      // 第一次尝试：高精度GPS定位
      const geolocation = new AMap.Geolocation({
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
        convert: true,
        noIpLocate: 1,
        noGeoLocation: 0,
        GeoLocationFirst: true,
        useNative: true,
        showButton: false,
        showMarker: false,
        showCircle: false,
        panToLocation: false,
        zoomToAccuracy: false,
        needAddress: true,
        extensions: 'all'
      })
      geolocation.getCurrentPosition((status, result) => {
        if (status === 'complete' && result.position) {
          const acc = result.accuracy
          const locType = result.location_type || ''

          // 更宽松的精度判断 - 只要精度<200米就接受
          if (typeof acc === 'number' && acc < 200 && acc > 0) {
            resolve({
              success: true,
              longitude: result.position.lng,
              latitude: result.position.lat,
              accuracy: acc,
              address: result.formattedAddress,
              locationType: locType,
              source: 'AMAP Enhanced Geolocation',
              note: acc < 30 ? '高精度' : acc < 100 ? '中等精度' : '较低精度',
              warning: acc > 100 ? '当前定位精度较低，建议在空旷环境下重试' : undefined,
              rawData: result
            })
          } else {
            resolve({
              success: false,
              error: `高德定位精度不足（${acc}米，类型:${locType}），请在空旷环境下重试`,
              code: 'AMAP_LOW_ACCURACY',
              details: result,
              nativeError
            })
          }
        } else {
          resolve({
            success: false,
            error: `高德定位失败: ${result.message || '未知错误'}`,
            code: result.code || 'AMAP_FAILED',
            details: result,
            nativeError
          })
        }
      })
    })
  } else {
    resolve({
      success: false,
      error: '浏览器和高德地图API均无法定位',
      code: 'NO_LOCATION_SUPPORT',
      nativeError
    })
  }
}

/**
 * 执行增强版高德定位（强化高精度参数）
 */
const executeEnhancedAMapGeolocation = (resolve) => {
  try {
    console.log('� 启动增强版高德定位（高精度模式）...')
    
    const geolocation = new AMap.Geolocation({
      // 核心高精度配置
      enableHighAccuracy: true,           // 强制高精度
      timeout: 15000,                     // 延长超时时间（高精度需要更多时间）
      maximumAge: 0,                      // 禁用缓存
      convert: true,                      // 自动转换坐标系
      
      // 定位源优化
      noIpLocate: 0,                      // 禁用低精度IP定位
      noGeoLocation: 0,
      GeoLocationFirst: true,             // 优先使用浏览器原生定位结果
      useNative: true,                    // 启用设备原生定位模块
      
      // 界面与交互配置
      showButton: false,
      showMarker: false,
      showCircle: false,
      panToLocation: false,
      zoomToAccuracy: false,
      
      // 扩展信息
      needAddress: true,
      extensions: 'all'
    })

    let locationAttempts = 0
    const maxAttempts = 2  // 高精度定位重试2次
    
    const attemptLocation = () => {
      locationAttempts++
      console.log(`📍 高德定位尝试 ${locationAttempts}/${maxAttempts}`)
      
      geolocation.getCurrentPosition(
        (status, result) => {
          if (status === 'complete') {
            console.log('✅ 高德定位成功，精度:', result.accuracy, '米')
            const amapLocation = processAMapLocation(result)
            resolve(amapLocation)
          } else {
            if (locationAttempts < maxAttempts) {
              console.log('📍 高德定位重试...')
              setTimeout(attemptLocation, 1500)  // 稍长间隔重试，给定位模块准备时间
            } else {
              resolve({
                success: false,
                error: `高德定位失败: ${result.message || '未知错误'}`,
                code: result.code || 'AMAP_FAILED',
                details: result
              })
            }
          }
        }
      )
    }
    
    attemptLocation()
    
  } catch (error) {
    console.error('📍 定位服务异常:', error)
    resolve({
      success: false,
      error: `定位服务异常: ${error.message}`,
      code: 'LOCATION_SERVICE_ERROR'
    })
  }
}

/**
 * 处理高德定位结果
 */
const processAMapLocation = (result) => {
  const position = result.position
  return {
    success: true,
    longitude: position.lng,  // 保留原始精度（高德返回通常为6位小数以上）
    latitude: position.lat,
    accuracy: result.accuracy || 5,  // 高德定位精度
    address: result.formattedAddress,
    province: result.addressComponent?.province,
    city: result.addressComponent?.city,
    district: result.addressComponent?.district,
    street: result.addressComponent?.street,
    streetNumber: result.addressComponent?.streetNumber,
    locationType: result.location_type || 'amap_high_accuracy',
    timestamp: Date.now(),
    source: 'AMAP Enhanced Geolocation',
    rawData: result  // 保留原始数据用于调试
  }
}

/**
 * 解析浏览器定位错误代码为可读文本
 */
const getGeolocationErrorText = (errorCode) => {
  const errors = {
    1: '用户拒绝了定位权限请求',
    2: '无法获取定位信息（设备可能未开启定位功能）',
    3: '定位请求超时（高精度定位可能需要更长时间）',
    4: '未知错误'
  }
  return errors[errorCode] || errors[4]
}

/**
 * 获取位置权限状态（含引导文案）
 */
export const getLocationPermissionStatus = () => {
  return new Promise((resolve) => {
    if (!navigator.permissions) {
      resolve({
        state: 'prompt',
        message: '浏览器不支持权限查询，请直接尝试定位'
      })
      return
    }

    navigator.permissions.query({ name: 'geolocation' })
      .then((result) => {
        const messages = {
          granted: '已获取定位权限，可进行高精度定位',
          denied: '定位权限已被拒绝，请在浏览器设置中启用（设置路径：浏览器设置 > 隐私与安全 > 位置信息 > 允许当前网站）',
          prompt: '尚未获取定位权限，请允许定位请求以获得高精度位置'
        }
        resolve({
          state: result.state,
          message: messages[result.state]
        })
      })
      .catch((error) => {
        resolve({
          state: 'unknown',
          message: `权限查询失败: ${error.message}`
        })
      })
  })
}

/**
 * 检查定位服务可用性（含高精度支持检测）
 */
export const isLocationServiceAvailable = () => {
  const hasBrowserSupport = !!navigator.geolocation
  const hasAMapSupport = typeof AMap !== 'undefined' && !!AMap.Geolocation
  const isHTTPS = window.location.protocol === 'https:'  // HTTPS环境下高精度定位更可靠
  
  return {
    available: hasBrowserSupport || hasAMapSupport,
    hasHighAccuracySupport: hasBrowserSupport,  // 浏览器原生定位是高精度核心
    isHTTPS: isHTTPS,
    recommendation: isHTTPS ? '当前环境支持高精度定位' : '建议使用HTTPS协议以获得更稳定的高精度定位'
  }
}

/**
 * 获取详细定位能力报告
 */
export const getLocationCapabilityReport = async() => {
  const permission = await getLocationPermissionStatus()
  const service = isLocationServiceAvailable()
  const deviceInfo = {
    platform: navigator.platform,
    userAgent: navigator.userAgent,
    isMobile: /Mobile|Android|iOS/.test(navigator.userAgent)
  }
  
  // 高精度定位建议
  const suggestions = []
  if (!service.isHTTPS) suggestions.push('切换到HTTPS协议以提升定位精度')
  if (permission.state === 'denied') suggestions.push('在浏览器设置中重新启用定位权限')
  if (deviceInfo.isMobile) suggestions.push('确保设备GPS已开启（设置 > 位置信息 > 高精度模式）')
  
  return {
    ...permission,
    ...service,
    deviceInfo,
    suggestions: suggestions.length ? suggestions : ['当前环境适合高精度定位']
  }
}

/**
 * 计算两点间距离（米）
 */
export const calculateDistance = (lat1, lng1, lat2, lng2) => {
  const R = 6371000
  const toRad = deg => deg * Math.PI / 180
  const dLat = toRad(lat2 - lat1)
  const dLng = toRad(lng2 - lng1)
  const a = Math.sin(dLat/2) **2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng/2)** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

/**
 * 格式化距离显示
 */
export const formatDistance = (distance) => {
  if (distance < 1000) return `${Math.round(distance)}米`
  return `${(distance / 1000).toFixed(1)}公里`
}

/**
 * 带重试的高精度定位（最多3次，间隔递增）
 */
export const getLocationWithRetry = async(maxRetries = 3) => {
  // 先检查定位能力，提前发现问题
  const report = await getLocationCapabilityReport()
  if (!report.available) {
    return {
      success: false,
      error: '设备不支持定位服务',
      code: 'NO_LOCATION_CAPABILITY',
      report
    }
  }
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    console.log(`🔄 高精度定位重试 ${attempt}/${maxRetries}`)
    
    try {
      const result = await getCurrentLocation()
      if (result.success) {
        // 定位成功时附加能力报告
        return { ...result, report }
      }
      
      if (attempt === maxRetries) {
        return { ...result, report }
      }
      
      // 重试间隔随次数增加（给定位模块更多准备时间）
      const delay = 1000 * attempt
      console.log(`⏳ 等待${delay}ms后重试...`)
      await new Promise(resolve => setTimeout(resolve, delay))
    } catch (error) {
      console.error(`❌ 第${attempt}次定位异常:`, error)
      
      if (attempt === maxRetries) {
        return {
          success: false,
          error: `所有定位尝试失败: ${error.message}`,
          code: 'ALL_ATTEMPTS_FAILED',
          report
        }
      }
    }
  }
}

export default {
  getCurrentLocation,
  getLocationWithRetry,
  isLocationServiceAvailable,
  getLocationPermissionStatus,
  getLocationCapabilityReport,
  calculateDistance,
  formatDistance
}