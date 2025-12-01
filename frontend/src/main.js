import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import './registerServiceWorker'
import '@fortawesome/fontawesome-free/css/all.css'

// 高德地图插件
import VueAMap, { initAMapApiLoader } from '@vuemap/vue-amap'
import '@vuemap/vue-amap/dist/style.css'

// 初始化 AMap JS API（使用提供的 key）
initAMapApiLoader({
  key: 'aa77c73bcbb93f304fd19800d73480f9',
  securityJsCode: '089b94688ce3d90e53d1f90e2480c1c9',
  plugin: [
    'AMap.Autocomplete',
    'AMap.PlaceSearch',
    'AMap.Scale',
    'AMap.OverView',
    'AMap.ToolBar',
    'AMap.MapType',
    'AMap.Geolocation'
  ]
})

const app = createApp(App)
app.use(createPinia()) // 注册 pinia
app.use(router)
app.use(VueAMap)
app.mount('#app')