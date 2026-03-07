import axios from 'axios'

// 环境变量配置API地址
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000
})

// 请求拦截器 - 自动带上token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  response => response.data,
  error => {
    const status = error.response?.status
    const data = error.response?.data
    
    let msg = '请求失败，请稍后重试'
    if (status === 401) {
      localStorage.removeItem('token')
      msg = '登录已过期，请重新登录'
    } else if (status === 403) {
      msg = '没有权限执行此操作'
    } else if (status === 404) {
      msg = '请求的资源不存在'
    } else if (status === 500) {
      msg = '服务器错误，请稍后重试'
    } else if (data?.msg) {
      msg = data.msg
    }
    
    // 可以用 Element Plus 的 ElMessage 显示
    if (typeof window !== 'undefined' && window.ElMessage) {
      window.ElMessage.error(msg)
    }
    
    return Promise.reject(new Error(msg))
  }
)

// 用户相关
export const userAPI = {
  register: (data) => api.post('/api/user/register', data),
  login: (data) => api.post('/api/user/login', data),
  profile: () => api.get('/api/user/profile'),
  updateProfile: (data) => api.put('/api/user/profile', data),
  changePassword: (oldPassword, newPassword) => api.put('/api/user/password', { old_password: oldPassword, new_password: newPassword }),
}

// 商品相关
export const productAPI = {
  list: (keyword = '') => api.get('/api/product/list', { params: { keyword } }),
  detail: (id) => api.get(`/api/product/detail/${id}`),
}

// 分类相关
export const categoryAPI = {
  list: () => api.get('/api/category/list'),
  products: (categoryId, keyword = '') => api.get(`/api/category/${categoryId}/products`, { params: { keyword } }),
}

// 评论相关
export const reviewAPI = {
  list: (productId) => api.get(`/api/product/${productId}/reviews`),
  count: (productId) => api.get(`/api/product/${productId}/reviews/count`),
  add: (data) => api.post(`/api/product/${data.product_id}/review`, data),
}

// 购物车相关
export const cartAPI = {
  add: (data) => {
    const token = localStorage.getItem('token')
    return api.post('/api/cart/add', data, {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    })
  },
  update: (data) => api.post('/api/cart/update', data),
  list: () => api.get('/api/cart/list'),
}

// 订单相关
export const orderAPI = {
  create: (data) => api.post('/api/order/create', data),
  list: () => api.get('/api/order/list'),
  pay: (orderId) => api.post(`/api/order/${orderId}/pay`),
  cancel: (orderId) => api.post(`/api/order/${orderId}/cancel`),
}

export default api
