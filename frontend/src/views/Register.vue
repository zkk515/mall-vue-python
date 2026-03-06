<template>
  <div class="register-page">
    <div class="register-box">
      <div class="register-header">
        <h2>新用户注册</h2>
      </div>
      <div class="register-form">
        <div class="form-item">
          <span class="icon">👤</span>
          <input type="text" v-model="form.username" placeholder="请输入用户名" />
        </div>
        <div class="form-item">
          <span class="icon">🔒</span>
          <input type="password" v-model="form.password" placeholder="请输入密码" />
        </div>
        <div class="form-item">
          <span class="icon">📧</span>
          <input type="email" v-model="form.email" placeholder="请输入邮箱（可选）" />
        </div>
        <button class="btn-register" @click="submit" :loading="loading">立即注册</button>
        <div class="footer">
          已有账号？<router-link to="/login">立即登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { userAPI } from '../api'

const router = useRouter()
const loading = ref(false)
const form = ref({ username: '', password: '', email: '' })

const submit = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await userAPI.register(form.value)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 500px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 50px 0;
}

.register-box {
  width: 350px;
  background: #fff;
  border: 1px solid #e4e7ed;
}

.register-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
}
.register-header h2 { font-size: 20px; font-weight: 400; color: #333; }

.register-form { padding: 30px; }

.form-item {
  display: flex;
  align-items: center;
  border: 1px solid #ccc;
  margin-bottom: 15px;
  height: 40px;
}
.form-item .icon { 
  width: 40px; 
  text-align: center; 
  color: #999;
  border-right: 1px solid #e4e7ed;
}
.form-item input {
  flex: 1;
  border: none;
  outline: none;
  padding: 0 15px;
  font-size: 14px;
}

.btn-register {
  width: 100%;
  height: 40px;
  background: #e4393c;
  color: #fff;
  border: none;
  font-size: 16px;
  cursor: pointer;
}
.btn-register:hover { background: #c23531; }

.footer {
  margin-top: 20px;
  text-align: center;
  font-size: 12px;
  color: #999;
}
.footer a { color: #e4393c; }
</style>
