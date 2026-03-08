<template>
  <div class="login-page">
    <div class="login-box">
      <div class="login-header">
        <h2>账号登录</h2>
      </div>
      <div class="login-form">
        <div class="form-item">
          <span class="icon">👤</span>
          <input type="text" v-model="form.username" placeholder="用户名" />
        </div>
        <div class="form-item">
          <span class="icon">🔒</span>
          <input type="password" v-model="form.password" placeholder="密码" />
        </div>
        <div class="form-actions">
          <label><input type="checkbox" v-model="remember" /> 记住登录</label>
        </div>
        <button class="btn-login" @click="submit" :loading="loading">登录</button>
        <div class="footer">
          <a href="#" @click.prevent="$router.push('/register')">立即注册</a>
          <a href="#">忘记密码？</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { userAPI } from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const form = ref({ username: '', password: '' })
const remember = ref(false)
const loading = ref(false)
const formRef = ref(null)

const submit = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await userAPI.login(form.value)
    if (remember.value) {
      localStorage.setItem('token', res.access_token)
      localStorage.setItem('username', form.value.username)
    } else {
      sessionStorage.setItem('token', res.access_token)
      sessionStorage.setItem('username', form.value.username)
    }
    ElMessage.success('登录成功')
    router.push('/products')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 50px 0;
}

.login-box {
  width: 350px;
  background: #fff;
  border: 1px solid #e4e7ed;
}

.login-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
}
.login-header h2 { font-size: 20px; font-weight: 400; color: #333; }

.login-form { padding: 30px; }

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

.form-actions {
  margin-bottom: 15px;
  font-size: 12px;
  color: #999;
}
.form-actions label { cursor: pointer; }

.btn-login {
  width: 100%;
  height: 40px;
  background: #e4393c;
  color: #fff;
  border: none;
  font-size: 16px;
  cursor: pointer;
}
.btn-login:hover { background: #c23531; }

.footer {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}
.footer a { color: #999; }
.footer a:hover { color: #e4393c; }
</style>
