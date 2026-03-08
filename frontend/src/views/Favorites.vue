<template>
  <div class="favorites-page">
    <h2 class="page-title">我的收藏</h2>
    
    <!-- 收藏列表 -->
    <div class="favorites-list" v-if="list.length">
      <div class="fav-item" v-for="item in list" :key="item.id">
        <img :src="item.image_url" class="fav-img" @click="$router.push(`/product/${item.product_id}`)" />
        <div class="fav-info">
          <div class="fav-name">{{ item.name }}</div>
          <div class="fav-price">¥{{ item.price }}</div>
        </div>
        <div class="fav-actions">
          <button class="btn-cart" @click="addToCart(item)">加入购物车</button>
          <button class="btn-remove" @click="removeFav(item.product_id)">删除</button>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div class="fav-empty" v-else>
      <img src="https://img12.360buyimg.com/vclist/jfs/t1/120989/20/14942/158/5e7a8f2aEbf730d76/91c2e937d2b24e31.png" />
      <p>暂无收藏，快去逛逛吧~</p>
      <button @click="$router.push('/products')">去购物</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { favoritesAPI, cartAPI } from '../api'
import { ElMessage } from 'element-plus'

const list = ref([])

const loadFavorites = async () => {
  try {
    list.value = await favoritesAPI.list()
  } catch (e) {
    ElMessage.error('加载收藏失败')
  }
}

const removeFav = async (productId) => {
  try {
    await favoritesAPI.remove(productId)
    ElMessage.success('已取消收藏')
    loadFavorites()
  } catch (e) {
    ElMessage.error(e.message || '操作失败')
  }
}

const addToCart = async (item) => {
  try {
    await cartAPI.add({ product_id: item.product_id, quantity: 1 })
    ElMessage.success('已加入购物车')
  } catch (e) {
    ElMessage.error(e.message || '添加失败')
  }
}

onMounted(loadFavorites)
</script>

<style scoped>
.favorites-page { padding: 10px; }
.page-title { font-size: 18px; font-weight: 400; color: #333; margin-bottom: 20px; }

.favorites-list { 
  background: #fff; 
  border: 1px solid #e4e7ed;
}

.fav-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #f5f5f5;
}
.fav-item:last-child { border-bottom: none; }

.fav-img { 
  width: 80px; 
  height: 80px; 
  object-fit: contain; 
  cursor: pointer;
  border: 1px solid #f5f5f5;
}

.fav-info { flex: 1; padding: 0 20px; }
.fav-name { font-size: 14px; color: #333; margin-bottom: 8px; cursor: pointer; }
.fav-name:hover { color: #e4393c; }
.fav-price { color: #e4393c; font-size: 18px; font-weight: bold; }

.fav-actions { display: flex; gap: 10px; }
.btn-cart {
  background: #e4393c; color: #fff;
  border: none; padding: 8px 16px;
  cursor: pointer; font-size: 12px;
  border-radius: 4px;
}
.btn-cart:hover { background: #c23531; }
.btn-remove {
  background: #fff; color: #666;
  border: 1px solid #ccc; padding: 8px 16px;
  cursor: pointer; font-size: 12px;
  border-radius: 4px;
}
.btn-remove:hover { border-color: #e4393c; color: #e4393c; }

.fav-empty { text-align: center; padding: 80px 0; background: #fff; }
.fav-empty img { width: 150px; }
.fav-empty p { color: #999; margin: 20px 0; }
.fav-empty button {
  background: #e4393c; color: #fff;
  border: none; padding: 10px 30px;
  cursor: pointer;
}
</style>
