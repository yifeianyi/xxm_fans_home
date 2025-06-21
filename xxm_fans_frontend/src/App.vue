<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeIndex = ref('1')

const handleSelect = (key) => {
  router.push(key)
}
</script>

<template>
  <el-container style="min-height: 100vh;">

    <!-- 顶部固定导航 -->
    <el-header
      style="
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        width: 100%;
        z-index: 1000;
        background-color: white;
        display: flex;
        padding: 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
      "
    >
      <el-menu
        :default-active="activeIndex"
        mode="horizontal"
        @select="handleSelect"
        style="flex: 1;"
      >
        <el-menu-item index="/songs">Processing Center</el-menu-item>
        <el-sub-menu index="2">
          <template #title>Workspace</template>
          <el-menu-item index="/w1">item one</el-menu-item>
          <el-menu-item index="/w2">item two</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/info" disabled>Info</el-menu-item>
        <el-menu-item index="/orders">Orders</el-menu-item>
      </el-menu>
    </el-header>

    <!-- 主体区域 -->
    <el-main style="padding-top: 60px;">
      <router-view />
    </el-main>

  </el-container>
</template>
