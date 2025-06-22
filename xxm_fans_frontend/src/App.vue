<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import xxmCard from './components/xxmCard.vue' 
const router = useRouter()
const activeIndex = ref('1')

const handleSelect = (key) => {
  router.push(key)
}
</script>

<template>
<xxmCard />
    <!-- <el-header>
        
    </el-header>
     -->
  <el-container style="min-height: 100vh;">
    <!-- 主体区域 -->
    <el-main style="padding-top: 60px;">
      <router-view />
    </el-main>

  </el-container>
</template>
<style>
html, body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  background-image: url('./assets/background.jpg'); /* ✅ 替换为你的图片路径 */
  background-repeat: repeat-y;
  background-size: 100% auto;
  background-position: top center;
  background-attachment: scroll;
  overflow-x: hidden;
}
</style>