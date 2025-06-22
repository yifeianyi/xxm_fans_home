<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

const songs = ref([])
const total = ref(0)
const curPage = ref(1)
const pageSize = 50

// 所有歌曲记录缓存：{ song_id: [record1, record2, ...] }
const records = ref({})
const loadingSet = ref(new Set())

// 展开行时加载演唱记录
const loadRecords = async (row) => {
  const songId = row.id

  if (records.value[songId]) return
  if (loadingSet.value.has(songId)) return
  loadingSet.value.add(songId)

  try {
    const res = await axios.get(`/api/songs/${songId}/records`)
    records.value[songId] = res.data
  } catch (err) {
    console.error(`❌ 获取演唱记录失败（id=${songId}）:`, err)
    records.value[songId] = []
  } finally {
    loadingSet.value.delete(songId)
  }
}

// 获取分页歌曲数据
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
    console.error('❌ 获取歌曲失败:', err)
  }
}

onMounted(fetchSongs)
watch(curPage, fetchSongs)
</script>



<template>
  <div class="song-list-container">
    <h2>歌曲列表</h2>

    <el-table
      :data="songs"
      stripe
      border
      fit
      style="width: 100%"
      @expand-change="loadRecords"
    >
      <el-table-column prop="id" label="No" min-width="80" align="center" header-align="center" />
      <el-table-column prop="song_name" label="歌曲名" min-width="130" align="center" header-align="center" />
      <el-table-column prop="singer" label="歌手" min-width="100" align="center" header-align="center" />
      <el-table-column prop="last_performed" label="最近一次演唱" min-width="140" align="center" header-align="center" />
      <el-table-column prop="perform_count" label="演唱次数" min-width="100" align="center" header-align="center" />

      <!-- 展开列 -->
      <el-table-column type="expand" label="演唱记录" width="120">
        <template #default="props">
          <div style="padding: 10px 30px">
            <div v-if="records[props.row.id] && records[props.row.id].length > 0">
              <div class="record-card-list">
                <div
                  v-for="(record, index) in records[props.row.id]"
                  :key="index"
                  class="record-card"
                >
                  <div class="record-time">
                    <a :href="record.url" target="_blank">▶ {{ record.performed_at }}</a>
                  </div>
                  <div class="record-notes">{{ record.notes || '' }}</div>
                </div>
              </div>
            </div>
            <div v-else style="padding: 10px; color: #999; text-align: center;">
              暂无演唱记录
            </div>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页歌曲列表 -->
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

.record-card-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.record-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px 16px;
  width: calc(33.333% - 12px); /* 每行最多 3 个，自动换行 */
  box-shadow: 1px 1px 4px rgba(0,0,0,0.05);
  background-color: #fafafa;
  transition: box-shadow 0.3s;
}

.record-card:hover {
  box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
}

.record-time a {
  font-weight: bold;
  color: #409EFF;
  text-decoration: none;
}

.record-time a:hover {
  text-decoration: underline;
}

.record-notes {
  margin-top: 6px;
  font-size: 13px;
  color: #333;
  white-space: pre-line;
}
</style>
