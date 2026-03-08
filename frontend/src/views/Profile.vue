<template>
  <div class="profile-page">
    <h2 class="page-title">个人中心</h2>
    
    <div class="profile-content">
      <!-- 头像 -->
      <div class="profile-avatar-card">
        <div class="avatar-wrapper">
          <img :src="profile.avatar_url || defaultAvatar" class="avatar" />
          <el-upload
            class="avatar-upload"
            :show-file-list="false"
            :before-upload="handleAvatarUpload"
            action="#"
          >
            <button class="btn-change-avatar">更换头像</button>
          </el-upload>
        </div>
        <div class="username">{{ profile.username }}</div>
      </div>
      
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

const profile = ref({ username: '', email: '', avatar_url: '' })
const password = ref({ old: '', new: '', confirm: '' })
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const loadProfile = async () => {
  try {
    const data = await userAPI.profile()
    profile.value = { username: data.username || '', email: data.email || '', avatar_url: data.avatar_url || '' }
  } catch (e) {
    ElMessage.error('获取用户信息失败')
  }
}

const handleAvatarUpload = async (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB')
    return false
  }
  // 转换为 Base64
  const reader = new FileReader()
  reader.onload = (e) => {
    profile.value.avatar_url = e.target.result
    saveProfile()
  }
  reader.readAsDataURL(file)
  return false
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
      localStorage.removeItem('username')
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('username')
      window.location.href = '/login'
    }, 1500))
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '修改失败')
  }
}

onMounted(loadProfile)
</script>

<style scoped>
.profile-page { padding: 10px; }
.page-title { font-size: 18px; font-weight: 400; color: #333; margin-bottom: 20px; }

.profile-content { display: flex; gap: 20px; flex-wrap: wrap; }

/* 头像卡片 */
.profile-avatar-card {
  width: 200px;
  background: #fff;
  padding: 30px 20px;
  border: 1px solid #e4e7ed;
  text-align: center;
}
.avatar-wrapper { position: relative; display: inline-block; }
.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #f5f5f5;
}
.avatar-upload {
  margin-top: 15px;
}
.btn-change-avatar {
  background: #fff;
  border: 1px solid #dcdfe6;
  padding: 6px 15px;
  font-size: 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s;
}
.btn-change-avatar:hover {
  border-color: #e4393c;
  color: #e4393c;
}
.username {
  margin-top: 15px;
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.profile-card {
  flex: 1;
  min-width: 300px;
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
