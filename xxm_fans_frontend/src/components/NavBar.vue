<template>
  <div class="navbar">
    <div class="navbar-left">
      <img src="/covers/default.jpg" class="logo" alt="logo" />
      <span class="title">小满虫之家</span>
    </div>
    <div class="navbar-right">
      <el-button link @click="go('/songs')" :class="{active: isActive('/songs')}">满的歌声</el-button>
      <el-button link @click="go('/footprint')" :class="{active: isActive('/footprint')}">满的足迹</el-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
const router = useRouter()
const route = useRoute()
function go(path) {
  router.push(path)
}
function isActive(path) {
  return route.path.startsWith(path)
}
</script>

<style scoped>
.navbar {
  width: 100%;
  height: 56px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 4vw;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 100;
  box-sizing: border-box;
}
.navbar-left {
  display: flex;
  align-items: center;
}
.logo {
  width: 36px;
  height: 36px;
  margin-right: 12px;
}
.title {
  font-size: 22px;
  font-weight: bold;
  color: #222;
}
.navbar-right {
  display: flex;
  gap: 18px;
}
.el-button {
  font-size: 16px;
  color: #333;
}
.el-button.active, .el-button:hover {
  color: #fda5c1;
  font-weight: bold;
}
@media (max-width: 600px) {
  .navbar {
    padding: 0 8px;
  }
  .title {
    font-size: 16px;
  }
  .logo {
    width: 28px;
    height: 28px;
  }
  .el-button {
    font-size: 13px;
    padding: 0 6px;
  }
}
</style> 