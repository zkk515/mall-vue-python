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
* { margin: 0; padding: 0; box-sizing: border-box; }
body { 
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif; 
  background: #f5f5f5;
  min-width: 1000px;
}
a { text-decoration: none; color: #666; }
a:hover { color: #e4393c; }

.app-container { min-height: 100vh; display: flex; flex-direction: column; }

/* 顶部导航 */
.top-bar { background: #f5f5f5; height: 30px; line-height: 30px; font-size: 12px; }
.top-bar-content { max-width: 1200px; margin: 0 auto; padding: 0 10px; display: flex; justify-content: space-between; }
.location { color: #999; }
.top-links a { margin: 0 8px; color: #999; }
.top-links .divider { color: #ddd; }

/* 搜索头部 */
.search-header { background: #fff; padding: 20px 0; }
.search-content { max-width: 1200px; margin: 0 auto; padding: 0 10px; display: flex; align-items: center; gap: 50px; }
.logo { 
  font-size: 40px; cursor: pointer; 
  background: #e4393c; 
  width: 150px; height: 60px; 
  display: flex; align-items: center; justify-content: center;
  border-radius: 4px;
}
.search-box { display: flex; flex: 1; max-width: 600px; }
.search-box input { 
  flex: 1; height: 40px; 
  border: 2px solid #e4393c; 
  border-right: none; 
  padding: 0 15px; 
  font-size: 14px;
  outline: none;
}
.search-box button { 
  width: 100px; height: 40px; 
  background: #e4393c; 
  color: #fff; 
  border: none; 
  font-size: 16px; 
  cursor: pointer;
}

/* 分类导航 */
.category-bar { background: #fff; border-bottom: 2px solid #e4393c; }
.category-content { max-width: 1200px; margin: 0 auto; padding: 0 10px; display: flex; align-items: center; height: 40px; }
.category-title { 
  background: #e4393c; 
  color: #fff; 
  padding: 0 15px; 
  height: 40px; 
  line-height: 40px; 
  margin-right: 30px;
}
.category-content a { 
  padding: 0 20px; 
  font-size: 14px; 
  color: #333;
}

/* 主内容 */
.main-content { 
  flex: 1; 
  max-width: 1200px; 
  margin: 0 auto; 
  width: 100%; 
  background: #fff; 
  padding: 20px;
  margin-top: 10px;
}

/* 底部 */
.footer { background: #fff; padding: 20px 0; border-top: 1px solid #e4e7ed; margin-top: 20px; }
.footer-content { text-align: center; color: #999; font-size: 12px; }
</style>
