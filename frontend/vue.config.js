const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,

  // ESLint 配置：开发时启用，生产时禁用以加快构建
  lintOnSave: process.env.NODE_ENV === 'development',

  // 保留你原有的开发服务器配置
  devServer: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        pathRewrite: { '^/api': '/api' },
        proxyTimeout: 20000,
        timeout: 20000,
      },
      // 2. 新增的静态文件转发规则
      '/uploads': {
        target: 'http://127.0.0.1:8000', // 转发到后端 Docker 端口
        changeOrigin: true,
        // 注意：/uploads 不像 /api 需要特别长的超时，但设置长一些也无妨
      },
    },
    // 添加客户端错误显示配置
    client: {
      overlay: {
        errors: true,
        warnings: false,
      },
    },
  },

  // 添加生产构建优化
  configureWebpack: {
    performance: {
      hints: process.env.NODE_ENV === 'production' ? 'warning' : false,
    },
  },

  // 生产构建优化
  productionSourceMap: false,
})