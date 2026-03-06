<template>
  <div class="products-page">
    <!-- 轮播图 -->
    <div class="banner-carousel">
      <div class="carousel-inner" :style="{ transform: `translateX(-${currentSlide * 100}%)` }">
        <div class="carousel-item" v-for="(banner, index) in banners" :key="index">
          <img :src="banner.image" :alt="banner.title" />
          <div class="carousel-caption">
            <h3>{{ banner.title }}</h3>
            <p>{{ banner.subtitle }}</p>
          </div>
        </div>
      </div>
      <div class="carousel-dots">
        <span 
          v-for="(banner, index) in banners" 
          :key="index"
          :class="{ active: currentSlide === index }"
          @click="currentSlide = index"
        ></span>
      </div>
    </div>
    
    <!-- 分类侧边栏 -->
    <div class="category-sidebar">
      <div class="category-title">全部分类</div>
      <div 
        class="category-item" 
        v-for="cat in categories" 
        :key="cat.id"
        :class="{ active: activeCategory === cat.id }"
        @click="selectCategory(cat.id)"
      >
        <span class="cat-icon">📱</span>
        {{ cat.name }}
      </div>
    </div>
    
    <!-- 商品列表 -->
    <div class="products-main">
      <h2 class="page-title">{{ pageTitle }}</h2>
      
      <!-- 搜索结果提示 -->
      <div class="search-tips" v-if="keyword">
        搜索"<span>{{ keyword }}</span>"，找到 {{ list.length }} 件商品
      </div>
      
      <!-- 商品列表 -->
      <div class="product-list">
        <div class="product-item" v-for="item in list" :key="item.id" @click="$router.push(`/product/${item.id}`)">
          <div class="product-img">
            <img :src="item.image_url" :alt="item.name" />
          </div>
          <div class="product-info">
            <div class="product-name">{{ item.name }}</div>
            <div class="product-desc">{{ item.description }}</div>
            <div class="product-price">
              <span class="price-symbol">¥</span>
              <span class="price-value">{{ item.price }}</span>
            </div>
            <div class="product-actions">
              <button class="btn-cart">加入购物车</button>
            </div>
            <div class="product-meta">
              <span>{{ item.stock }}人评价</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div class="empty" v-if="!loading && list.length === 0">
        <img src="https://img12.360buyimg.com/vclist/jfs/t1/120989/20/14942/158/5e7a8f2aEbf730d76/91c2e937d2b24e31.png" />
        <p>暂无商品</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { productAPI, categoryAPI } from '../api'

const route = useRoute()
const loading = ref(false)
const list = ref([])
const categories = ref([])
const keyword = ref('')
const activeCategory = ref(0)
const currentSlide = ref(0)
let carouselTimer = null

const banners = [
  { image: 'https://picsum.photos/800/350?random=101', title: '新品上市', subtitle: 'iPhone 15 Pro Max 限时优惠' },
  { image: 'https://picsum.photos/800/350?random=102', title: '电脑专场', subtitle: 'MacBook Air M3 立省500元' },
  { image: 'https://picsum.photos/800/350?random=103', title: '智能穿戴', subtitle: 'Apple Watch S9 全新上市' },
  { image: 'https://picsum.photos/800/350?random=104', title: '音频狂欢', subtitle: 'AirPods Pro 2 代直降200' },
]

const pageTitle = computed(() => {
  if (keyword.value) return '搜索结果'
  if (activeCategory.value) {
    const cat = categories.value.find(c => c.id === activeCategory.value)
    return cat ? cat.name : '商品列表'
  }
  return '商品列表'
})

const loadCategories = async () => {
  try {
    categories.value = await categoryAPI.list()
  } catch (e) {
    console.error('加载分类失败', e)
  }
}

const loadProducts = async () => {
  loading.value = true
  try {
    if (activeCategory.value) {
      list.value = await categoryAPI.products(activeCategory.value, keyword.value)
    } else {
      list.value = await productAPI.list(keyword.value)
    }
  } finally {
    loading.value = false
  }
}

const selectCategory = (id) => {
  activeCategory.value = activeCategory.value === id ? 0 : id
  keyword.value = ''
  loadProducts()
}

onMounted(() => {
  keyword.value = route.query.keyword || ''
  loadCategories()
  loadProducts()
})

watch(() => route.query.keyword, (newKw) => {
  keyword.value = newKw || ''
  activeCategory.value = 0
  loadProducts()
})

