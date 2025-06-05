import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axiosInstance from './plugins/axios'

import App from './App.vue'
import router from './router'

import './assets/style.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Делаем axios доступным глобально
app.config.globalProperties.$axios = axiosInstance

app.mount('#app')
