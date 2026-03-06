<template>
  <div class="cart-page">
    <h2 class="page-title">我的购物车</h2>
    
    <!-- 购物车表头 -->
    <div class="cart-header">
      <div class="col-check">
        <input type="checkbox" v-model="allChecked" @change="checkAll" />
        <span>全选</span>
      </div>
      <div class="col-img">商品图片</div>
      <div class="col-info">商品信息</div>
      <div class="col-price">单价</div>
      <div class="col-quantity">数量</div>
      <div class="col-total">小计</div>
      <div class="col-action">操作</div>
    </div>
    
    <!-- 购物车商品 -->
    <div class="cart-list" v-if="list.length">
      <div class="cart-item" v-for="row in list" :key="row.id">
        <div class="col-check">
          <input type="checkbox" v-model="row.checked" @change="calcTotal" />
        </div>
        <div class="col-img">
          <img :src="row.product_image" />
        </div>
        <div class="col-info">
          <div class="product-name">{{ row.product_name }}</div>
        </div>
        <div class="col-price">¥{{ row.product_price }}</div>
        <div class="col-quantity">
          <div class="quantity-input">
            <button @click="updateQuantity(row, row.quantity - 1)">-</button>
            <input type="text" v-model="row.quantity" @change="updateQuantity(row, row.quantity)" />
            <button @click="updateQuantity(row, row.quantity + 1)">+</button>
          </div>
        </div>
        <div class="col-total">¥{{ (row.product_price * row.quantity).toFixed(2) }}</div>
        <div class="col-action">
          <a href="#" @click.prevent="updateQuantity(row, 0)">删除</a>
        </div>
      </div>
    </div>
    
    <!-- 空购物车 -->
    <div class="cart-empty" v-else>
      <img src="https://img12.360buyimg.com/vclist/jfs/t1/120989/20/14942/158/5e7a8f2aEbf730d76/91c2e937d2b24e31.png" />
      <p>购物车空空的，去逛逛吧~</p>
      <button @click="$router.push('/products')">去购物</button>
    </div>
    
    <!-- 结算栏 -->
    <div class="cart-footer" v-if="list.length">
      <div class="footer-left">
        <a href="#" @click.prevent="clearChecked">清空已选</a>
      </div>
      <div class="footer-right">
        <span class="total-price">总价: <b>¥{{ total.toFixed(2) }}</b></span>
        <button class="btn-checkout" @click="checkout">去结算</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { cartAPI } from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const list = ref([])
const allChecked = ref(false)

const total = computed(() => {
  return list.value.filter(r => r.checked).reduce((sum, r) => sum + r.product_price * r.quantity, 0)
})

const loadCart = async () => {
  const data = await cartAPI.list()
  list.value = data.map(item => ({ ...item, checked: false }))
}

const updateQuantity = async (row, quantity) => {
  if (quantity <= 0) {
    if (confirm('确定要删除这件商品吗？')) {
      await cartAPI.update({ product_id: row.product_id, quantity: 0 })
      await loadCart()
    }
  } else {
    await cartAPI.update({ product_id: row.product_id, quantity })
    row.quantity = quantity
    calcTotal()
  }
}

const checkAll = () => {
  list.value.forEach(r => r.checked = allChecked.value)
}

const calcTotal = () => {
  allChecked.value = list.value.length > 0 && list.value.every(r => r.checked)
}

const checkout = async () => {
  const checkedItems = list.value.filter(r => r.checked)
  if (!checkedItems.length) {
    ElMessage.warning('请先选择商品')
    return
  }
  router.push('/orders')
}

onMounted(loadCart)
</script>

<style scoped>
.cart-page { padding: 10px; }
.page-title { font-size: 18px; font-weight: 400; color: #333; margin-bottom: 20px; }

.cart-header {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  padding: 15px 20px;
  font-size: 12px;
  color: #999;
}
.cart-item {
  display: flex;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fff;
}

.col-check { width: 80px; }
.col-img { width: 80px; height: 80px; }
.col-img img { width: 100%; height: 100%; object-fit: contain; }
.col-info { flex: 1; padding: 0 15px; }
.product-name { font-size: 14px; color: #333; line-height: 1.5; }
.col-price { width: 120px; text-align: center; color: #333; }
.col-quantity { width: 150px; text-align: center; }
.col-total { width: 120px; text-align: center; color: #e4393c; font-weight: bold; }
.col-action { width: 80px; text-align: center; }
.col-action a { color: #999; font-size: 12px; }
.col-action a:hover { color: #e4393c; }

.quantity-input { display: flex; align-items: center; justify-content: center; }
.quantity-input button { 
  width: 28px; height: 28px; 
  border: 1px solid #ccc; 
  background: #f5f5f5;
  cursor: pointer;
}
.quantity-input input { 
  width: 50px; height: 26px; 
  border: 1px solid #ccc; 
  border-left: none; border-right: none;
  text-align: center; outline: none;
}

.cart-empty { 
  text-align: center; padding: 80px 0; 
  background: #fff;
}
.cart-empty img { width: 150px; }
.cart-empty p { color: #999; margin: 20px 0; }
.cart-empty button {
  background: #e4393c; color: #fff;
  border: none; padding: 10px 30px;
  cursor: pointer;
}

.cart-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 20px;
  border-top: 2px solid #e4393c;
}
.footer-left a { color: #999; font-size: 12px; }
.total-price { font-size: 14px; color: #333; margin-right: 20px; }
.total-price b { color: #e4393c; font-size: 24px; }
.btn-checkout {
  background: #e4393c; color: #fff;
  border: none; padding: 15px 40px;
  font-size: 18px; cursor: pointer;
}
.btn-checkout:hover { background: #c23531; }
</style>
