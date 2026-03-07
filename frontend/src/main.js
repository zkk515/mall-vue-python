import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
// Element Plus 和 Icons 使用 vite 插件自动按需导入，无需手动 import

const app = createApp(App)
app.use(router)
app.mount('#app')
