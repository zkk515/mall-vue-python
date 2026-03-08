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
          <button class="btn-favorite" :class="{ active: isFavorited }" @click="toggleFavorite">
            {{ isFavorited ? '❤️ 已收藏' : '🤍 收藏' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 评论区域 -->
    <div class="review-section" v-if="product">
      <div class="review-header">
        <h3>商品评价</h3>
        <div class="review-stats">
          <span class="avg-rating" v-if="reviewCount.avg_rating > 0">评分: {{ reviewCount.avg_rating }} ⭐</span>
          <span class="total-count">{{ reviewCount.total }} 条评价</span>
        </div>
      </div>
      
      <!-- 添加评论 -->
      <div class="add-review" v-if="isLoggedIn">
        <div class="review-form">
          <div class="rating-select">
            <span>评分:</span>
            <el-rate v-model="newReview.rating" :colors="['#99a9bf', '#e4393c', '#e4393c']" />
          </div>
          <textarea v-model="newReview.comment" placeholder="分享你的使用体验..." rows="3"></textarea>
          <button class="btn-submit" @click="submitReview">提交评论</button>
        </div>
      </div>
      <div class="login-tip" v-else>
        <a @click="$router.push('/login')">登录</a>后可以发表评论
      </div>
      
      <!-- 评论列表 -->
      <div class="review-list">
        <div class="review-item" v-for="review in reviews" :key="review.id">
          <div class="review-user">{{ review.username }}</div>
          <div class="review-rating">
            <span v-for="n in 5" :key="n" :class="{ filled: n <= review.rating }">★</span>
          </div>
          <div class="review-comment">{{ review.comment || '默认好评' }}</div>
          <div class="review-date">{{ review.created_at }}</div>
        </div>
        <div class="empty-review" v-if="reviews.length === 0">
          暂无评价，快来抢先评价吧！
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
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productAPI, cartAPI, reviewAPI, favoritesAPI } from '../api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const product = ref(null)
const quantity = ref(1)
const reviews = ref([])
const reviewCount = ref({ total: 0, avg_rating: 0 })
const newReview = ref({ rating: 5, comment: '' })
const isLoggedIn = computed(() => !!localStorage.getItem('token'))
const isFavorited = ref(false)

const loadFavorited = async () => {
  try {
    const res = await favoritesAPI.check(route.params.id)
    isFavorited.value = res.favorited || false
  } catch (e) {
    // 未登录时忽略
  }
}

const toggleFavorite = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  try {
    if (isFavorited.value) {
      await favoritesAPI.remove(product.value.id)
      isFavorited.value = false
      ElMessage.success('已取消收藏')
    } else {
      await favoritesAPI.add(product.value.id)
      isFavorited.value = true
      ElMessage.success('收藏成功')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

const loadReviews = async () => {
  try {
    reviews.value = await reviewAPI.list(route.params.id)
    reviewCount.value = await reviewAPI.count(route.params.id)
  } catch (e) {
    console.error('加载评论失败', e)
  }
}

const submitReview = async () => {
  if (newReview.value.rating < 1) {
    ElMessage.warning('请选择评分')
    return
  }
  try {
    await reviewAPI.add({
      product_id: parseInt(route.params.id),
      rating: newReview.value.rating,
      comment: newReview.value.comment
    })
    ElMessage.success('评论成功')
    newReview.value = { rating: 5, comment: '' }
    loadReviews()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '评论失败')
  }
}

onMounted(async () => {
  loading.value = true
  try {
    product.value = await productAPI.detail(route.params.id)
    await loadReviews()
    if (isLoggedIn.value) {
      await loadFavorited()
    }
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
/* ========== UI设计规范 ========== */
.product-detail { padding: var(--spacing-md, 16px); }

.breadcrumb { margin-bottom: var(--spacing-md, 16px); font-size: 12px; color: var(--text-secondary, #999); }
.breadcrumb a { color: var(--text-primary, #333); }
.breadcrumb a:hover { color: var(--primary, #E4393C); }
.breadcrumb .divider { margin: 0 8px; }

.product-main { display: flex; gap: var(--spacing-xl, 32px); }

.product-imgs { width: 450px; flex-shrink: 0; }
.main-img { 
  width: 450px; height: 450px; 
  border: 1px solid var(--border, #E0E0E0);
  display: flex; align-items: center; justify-content: center;
  background: var(--bg, #F5F5F5);
  border-radius: var(--radius, 8px);
  overflow: hidden;
}
.main-img img { max-width: 100%; max-height: 100%; object-fit: contain; transition: transform 0.3s ease; }
.main-img:hover img { transform: scale(1.02); }

.product-info { flex: 1; }
.product-title { font-size: 22px; font-weight: 400; line-height: 1.5; margin-bottom: var(--spacing-sm, 8px); color: var(--text-primary, #333); }
.product-desc { font-size: 14px; color: var(--text-secondary, #999); margin-bottom: var(--spacing-lg, 24px); }

.price-box { 
  background: var(--bg, #F5F5F5); 
  padding: var(--spacing-md, 16px); 
  margin-bottom: var(--spacing-md, 16px);
  display: flex; align-items: center;
  border-radius: var(--radius, 8px);
}
.price-label { color: var(--text-secondary, #999); font-size: 14px; width: 70px; }
.price-content { display: flex; align-items: baseline; }
.price-symbol { color: var(--primary, #E4393C); font-size: 20px; }
.price-value { color: var(--primary, #E4393C); font-size: 32px; font-weight: bold; }

.stock-box, .quantity-box { display: flex; align-items: center; margin-bottom: var(--spacing-lg, 24px); padding: var(--spacing-sm, 8px) 0; }
.stock-label, .quantity-label { color: var(--text-secondary, #999); font-size: 14px; width: 70px; }
.stock-value { color: var(--text-primary, #333); font-size: 14px; }
.stock-value.low-stock { color: var(--warning, #FAAD14); }

.quantity-input { display: flex; align-items: center; }
.quantity-input button { 
  width: 32px; height: 32px; 
  border: 1px solid var(--border, #E0E0E0); 
  background: var(--card-bg, #fff);
  cursor: pointer;
  font-size: 16px;
  border-radius: var(--radius, 8px);
  transition: all 0.3s ease;
}
.quantity-input button:hover { 
  background: var(--primary, #E4393C); 
  color: #fff; 
  border-color: var(--primary, #E4393C);
}
.quantity-input input { 
  width: 50px; height: 30px; 
  border: 1px solid var(--border, #E0E0E0); 
  text-align: center; 
  margin: 0 -1px;
  outline: none;
  border-radius: 0;
}

.action-buttons { margin-top: var(--spacing-xl, 32px); display: flex; gap: var(--spacing-md, 16px); }
.btn-buy { 
  flex: 1; height: 48px; 
  background: #fff; 
  color: var(--primary, #E4393C); 
  border: 2px solid var(--primary, #E4393C);
  font-size: 18px; cursor: pointer;
  border-radius: var(--radius, 8px);
  transition: all 0.3s ease;
}
.btn-buy:hover { 
  background: var(--primary, #E4393C); 
  color: #fff; 
}

.btn-cart { 
  flex: 1; height: 48px; 
  background: var(--primary, #E4393C); 
  color: #fff; 
  border: none;
  font-size: 18px; cursor: pointer;
  border-radius: var(--radius, 8px);
  transition: all 0.3s ease;
}
.btn-cart:hover { 
  background: var(--primary-hover, #C93538); 
}

.btn-favorite {
  width: 120px; height: 48px;
  background: #fff;
  border: 1px solid #e4e7ed;
  font-size: 14px; cursor: pointer;
  border-radius: var(--radius, 8px);
  transition: all 0.3s ease;
}
.btn-favorite:hover { border-color: #e4393c; color: #e4393c; }
.btn-favorite.active { background: #ffe4d6; border-color: #e4393c; color: #e4393c; }

/* 评论区域样式 */
.review-section { 
  margin-top: var(--spacing-xl, 32px); 
  background: var(--card-bg, #fff); 
  padding: var(--spacing-lg, 24px); 
  border-radius: var(--radius, 8px);
  box-shadow: var(--shadow, 0 2px 8px rgba(0,0,0,0.08));
}
.review-header { 
  display: flex; justify-content: space-between; align-items: center; 
  border-bottom: 2px solid var(--primary, #E4393C); 
  padding-bottom: var(--spacing-sm, 8px); 
  margin-bottom: var(--spacing-lg, 24px);
}
.review-header h3 { font-size: 18px; color: var(--text-primary, #333); }
.review-stats { font-size: 14px; }
.avg-rating { color: var(--primary, #E4393C); margin-right: var(--spacing-md, 16px); }
.total-count { color: var(--text-secondary, #999); }

.add-review { margin-bottom: var(--spacing-lg, 24px); padding: var(--spacing-md, 16px); background: var(--bg, #F5F5F5); border-radius: var(--radius, 8px); }
.review-form { display: flex; flex-direction: column; gap: var(--spacing-sm, 8px); }
.rating-select { display: flex; align-items: center; gap: 10px; }
.review-form textarea { 
  padding: var(--spacing-sm, 8px) var(--spacing-md, 16px); 
  border: 1px solid var(--border, #E0E0E0); 
  border-radius: var(--radius, 8px); 
  resize: none;
  font-family: inherit;
  transition: border-color 0.3s;
}
.review-form textarea:focus { border-color: var(--primary, #E4393C); }
.btn-submit { 
  align-self: flex-end; 
  padding: 8px 24px; 
  background: var(--primary, #E4393C); 
  color: #fff; 
  border: none; 
  border-radius: var(--radius, 8px); 
  cursor: pointer;
  transition: all 0.3s ease;
}
.btn-submit:hover { background: var(--primary-hover, #C93538); }

.login-tip { padding: var(--spacing-md, 16px); background: var(--bg, #F5F5F5); text-align: center; color: var(--text-secondary, #999); border-radius: var(--radius, 8px); }
.login-tip a { color: var(--primary, #E4393C); cursor: pointer; }

.review-item { 
  padding: var(--spacing-md, 16px) 0; 
  border-bottom: 1px solid var(--border, #E0E0E0); 
}
.review-item:last-child { border-bottom: none; }
.review-user { font-weight: bold; margin-bottom: var(--spacing-xs, 4px); }
.review-rating { margin-bottom: var(--spacing-xs, 8px); }
.review-rating span { color: #ddd; font-size: 14px; }
.review-rating span.filled { color: var(--primary, #E4393C); }
.review-comment { color: var(--text-primary, #333); font-size: 14px; margin-bottom: var(--spacing-xs, 4px); }
.review-date { color: var(--text-secondary, #999); font-size: 12px; }
.empty-review { padding: var(--spacing-xl, 32px); text-align: center; color: var(--text-secondary, #999); }

.loading { text-align: center; padding: 100px; }
.loading img { width: 150px; }
.loading p { color: var(--text-secondary, #999); margin-top: 10px; }
</style>
