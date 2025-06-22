<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const query = ref('')
const songs = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 50

const fetchSongs = async () => {
  try {
    const res = await axios.get('/api/songs', {
      params: {
        q: query.value,
        page: page.value,
        limit: pageSize
      }
    })
    songs.value = res.data.results
    total.value = res.data.total
  } catch (err) {
    ElMessage.error('搜索失败')
    console.error(err)
  }
}

// 初始加载
fetchSongs()
</script>

<template>
  <div style="padding: 20px">
    <el-input
      v-model="query"
      placeholder="请输入歌曲名"
      style="width: 300px; margin-right: 10px"
      @keyup.enter="() => { page = 1; fetchSongs() }"
    />
    <el-button type="primary" @click="() => { page = 1; fetchSongs() }">搜索</el-button>

    <el-table :data="songs" style="margin-top: 20px; width: 100%">
      <el-table-column prop="song_name" label="歌名" />
      <el-table-column prop="singer" label="歌手" />
      <el-table-column prop="last_performed" label="最近演唱" />
      <el-table-column prop="perform_count" label="演唱次数" />
      <el-table-column prop="styles" label="曲风">
        <template #default="{ row }">
          <el-tag
            v-for="(style, idx) in row.styles"
            :key="idx"
            style="margin-right: 4px"
            type="info"
          >{{ style }}</el-tag>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-if="total > pageSize"
      style="margin-top: 20px"
      background
      layout="prev, pager, next"
      :total="total"
      :page-size="pageSize"
      :current-page="page"
      @current-change="(val) => { page = val; fetchSongs() }"
    />
  </div>
</template>
