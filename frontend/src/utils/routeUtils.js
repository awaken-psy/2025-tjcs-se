
/**
 * 路由工具类：封装Vue Router核心操作，统一路由逻辑，减少页面重复代码
 * 依赖：项目需提前创建Vue Router实例（src/router/index.js）
 * 使用场景：页面跳转、参数解析、路由守卫辅助、权限判断
 */
import router from '@/router/index.js' // 引入项目已配置的Router实例
import { useUserStore } from '@/store/user' // 引入用户状态（可选，用于权限判断）

/**
 * 1. 路由跳转：支持路径跳转/命名路由，自动处理参数，避免重复写router.push
 * @param {String|Object} target - 目标路由（路径字符串/命名路由对象）
 * @param {Object} [options={}] - 额外配置
 * @param {Object} [options.params] - 路由params参数（命名路由时生效）
 * @param {Object} [options.query] - 路由query参数
 * @param {Boolean} [options.replace=false] - 是否用replace模式（不增加历史记录）
 * @param {Boolean} [options.needLogin=false] - 是否需要登录权限
 * @example
 * // 路径跳转
 * routeJump('/my-capsule', { query: { page: 1 } });
 * // 命名路由跳转
 * routeJump({ name: 'UserHome' }, { params: { userId: '123' }, replace: true });
 */
export const routeJump = (target, options = {}) => {
  const { params, query, replace = false, needLogin = false } = options
  const userStore = useUserStore()

  // 1. 权限判断：需要登录但未登录时，跳转登录页
  if (needLogin && !userStore.token) {
    router.push({
      path: '/login',
      query: { redirect: router.currentRoute.value.fullPath }
    })
    return
  }

  // 2. 处理目标路由格式
  let routeConfig = {}
  if (typeof target === 'string') {
    // 路径跳转
    routeConfig = { path: target, query }
  } else if (typeof target === 'object' && target.name) {
    // 命名路由跳转
    routeConfig = { name: target.name, params, query }
  } else {
    console.error('routeJump：目标路由格式错误，需为路径字符串或含name的对象')
    return
  }

  // 3. 执行跳转（replace模式/普通模式）
  if (replace) {
    router.replace(routeConfig).catch(err => handleRouteError(err))
  } else {
    router.push(routeConfig).catch(err => handleRouteError(err))
  }
}

/**
 * 2. 解析路由参数：自动转换query/params参数类型（URL参数默认是字符串，需转数字/布尔）
 * @param {String} type - 参数类型（'query'/'params'）
 * @param {String} key - 参数键名
 * @param {String} [format='string'] - 参数格式（string/number/boolean）
 * @param {any} [defaultVal=''] - 默认值（参数不存在时返回）
 * @returns {any} 解析后的参数值
 * @example
 * // 解析query中的page参数（转数字，默认1）
 * const page = parseRouteParam('query', 'page', 'number', 1);
 * // 解析params中的userId参数（默认空字符串）
 * const userId = parseRouteParam('params', 'userId', 'string', '');
 */
export const parseRouteParam = (type, key, format = 'string', defaultVal = '') => {
  const currentRoute = router.currentRoute.value
  // 1. 获取原始参数
  const rawValue = type === 'query' 
    ? currentRoute.query[key] 
    : currentRoute.params[key]

  // 2. 参数不存在时返回默认值
  if (rawValue === undefined || rawValue === null || rawValue === '') {
    return defaultVal
  }

  // 3. 转换参数格式
  switch (format) {
  case 'number': {
    const numVal = Number(rawValue)
    return isNaN(numVal) ? defaultVal : numVal
  }
  case 'boolean': {
    return rawValue === 'true' || rawValue === '1' ? true : false
  }
  case 'array': {
    return Array.isArray(rawValue) ? rawValue : [rawValue]
  }
  case 'string':
  default: {
    return String(rawValue)
  }
  }
}

/**
 * 3. 路由错误处理：统一捕获路由跳转错误（如重复跳转同一路径）
 * @param {Error} err - 路由错误对象
 */
export const handleRouteError = (err) => {
  if (err && err.message && err.message.includes('Avoided redundant navigation to current location')) {
    return
  }
  console.error('路由跳转错误：', err)
}

/**
 * 4. 获取当前路由名称：简化获取当前路由name的写法
 * @returns {String} 当前路由name（无name时返回path）
 */
export const getCurrentRouteName = () => {
  const currentRoute = router.currentRoute.value
  return currentRoute.name || currentRoute.path
}

/**
 * 5. 回到上一页：封装router.go(-1)，支持 fallback（无历史记录时跳转默认页）
 * @param {String} [fallbackPath='/'] - 无历史记录时的默认跳转路径
 */
export const goBack = (fallbackPath = '/') => {
  if (window.history.length <= 1) {
    router.push(fallbackPath).catch(err => handleRouteError(err))
  } else {
    router.go(-1)
  }
}

/**
 * 6. 拼接完整URL：用于分享、跳转外部链接时，拼接路由完整路径
 * @param {String|Object} route - 目标路由（路径字符串/命名路由对象）
 * @param {Object} [options={ params, query }] - 路由参数
 * @returns {String} 完整URL（含域名）
 */
export const getFullRouteUrl = (route, options = {}) => {
  const { params, query } = options
  const routeLocation = router.resolve(route, params, query)
  const origin = import.meta.env && import.meta.env.MODE === 'development' 
    ? 'http://localhost:5173' 
    : window.location.origin
  return `${origin}${routeLocation.href}`
}
