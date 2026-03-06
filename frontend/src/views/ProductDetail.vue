<template>
  <div class="product-detail">
    <!-- 面包屑 -->
    <div class="breadcrumb">
      <a href="#" @click.prevent="$router.push('/products')">首页</a>
      <span class="divider">></span>
      <span>商品详情</span>
    </div>
    
    <!-- 商品主图和基本信息 -->
    <div class="product-main" v-if="product">
      <div class="product-imgs">
        <div class="main-img">
          <img :src="product.image_url" :alt="product.name" />
        </div>
      </div>
      
      <div class="product-info">
        <h1 class="product-title">{{ product.name }}</h1>
        <p class="product-desc">{{ product.description }}</p>
        
        <div class="price-box">
          <div class="price-label">价&nbsp;&nbsp;格</div>
          <div class="price-content">
            <span class="price-symbol">¥</span>
            <span class="price-value">{{ product.price }}</span>
          </div>
        </div>
        
        <div class="stock-box">
          <span class="stock-label">库&nbsp;&nbsp;存</span>
          <span class="stock-value">{{ product.stock }} 件</span>
        </div>
        
        <div class="quantity-box">
          <span class="quantity-label">数&nbsp;&nbsp;量</span>
          <div class="quantity-input">
            <button @click="quantity > 1 && quantity--">-</button>
            <input type="text" v-model="quantity" />
            <button @click="quantity++">+</button>
          </div>
        </div>
        
        <div class="action-buttons">
          <button class="btn-buy" @click="buyNow">立即购买</button>
          <button class="btn-cart" @click="addToCart">加入购物车</button>
        </div>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div class="loading" v-if="loading">
      <img src="https://img12.360buyimg.com/vclist/jfs/t1/120989/20/14942/158/5e7a8f2aEbf730d76/91c2e937d2b24e31.png" />
      <p>加载中...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productAPI, cartAPI } from '../api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const product = ref(null)
const quantity = ref(1)

onMounted(async () => {
  loading.value = true
  try {
    product.value = await productAPI.detail(route.params.id)
  } finally {
    loading.value = false
  }
})

const addToCart = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  try {
    await cartAPI.add({ product_id: product.value.id, quantity: quantity.value })
    ElMessage.success('已加入购物车')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '添加失败')
  }
}

const buyNow = () => {
  addToCart().then(() => {
    router.push('/cart')
  })
}
</script>

<style scoped>
.product-detail { padding: 10px; }
.breadcrumb { margin-bottom: 15px; font-size: 12px; color: #999; }
.breadcrumb a { color: #666; }
.breadcrumb .divider { margin: 0 8px; }

.product-main { display: flex; gap: 30px; }

.product-imgs { width: 450px; flex-shrink: 0; }
.main-img { 
  width: 450px; height: 450px; 
  border: 1px solid #e4e7ed;
  display: flex; align-items: center; justify-content: center;
  background: #f5f5f5;
}
.main-img img { max-width: 100%; max-height: 100%; object-fit: contain; }

.product-info { flex: 1; }
.product-title { font-size: 20px; font-weight: 400; line-height: 1.5; margin-bottom: 10px; color: #333; }
.product-desc { font-size: 14px; color: #999; margin-bottom: 20px; }

.price-box { 
  background: #f5f5f5; 
  padding: 15px; 
  margin-bottom: 15px;
  display: flex; align-items: center;
}
.price-label { color: #999; font-size: 14px; width: 70px; }
.price-content { display: flex; align-items: baseline; }
.price-symbol { color: #e4393c; font-size: 20px; }
.price-value { color: #e4393c; font-size: 32px; font-weight: bold; }

.stock-box, .quantity-box { display: flex; align-items: center; margin-bottom: 20px; padding: 10px 0; }
.stock-label, .quantity-label { color: #999; font-size: 14px; width: 70px; }
.stock-value { color: #666; font-size: 14px; }

.quantity-input { display: flex; align-items: center; }
.quantity-input button { 
  width: 30px; height: 30px; 
  border: 1px solid #ccc; 
  background: #f5f5f5;
  cursor: pointer;
  font-size: 16px;
}
.quantity-input input { 
  width: 50px; height: 28px; 
  border: 1px solid #ccc; 
  text-align: center; 
  margin: 0 -1px;
  outline: none;
}

.action-buttons { margin-top: 30px; display: flex; gap: 15px; }
.btn-buy { 
  width: 150px; height: 46px; 
  background: #ffe4d6; 
  color: #e4393c; 
  border: 2px solid #e4393c;
  font-size: 18px; cursor: pointer;
}
.btn-buy:hover { background: #e4393c; color: #fff; }

.btn-cart { 
  width: 150px; height: 46px; 
  background: #e4393c; 
  color: #fff; 
  border: none;
  font-size: 18px; cursor: pointer;
}
.btn-cart:hover { background: #c23531; }

.loading { text-align: center; padding: 100px; }
.loading img { width: 150px; }
.loading p { color: #999; margin-top: 10px; }
</style>
