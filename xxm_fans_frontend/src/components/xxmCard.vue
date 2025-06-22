<template>
  <div class="xxm-card">
    <img class="avatar" :src="avatarUrl" alt="头像" />
    <h2 class="username">{{ username }}</h2>
  </div>
</template>

<script setup>
const avatarUrl = '/src/assets/xxmHeader.jpg'  // ✅ 你的头像路径
const username = '咻咻满'
// const description = 'test'
</script>

<style scoped>
.xxm-card {
  text-align: center;
  padding: 20px;
  margin-top: 20px;
  color: #333;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
}

.username {
  font-size: 24px;
  font-weight: bold;
  margin-top: 10px;
}
</style>
