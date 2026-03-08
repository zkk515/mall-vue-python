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
    
    <!-- 主体内容：左侧分类 + 右侧商品 -->
    <div class="content-wrapper">
      <!-- 左侧分类 -->
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
      
      <!-- 右侧商品列表 -->
      <div class="products-main">
        <h2 class="page-title">{{ pageTitle }}</h2>
        
        <!-- 搜索结果提示 -->
        <div class="search-tips" v-if="keyword">
          搜索"<span>{{ keyword }}</span>"，找到 {{ total }} 件商品
        </div>
        
        <!-- 排序和筛选 -->
        <div class="filter-bar">
          <div class="sort-buttons">
            <button 
              :class="{ active: sortBy === 'default' }" 
              @click="sortBy = 'default'; loadProducts()"
            >默认</button>
            <button 
              :class="{ active: sortBy === 'price_asc' }" 
              @click="sortBy = 'price_asc'; loadProducts()"
            >价格 ↑</button>
            <button 
              :class="{ active: sortBy === 'price_desc' }" 
              @click="sortBy = 'price_desc'; loadProducts()"
            >价格 ↓</button>
            <button 
              :class="{ active: sortBy === 'sales' }" 
              @click="sortBy = 'sales'; loadProducts()"
            >销量</button>
          </div>
          <div class="view-toggle">
            <span :class="{ active: viewMode === 'grid' }" @click="viewMode = 'grid'">▦</span>
            <span :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'">☰</span>
          </div>
        </div>
        
        <!-- 商品列表 -->
        <div class="product-list" :class="{ 'list-view': viewMode === 'list' }">
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
        
        <!-- 分页 -->
        <div class="pagination" v-if="total > pageSize">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            layout="prev, pager, next, total"
            @current-change="handlePageChange"
          />
        </div>
        
        <!-- 空状态 -->
        <div class="empty" v-if="!loading && list.length === 0">
          <img src="https://img12.360buyimg.com/vclist/jfs/t1/120989/20/14942/158/5e7a8f2aEbf730d76/91c2e937d2b24e31.png" />
          <p>暂无商品</p>
        </div>
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
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('default')
const viewMode = ref('grid')
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
    const params = { 
      keyword: keyword.value, 
      page: currentPage.value, 
      page_size: pageSize.value,
      sort: sortBy.value
    }
    if (activeCategory.value) {
      const res = await categoryAPI.products(activeCategory.value, keyword.value, currentPage.value, pageSize.value)
      list.value = res.items || res.products || res || []
      total.value = res.total || list.value.length
    } else {
      const res = await productAPI.list(keyword.value, currentPage.value, pageSize.value)
      list.value = res.items || res.products || res || []
      total.value = res.total || list.value.length
    }
    // 前端排序（后端不支持时使用）
    if (sortBy.value === 'price_asc') {
      list.value.sort((a, b) => (a.price || 0) - (b.price || 0))
    } else if (sortBy.value === 'price_desc') {
      list.value.sort((a, b) => (b.price || 0) - (a.price || 0))
    }
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadProducts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const selectCategory = (id) => {
  activeCategory.value = activeCategory.value === id ? 0 : id
  keyword.value = ''
  currentPage.value = 1
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
  currentPage.value = 1
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
/* ========== UI设计规范 ========== */
.products-page { 
  display: flex; 
  flex-direction: column; 
  gap: var(--spacing-md, 16px); 
  min-height: 500px; 
}

/* 轮播图 */
.banner-carousel {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius, 8px);
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
  transition: background 0.3s;
}
.carousel-dots span.active { background: #fff; }

/* 主体内容：左侧分类 + 右侧商品 */
.content-wrapper {
  display: flex;
  gap: 0;
  background: var(--card-bg, #fff);
  border-radius: var(--radius, 8px);
  box-shadow: var(--shadow, 0 2px 8px rgba(0,0,0,0.08));
  overflow: hidden;
}

/* 分类侧边栏 */
.category-sidebar {
  width: 200px;
  background: #F7F7F7;
  padding: 0;
  flex-shrink: 0;
}
.category-title {
  background: var(--primary, #E4393C);
  color: #fff;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: bold;
}
.category-item {
  padding: 12px 16px;
  font-size: 13px;
  cursor: pointer;
  border-bottom: 1px solid #f5f5f5;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}
.category-item:hover { background: #f5f5f5; }
.category-item.active { 
  background: #ffe4d6; 
  color: var(--primary, #E4393C);
}
.cat-icon { margin-right: 8px; }

/* 商品列表区域 */
.products-main { flex: 1; padding-left: var(--spacing-lg, 24px); }

.page-title { font-size: 20px; font-weight: 400; color: var(--text-secondary, #999); margin-bottom: var(--spacing-md, 16px); }

.search-tips { 
  background: #fff9e6; 
  padding: 10px 16px; 
  margin-bottom: var(--spacing-md, 16px);
  font-size: 12px;
  border-radius: var(--radius, 8px);
}
.search-tips span { color: var(--primary, #E4393C); font-weight: bold; }

/* 排序和筛选 */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md, 16px);
  padding: 10px 0;
}
.sort-buttons {
  display: flex;
  gap: 5px;
}
.sort-buttons button {
  padding: 6px 12px;
  border: 1px solid #e4e7ed;
  background: #fff;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
}
.sort-buttons button:hover { border-color: #e4393c; color: #e4393c; }
.sort-buttons button.active { background: #e4393c; color: #fff; border-color: #e4393c; }

.view-toggle {
  display: flex;
  gap: 10px;
  font-size: 18px;
  cursor: pointer;
}
.view-toggle span {
  color: #ccc;
  transition: color 0.3s;
}
.view-toggle span.active { color: #e4393c; }

/* 列表视图 */
.product-list.list-view { flex-direction: column; }
.product-list.list-view .product-item {
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
}
.product-list.list-view .product-img {
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}
.product-list.list-view .product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.product-list { 
  display: flex; 
  flex-wrap: wrap; 
  gap: 12px;
}

/* 商品卡片 */
.product-item { 
  width: calc(20% - 10px); 
  min-width: 200px;
  background: var(--card-bg, #fff); 
  cursor: pointer; 
  transition: all 0.3s ease;
  border: 1px solid var(--border, #E0E0E0);
  border-radius: var(--radius, 8px);
  overflow: hidden;
}
.product-item:hover { 
  border-color: var(--primary, #E4393C); 
  box-shadow: var(--shadow-hover, 0 4px 12px rgba(0,0,0,0.12));
  transform: translateY(-2px);
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
  transition: transform 0.3s ease;
}
.product-item:hover .product-img img { transform: scale(1.05); }

.product-info { padding: var(--spacing-sm, 8px) var(--spacing-md, 16px) var(--spacing-md, 16px); }
.product-name { 
  font-size: 14px; 
  line-height: 1.5; 
  height: 42px; 
  overflow: hidden;
  margin-bottom: 8px;
  color: var(--text-primary, #333);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.product-item:hover .product-name { color: var(--primary, #E4393C); }

.product-desc { 
  font-size: 12px; 
  color: var(--text-secondary, #999); 
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-price { margin-bottom: 8px; }
.price-symbol { color: var(--primary, #E4393C); font-size: 14px; font-weight: bold; }
.price-value { color: var(--primary, #E4393C); font-size: 22px; font-weight: bold; }

.product-actions { margin-bottom: 8px; }
.btn-cart { 
  background: #ffe4d6; 
  color: var(--primary, #E4393C); 
  border: none;
  padding: 6px 16px;
  cursor: pointer;
  font-size: 12px;
  border-radius: var(--radius, 8px);
  transition: all 0.3s ease;
}
.btn-cart:hover { 
  background: var(--primary, #E4393C); 
  color: #fff; 
}

.product-meta { font-size: 12px; color: var(--text-secondary, #999); }

.empty { text-align: center; padding: 50px; }
.empty img { width: 200px; }
.empty p { color: var(--text-secondary, #999); margin-top: 10px; }

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  padding: var(--spacing-lg, 24px) 0;
  margin-top: var(--spacing-md, 16px);
}
</style>