// 轮播图自动播放
const startCarousel = () => {
  carouselTimer = setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % banners.length
  }, 3000)
}

onMounted(() => {
  keyword.value = route.query.keyword || ''
  loadCategories()
  loadProducts()
  startCarousel()
})

onUnmounted(() => {
  if (carouselTimer) clearInterval(carouselTimer)
})
</script>

<style scoped>
.products-page { display: flex; flex-direction: column; gap: 15px; min-height: 500px; }

/* 轮播图 */
.banner-carousel {
  position: relative;
  overflow: hidden;
  border-radius: 4px;
}
.carousel-inner {
  display: flex;
  transition: transform 0.5s ease;
}
.carousel-item {
  min-width: 100%;
  position: relative;
}
.carousel-item img {
  width: 100%;
  height: 350px;
  object-fit: cover;
}
.carousel-caption {
  position: absolute;
  bottom: 30px;
  left: 50px;
  color: #fff;
  text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}
.carousel-caption h3 { font-size: 28px; margin-bottom: 5px; }
.carousel-caption p { font-size: 16px; }

.carousel-dots {
  position: absolute;
  bottom: 15px;
  right: 20px;
  display: flex;
  gap: 8px;
}
.carousel-dots span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255,255,255,0.5);
  cursor: pointer;
}
.carousel-dots span.active { background: #fff; }

/* 主内容区 - 包含分类侧边栏和商品列表 */
.products-main { 
  display: flex; 
  gap: 0; 
  min-height: 500px; 
  background: #fff; 
  padding: 15px; 
}
.category-sidebar {
  width: 200px;
  background: #fff;
  padding: 0;
  flex-shrink: 0;
}
.category-title {
  background: #e4393c;
  color: #fff;
  padding: 12px 15px;
  font-size: 14px;
  font-weight: bold;
}
.category-item {
  padding: 12px 15px;
  font-size: 13px;
  cursor: pointer;
  border-bottom: 1px solid #f5f5f5;
  display: flex;
  align-items: center;
  transition: all 0.2s;
}
.category-item:hover { background: #f5f5f5; }
.category-item.active { 
  background: #ffe4d6; 
  color: #e4393c;
}
.cat-icon { margin-right: 8px; }

/* 商品列表区域 */
.products-main { flex: 1; padding-left: 20px; }

.page-title { font-size: 18px; font-weight: 400; color: #666; margin-bottom: 15px; }

.search-tips { 
  background: #fff9e6; 
  padding: 10px 15px; 
  margin-bottom: 15px;
  font-size: 12px;
}
.search-tips span { color: #e4393c; }

.product-list { 
  display: flex; 
  flex-wrap: wrap; 
  gap: 10px;
}

.product-item { 
  width: calc(25% - 8px); 
  min-width: 200px;
  background: #fff; 
  cursor: pointer; 
  transition: all 0.2s;
  border: 1px solid transparent;
}
.product-item:hover { 
  border-color: #e4393c; 
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.product-img { 
  width: 100%; 
  height: 200px; 
  display: flex; 
  align-items: center; 
  justify-content: center;
  background: #f5f5f5;
  overflow: hidden;
}
.product-img img { 
  max-width: 100%; 
  max-height: 100%; 
  object-fit: contain;
}

.product-info { padding: 10px; }
.product-name { 
  font-size: 14px; 
  line-height: 1.5; 
  height: 42px; 
  overflow: hidden;
  margin-bottom: 8px;
  color: #333;
}
.product-item:hover .product-name { color: #e4393c; }

.product-desc { 
  font-size: 12px; 
  color: #999; 
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-price { margin-bottom: 8px; }
.price-symbol { color: #e4393c; font-size: 14px; font-weight: bold; }
.price-value { color: #e4393c; font-size: 22px; font-weight: bold; }

.product-actions { margin-bottom: 8px; }
.btn-cart { 
  background: #ffe4d6; 
  color: #e4393c; 
  border: 1px solid #ffb900;
  padding: 4px 15px;
  cursor: pointer;
  font-size: 12px;
  border-radius: 2px;
}
.btn-cart:hover { background: #e4393c; color: #fff; }

.product-meta { font-size: 12px; color: #999; }

.empty { text-align: center; padding: 50px; }
.empty img { width: 200px; }
.empty p { color: #999; margin-top: 10px; }
</style>
