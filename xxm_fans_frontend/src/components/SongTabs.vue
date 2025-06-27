<template>
  <div class="song-tabs-wrapper">
    <div class="custom-tabs">
      <div
        class="tab-btn"
        :class="{ active: activeTab === 'top' }"
        @click="switchTab('top')"
      >热歌榜</div>
      <div
        class="tab-btn"
        :class="{ active: activeTab === 'songs' }"
        @click="switchTab('songs')"
      >满的歌声</div>
    </div>
    <div class="card-content-bg">
      <div class="tab-content">
        <TopChart v-if="activeTab === 'top'" />
        <SongList v-else />
      </div>
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 20px 40px 20px;
  position: relative;
  background: transparent;
}
.custom-tabs {
  display: flex;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  border-radius: 22px;
  margin-bottom: 10px;
}
.tab-btn {
  flex: 1;
  height: 44px;
  font-size: 15px;
  font-weight: bold;
  color: #333;
  background: #fff;
  border: none;
  outline: none;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  user-select: none;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 22px;
}
.tab-btn.active {
  background: #fda5c1;
  color: #fff;
}
.card-content-bg {
  background: transparent;
  border-radius: 20px;
  width: 100%;
}
.tab-content {
  padding: 32px;
  min-height: 300px;
  background-color: rgb(250, 250, 250,0.7);
}
</style>
