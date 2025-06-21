<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

const songs = ref([])
const total = ref(0)
const curPage = ref(1)
const pageSize = 50

const fetchSongs = async () => {
  try {
    const res = await axios.get('/api/songs', {
      params: {
        page: curPage.value,
        limit: pageSize,
      }
    })
    songs.value = res.data.results
    total.value = res.data.total
  } catch (err) {
    console.error('❌ 获取失败:', err)
  }
}

// 第一次加载 + 翻页时调用
onMounted(fetchSongs)
watch(curPage, fetchSongs)
</script>

<template>
  <div class="song-list-container">
    <h2>歌曲列表</h2>

    <el-table :data="songs" stripe border style="width: 100%" fit>
      <el-table-column prop="id" label="No" min-width="130" align="center" header-align="center" />
      <el-table-column prop="song_name" label="歌曲名" min-width="130" align="center" header-align="center" />
      <el-table-column prop="singer" label="歌手" min-width="100" align="center" header-align="center" />
      <el-table-column prop="last_performed" label="最近一次演唱" min-width="140" align="center" header-align="center" />
      <el-table-column prop="perform_count" label="演唱次数" min-width="100" align="center" header-align="center" />
    </el-table>

    <el-pagination
      v-model:current-page="curPage"
      :page-size="pageSize"
      :total="total"
      layout="prev, pager, next"
      background
      style="margin-top: 20px; text-align: center"
    />
  </div>
</template>

<style scoped>
.song-list-container {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
  text-align: center;
}
</style>
