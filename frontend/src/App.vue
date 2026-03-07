<template>
  <div class="app-container">
    <!-- 顶部导航 -->
    <div class="top-bar">
      <div class="top-bar-content">
        <div class="location">📍 上海</div>
        <div class="top-links">
          <a href="#" @click.prevent="handleClick">你好 {{ username || '请登录' }}</a>
          <a href="#" @click.prevent="logout" v-if="isLoggedIn">退出登录</a>
          <a href="#" @click="$router.push('/register')" v-else>免费注册</a>
          <span class="divider">|</span>
          <a href="#" @click="$router.push('/orders')">我的订单</a>
          <span class="divider">|</span>
          <a href="#" @click="$router.push('/profile')">个人中心</a>
          <span class="divider">|</span>
          <a href="#" @click="$router.push('/cart')">购物车</a>
        </div>
      </div>
    </div>
    
    <!-- 搜索头部 -->
    <div class="search-header">
      <div class="search-content">
        <div class="logo" @click="$router.push('/products')">🛒</div>
        <div class="search-box">
          <input type="text" v-model="keyword" placeholder="搜索商品" @keyup.enter="doSearch" />
          <button @click="doSearch">搜索</button>
        </div>
      </div>
    </div>
    
    <!-- 分类导航 -->
    <div class="category-bar">
      <div class="category-content">
        <span class="category-title">全部商品分类</span>
        <a href="#" @click.prevent="$router.push('/products')">首页</a>
        <a href="#">京东超市</a>
        <a href="#">京东生鲜</a>
        <a href="#">京东金融</a>
      </div>
    </div>
    
    <!-- 主内容 -->
    <el-main class="main-content">
      <router-view />
    </el-main>
    
    <!-- 底部 -->
    <footer class="footer">
      <div class="footer-content">
        <p>© 2026 极简商城 - 让购物更简单</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref(localStorage.getItem('username') || '')
const keyword = ref('')
const isLoggedIn = computed(() => !!localStorage.getItem('token'))

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  username.value = ''
  router.push('/login')
}

const doSearch = () => {
  router.push({ path: '/products', query: { keyword: keyword.value } })
}

const handleClick = () => {
  if (!isLoggedIn.value) {
    router.push('/login')
  } else {
    router.push('/profile')
  }
}
</script>

<style>
/* ========== UI设计规范 ========== 
 * 主色: #E4393C (京东红)
 * 背景: #F5F5F5
 * 间距: 4/8/16/24/32px
 * 圆角: 8px
 * 阴影: 0 2px 8px rgba(0,0,0,0.08)
 */

* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
  --primary: #E4393C;
  --primary-hover: #C93538;
  --orange: #FF6B00;
  --blue: #0066FF;
  --success: #52C41A;
  --warning: #FAAD14;
  --error: #F5222D;
  --info: #1890FF;
  --bg: #F5F5F5;
  --card-bg: #FFFFFF;
  --border: #E0E0E0;
  --text-secondary: #999999;
  --text-primary: #333333;
  --radius: 8px;
  --shadow: 0 2px 8px rgba(0,0,0,0.08);
  --shadow-hover: 0 4px 12px rgba(0,0,0,0.12);
}

body { 
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif; 
  background: var(--bg);
  color: var(--text-primary);
  min-width: 1000px;
  line-height: 1.5;
  transition: all 0.3s ease;
}
a { text-decoration: none; color: var(--text-secondary); transition: color 0.3s; }
a:hover { color: var(--primary); }

.app-container { min-height: 100vh; display: flex; flex-direction: column; }

/* 顶部导航 */
.top-bar { background: var(--bg); height: 30px; line-height: 30px; font-size: 12px; }
.top-bar-content { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; }
.location { color: var(--text-secondary); }
.top-links a { margin: 0 8px; color: var(--text-secondary); }
.top-links a:hover { color: var(--primary); }
.top-links .divider { color: var(--border); }

/* 搜索头部 */
.search-header { background: #fff; padding: 16px 0; box-shadow: var(--shadow); }
.search-content { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; align-items: center; gap: 32px; }
.logo { 
  cursor: pointer; 
  background: var(--primary); 
  width: 170px; height: 60px; 
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--radius);
  font-size: 24px; font-weight: bold; color: #fff;
  transition: all 0.3s ease;
}
.logo:hover { background: var(--primary-hover); transform: scale(1.02); }
.search-box { display: flex; flex: 1; max-width: 600px; }
.search-box input { 
  flex: 1; height: 40px; 
  border: 2px solid var(--primary); 
  border-right: none; 
  border-radius: 20px 0 0 20px;
  padding: 0 16px; 
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
}
.search-box input:focus { border-color: var(--primary-hover); }
.search-box button { 
  width: 100px; height: 40px; 
  background: var(--primary); 
  color: #fff; 
  border: none; 
  border-radius: 0 20px 20px 0;
  font-size: 16px; 
  cursor: pointer;
  transition: background 0.3s;
}
.search-box button:hover { background: var(--primary-hover); }

/* 分类导航 */
.category-bar { background: #fff; border-bottom: 2px solid var(--primary); }
.category-content { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; align-items: center; height: 40px; }
.category-title { 
  background: var(--primary); 
  color: #fff; 
  padding: 0 16px; 
  height: 40px; 
  line-height: 40px; 
  margin-right: 32px;
  border-radius: 0 var(--radius) var(--radius) 0;
}
.category-content a { 
  padding: 0 24px; 
  font-size: 14px; 
  color: var(--text-primary);
  transition: color 0.3s;
}
.category-content a:hover { color: var(--primary); }

/* 主内容 */
.main-content { 
  flex: 1; 
  max-width: 1200px; 
  margin: 0 auto; 
  width: 100%; 
  background: var(--card-bg); 
  padding: 16px;
  margin-top: 8px;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

/* 底部 */
.footer { background: var(--card-bg); padding: 24px 0; border-top: 1px solid var(--border); margin-top: 24px; }
.footer-content { text-align: center; color: var(--text-secondary); font-size: 12px; }

/* 通用按钮 */
.btn-primary {
  background: var(--primary);
  color: #fff;
  border: none;
  height: 36px;
  padding: 0 24px;
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.3s ease;
}
.btn-primary:hover { background: var(--primary-hover); }
.btn-primary:active { transform: scale(0.98); }

/* 通用卡片 */
.card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  transition: all 0.3s ease;
}
.card:hover { box-shadow: var(--shadow-hover); transform: translateY(-2px); }
</style>
