<template>
  <div class="profile-page">
    <h2 class="page-title">个人中心</h2>
    
    <div class="profile-content">
      <!-- 用户信息 -->
      <div class="profile-card">
        <h3>基本信息</h3>
        <div class="form-group">
          <label>用户名</label>
          <input type="text" v-model="profile.username" />
        </div>
        <div class="form-group">
          <label>邮箱</label>
          <input type="email" v-model="profile.email" />
        </div>
        <button class="btn-save" @click="saveProfile">保存修改</button>
      </div>
      
      <!-- 修改密码 -->
      <div class="profile-card">
        <h3>修改密码</h3>
        <div class="form-group">
          <label>当前密码</label>
          <input type="password" v-model="password.old" />
        </div>
        <div class="form-group">
          <label>新密码</label>
          <input type="password" v-model="password.new" />
        </div>
        <div class="form-group">
          <label>确认新密码</label>
          <input type="password" v-model="password.confirm" />
        </div>
        <button class="btn-save" @click="changePassword">修改密码</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { userAPI } from '../api'
import { ElMessage } from 'element-plus'

const profile = ref({ username: '', email: '' })
const password = ref({ old: '', new: '', confirm: '' })

const loadProfile = async () => {
  try {
    const data = await userAPI.profile()
    profile.value = { username: data.username || '', email: data.email || '' }
  } catch (e) {
    ElMessage.error('获取用户信息失败')
  }
}

const saveProfile = async () => {
  try {
    await userAPI.updateProfile(profile.value)
    localStorage.setItem('username', profile.value.username)
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  }
}

const changePassword = async () => {
  if (!password.value.old || !password.value.new) {
    ElMessage.warning('请填写完整')
    return
  }
  if (password.value.new !== password.value.confirm) {
    ElMessage.warning('两次密码不一致')
    return
  }
  if (password.value.new.length < 6) {
    ElMessage.warning('密码至少6位')
    return
  }
  try {
    await userAPI.changePassword(password.value.old, password.value.new)
    ElMessage.success('密码修改成功，请重新登录')
    password.value = { old: '', new: '', confirm: '' }
    setTimeout(() => {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }, 1500)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '修改失败')
  }
}

onMounted(loadProfile)
</script>

<style scoped>
.profile-page { padding: 10px; }
.page-title { font-size: 18px; font-weight: 400; color: #333; margin-bottom: 20px; }

.profile-content { display: flex; gap: 20px; }

.profile-card {
  flex: 1;
  background: #fff;
  padding: 20px;
  border: 1px solid #e4e7ed;
}
.profile-card h3 { 
  font-size: 16px; 
  font-weight: 400; 
  color: #333; 
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.form-group { margin-bottom: 15px; }
.form-group label { 
  display: block; 
  font-size: 12px; 
  color: #999; 
  margin-bottom: 5px; 
}
.form-group input { 
  width: 100%; 
  height: 36px; 
  border: 1px solid #ccc; 
  padding: 0 10px; 
  font-size: 14px;
}

.btn-save {
  background: #e4393c; color: #fff;
  border: none; padding: 10px 30px;
  cursor: pointer; font-size: 14px;
}
.btn-save:hover { background: #c23531; }
</style>
