import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import './registerServiceWorker'

const app = createApp(App)
app.use(createPinia()) // 注册 pinia
app.use(router)
app.mount('#app')