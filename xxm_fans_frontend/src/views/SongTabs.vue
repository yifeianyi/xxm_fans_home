<template>
  <div class="song-tabs-wrapper">
    <!-- 标签页 -->
    <div class="tab-header">
      <div
        class="tab-item"
        :class="{ active: activeTab === 'top' }"
        @click="activeTab = 'top'"
      >
        热歌榜
      </div>
      <div
        class="tab-item"
        :class="{ active: activeTab === 'songs' }"
        @click="activeTab = 'songs'"
      >
        歌单
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="tab-content">
      <TopChart v-if="activeTab === 'top'" />
      <SongList v-else />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// ✅ 直接引用两个页面
import TopChart from './TopChart.vue'
import SongList from './SongList.vue'

const activeTab = ref('songs')
</script>

<style scoped>
.song-tabs-wrapper {
  max-width: 1000px;
  margin: 0 auto;
}

.tab-header {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.tab-item {
  padding: 10px 30px;
  margin: 0 8px;
  border-radius: 30px;
  background-color: #f0f0f0;
  color: #555;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-item.active {
  background-color: #fda5c1;
  color: white;
}

.tab-content {
  padding: 20px;
  border-radius: 12px;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
</style>
