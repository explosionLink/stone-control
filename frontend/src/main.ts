import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// Inizializza lo store auth (carica token dagli header axios)
const auth = useAuthStore()
auth.init()

app.mount('#app')
