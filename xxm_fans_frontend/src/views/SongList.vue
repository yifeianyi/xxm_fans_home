<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import RecordList from './RecordList.vue'

const songs = ref([])
const total = ref(0)
const curPage = ref(1)
const pageSize = 50
const query = ref('')
// 获取分页歌曲数据
const fetchSongs = async () => {
  try {
    const res = await axios.get('/api/songs', {
      params: {
        q: query.value,
        page: curPage.value,
        limit: pageSize,
        styles: selectedStyles.value.join(','),  // ✅ 添加这行
      }
    })
    songs.value = res.data.results
    total.value = res.data.total
  } catch (err) {
    console.error('❌ 获取歌曲失败:', err)
  }
}
// ✅ 选中的曲风（多选）
const selectedStyles = ref([])

// ✅ 可供选择的曲风列表
const styleOptions = ref([])
const loadStyleOptions = async () => {
  try {
    const res = await axios.get('/api/styles')
    styleOptions.value = res.data
  } catch (err) {
    console.error('❌ 获取曲风列表失败:', err)
  }
}


onMounted( ()=>{
  loadStyleOptions()
  fetchSongs()
})
watch(curPage, fetchSongs)



</script>



<template>
  <div class="song-list-container">
  <!-- ✅ 筛选区域 -->
    <div class="filter-bar">
  <div class="filter-box">
    <el-button
      type="primary"
      @click="() => { curPage = 1; fetchSongs() }"
      style="margin-bottom: 10px"
    >
      🔍 筛选
    </el-button>
    <el-checkbox-group v-model="selectedStyles">
      <el-checkbox
        v-for="style in styleOptions"
        :key="style"
        :label="style"
      >
        {{ style }}
      </el-checkbox>
    </el-checkbox-group>
  </div>
</div>


    <!-- 搜索框 -->
    <div class="search-bar">
        <el-input
            v-model="query"
            placeholder="请输入歌曲名"
            style="width: 300px; margin-right: 10px"
            @keyup.enter="() => { page = 1; fetchSongs() }"
            />
        <el-button type="primary" @click="() => { page = 1; fetchSongs() }">搜索</el-button>

    </div>
    
    <el-table
      :data="songs"
      stripe
      border
      fit
      style="width: 100%" 
    >
        <el-table-column prop="id" label="No" min-width="80" align="center" header-align="center" />
        <el-table-column prop="song_name" label="歌曲名" min-width="130" align="center" header-align="center" />
        <el-table-column prop="singer" label="歌手" min-width="100" align="center" header-align="center" />
        <el-table-column label="曲风" width="120" min-width="80" align="center" header-align="center">
            <template #default="{ row }">
                <span v-if="row.styles && row.styles.length > 0">
                {{ row.styles.join('、') }}
                </span>
                <span v-else>暂无</span>
            </template>
        </el-table-column>
        <el-table-column prop="last_performed" label="最近一次演唱" min-width="140" align="center" header-align="center" />
        <el-table-column prop="perform_count" label="演唱次数" min-width="100" align="center" header-align="center" />

      <!-- 展开列 -->
      <el-table-column type="expand" label="演唱记录" width="120">
        <template #default="props">
            <RecordList 
                :song-id="props.row.id" 
                :song-name="props.row.song_name"
            />
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
.search-bar {
  margin-bottom: 20px;
  text-align: center;
}
.song-list-container {
  position: relative;
  z-index: 1;
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
  text-align: center;
  background-color: transparent; /* 防止遮住弹窗 */
}

.video-dialog {
  max-width: 960px;
  z-index: 99999 !important;
}

.filter-bar {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.filter-box {
  border: 2px dashed black;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  border-radius: 8px;
  background-color: #ffffffbb; /* 半透明白背景，可选 */
}

/* 控制复选框一行显示多个 */
.el-checkbox-group {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}


</style>
