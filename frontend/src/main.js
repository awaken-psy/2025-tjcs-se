import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import './registerServiceWorker'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

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
    'AMap.Geocoder',      // 用于逆地理编码
    'AMap.Geolocation',
  ],
})

const app = createApp(App)

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia) // 注册 pinia
app.use(router)
app.use(VueAMap)
app.mount('#app')