<template>
  <div class="song-tabs-wrapper">
    <!-- 标签页 -->
    <div class="tab-header">
      <div
        class="tab-item"
        :class="{ active: activeTab === 'top' }"
        @click="switchTab('top')"
      >
        热歌榜
      </div>
      <div
        class="tab-item"
        :class="{ active: activeTab === 'songs' }"
        @click="switchTab('songs')"
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
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// ✅ 直接引用两个页面
// import TopChart from './TopChart.vue'
import SongList from '../views/SongList.vue'
import TopChart from '../views/TopChart.vue'

const route = useRoute()
const router = useRouter()
const activeTab = ref('songs')

// 路由参数控制标签页
watch(
  () => route.query.tab,
  (val) => {
    if (val === 'top' || val === 'songs') {
      activeTab.value = val
    }
  },
  { immediate: true }
)

function switchTab(tab) {
  activeTab.value = tab
  router.replace({ query: { ...route.query, tab } })
}
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
  background-color: rgba(255,255,255,0.7);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
</style>
