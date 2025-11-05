const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,

  // ESLint 配置：开发时启用，生产时禁用以加快构建
  lintOnSave: process.env.NODE_ENV === 'development',

  // 保留你原有的开发服务器配置
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        pathRewrite: { '^/api': '/api' }
      }
    },
    // 添加客户端错误显示配置
    client: {
      overlay: {
        errors: true,
        warnings: false
      }
    }
  },

  // 添加生产构建优化
  configureWebpack: {
    performance: {
      hints: process.env.NODE_ENV === 'production' ? 'warning' : false
    }
  },

  // 生产构建优化
  productionSourceMap: false
})