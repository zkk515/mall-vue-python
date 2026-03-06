<template>
  <div class="orders-page">
    <h2 class="page-title">我的订单</h2>
    
    <!-- 订单列表 -->
    <div class="order-list" v-if="list.length">
      <div class="order-item" v-for="order in list" :key="order.id">
        <div class="order-header">
          <div class="order-info-left">
            <span class="order-id">订单号: {{ order.id }}</span>
            <span class="order-date">{{ order.created_at }}</span>
          </div>
          <div class="order-info-right">
            <span class="order-status" :class="order.status">{{ order.status_text }}</span>
            <span class="order-total">¥{{ order.total_amount }}</span>
          </div>
        </div>
        
        <div class="order-products">
          <div class="product-item" v-for="item in order.items" :key="item.id">
            <img :src="item.product_image" class="product-img" />
            <div class="product-info">
              <div class="product-name">{{ item.product_name }}</div>
              <div class="product-price">¥{{ item.price }} × {{ item.quantity }}</div>
            </div>
            <div class="product-total">¥{{ (item.price * item.quantity).toFixed(2) }}</div>
          </div>
        </div>
        
        <div class="order-footer">
          <div class="receiver-info">
            <span>收货人: {{ order.receiver_name }}</span>
            <span>电话: {{ order.receiver_phone }}</span>
            <span>地址: {{ order.receiver_address }}</span>
          </div>
          <div class="order-actions">
            <button class="btn-primary" v-if="order.status === 'pending'" @click="handlePay(order.id)">去支付</button>
            <button class="btn-danger" v-if="order.status === 'pending'" @click="handleCancel(order.id)">取消订单</button>
            <button class="btn-default" @click="viewDetail(order)">查看详情</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div class="order-empty" v-else>
      <img src="https://img12.360buyimg.com/vclist/jfs/t1/120989/20/14942/158/5e7a8f2aEbf730d76/91c2e937d2b24e31.png" />
      <p>暂无订单，快去购物吧~</p>
      <button @click="$router.push('/products')">去购物</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { orderAPI } from '../api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const list = ref([])

const statusMap = {
  'pending': '待支付',
  'paid': '已支付',
  'shipped': '待收货',
  'completed': '已完成',
  'cancelled': '已取消'
}

const loadOrders = async () => {
  loading.value = true
  try {
    const data = await orderAPI.list()
    list.value = data.map(order => ({
      ...order,
      status_text: statusMap[order.status] || order.status,
      created_at: order.created_at ? order.created_at.substring(0, 10) : ''
    }))
  } finally {
    loading.value = false
  }
}

const handlePay = async (orderId) => {
  try {
    await orderAPI.pay(orderId)
    ElMessage.success('支付成功')
    loadOrders()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '支付失败')
  }
}

const handleCancel = async (orderId) => {
  if (!confirm('确定要取消订单吗？')) return
  try {
    await orderAPI.cancel(orderId)
    ElMessage.success('订单已取消')
    loadOrders()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '取消失败')
  }
}

const viewDetail = (order) => {
  ElMessage.info(`订单${order.id}详情`)
}

onMounted(loadOrders)
</script>

<style scoped>
.orders-page { padding: 10px; }
.page-title { font-size: 18px; font-weight: 400; color: #333; margin-bottom: 20px; }

.order-item { 
  background: #fff; 
  margin-bottom: 15px; 
  border: 1px solid #e4e7ed;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: #f5f5f5;
  border-bottom: 1px solid #e4e7ed;
}
.order-id { font-weight: bold; color: #333; margin-right: 20px; }
.order-date { color: #999; font-size: 12px; }
.order-info-right { display: flex; align-items: center; gap: 20px; }
.order-status { 
  padding: 2px 10px; 
  border-radius: 2px; 
  font-size: 12px;
}
.order-status.pending { background: #fff3e0; color: #ff9800; }
.order-status.paid { background: #e3f2fd; color: #2196f3; }
.order-status.shipped { background: #e8f5e9; color: #4caf50; }
.order-status.completed { background: #f5f5f5; color: #999; }
.order-status.cancelled { background: #fce4ec; color: #f44336; }
.order-total { 
  color: #e4393c; 
  font-size: 20px; 
  font-weight: bold; 
}

.order-products { padding: 15px 20px; }
.product-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
}
.product-item:last-child { border-bottom: none; }
.product-img { width: 60px; height: 60px; object-fit: contain; margin-right: 15px; }
.product-info { flex: 1; }
.product-name { font-size: 14px; color: #333; }
.product-price { font-size: 12px; color: #999; margin-top: 5px; }
.product-total { color: #e4393c; font-weight: bold; }

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-top: 1px solid #e4e7ed;
}
.receiver-info { font-size: 12px; color: #999; }
.receiver-info span { margin-right: 20px; }

.order-actions { display: flex; gap: 10px; }
.btn-primary {
  background: #e4393c; color: #fff;
  border: none; padding: 8px 20px;
  cursor: pointer; font-size: 12px;
}
.btn-primary:hover { background: #c23531; }
.btn-danger {
  background: #fff; color: #666;
  border: 1px solid #ccc; padding: 8px 20px;
  cursor: pointer; font-size: 12px;
}
.btn-danger:hover { border-color: #f44336; color: #f44336; }
.btn-default {
  background: #fff; color: #666;
  border: 1px solid #ccc; padding: 8px 20px;
  cursor: pointer; font-size: 12px;
}
.btn-default:hover { border-color: #999; color: #333; }

.order-empty { text-align: center; padding: 80px 0; background: #fff; }
.order-empty img { width: 150px; }
.order-empty p { color: #999; margin: 20px 0; }
.order-empty button {
  background: #e4393c; color: #fff;
  border: none; padding: 10px 30px;
  cursor: pointer;
}
</style>
