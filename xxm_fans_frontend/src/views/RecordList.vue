<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import VideoPlayerDialog from '../components/VideoPlayerDialog.vue'

const props = defineProps({
  songId: {
    type: Number,
    required: true,
  },
  songName: {
    type: String,
    required: true
  }
})

// 弹窗状态
const showPlayer = ref(false)
const currentUrl = ref('')

// 播放弹窗
const openPlayer = (url) => {
  if (!url) {
    ElMessage.warning('暂无视频链接')
    return
  }
  currentUrl.value = url
  showPlayer.value = true
}

// 缓存机制
const recordCache = new Map()
const records = ref(null)
const loading = ref(false)

const fetchRecords = async () => {
  if (recordCache.has(props.songId)) {
    records.value = recordCache.get(props.songId)
    return
  }

  loading.value = true
  try {
    const res = await axios.get(`/api/songs/${props.songId}/records`)
    records.value = res.data.results || res.data
    recordCache.set(props.songId, records.value)
  } catch (err) {
    console.error(`❌ 获取演唱记录失败（id=${props.songId}）:`, err)
    records.value = []
  } finally {
    loading.value = false
  }
}
const getFullCoverUrl = (relativePath) => {
    const performedAt = record?.performed_at
    if (!performedAt) return '/cover/default.jpg'
    return `/cover/${performedAt}.jpg`
//   return 'http://192.168.0.102:8000' + relativePath
}

onMounted(fetchRecords)
</script>

<template>
  <div style="padding: 10px 30px">
    <div v-if="loading" style="text-align: center; color: #666;">加载中...</div>
    <div v-else-if="records && records.length > 0">
      <div class="record-card-list">
        <div
          v-for="(record, index) in records"
          :key="index"
          class="record-card"
        >
          <!-- ✅ 封面图 -->
            <img
            v-if="record.cover_url"
            :src="record.cover_url"
            alt="cover"
            class="record-cover"
            @error="e => (e.target.src = '/covers/default.jpg')"
            />
          <!-- <img
            v-if="record.cover_url"
            :src="getFullCoverUrl(record.cover_url)"
            alt="cover"
            class="record-cover"
            @error="e => (e.target.style.display = 'none')"
          /> -->

          <div class="record-time clickable" @click="openPlayer(record.url)">
            ▶ {{ record.performed_at }}
          </div>
          <div class="record-notes">{{ record.notes || '' }}</div>
        </div>
      </div>
    </div>
    <div v-else style="padding: 10px; color: #999; text-align: center;">
      暂无演唱记录
    </div>
  </div>

  <VideoPlayerDialog
    v-model:visible="showPlayer"
    :url="currentUrl"
    :songName="props.songName"
  />
</template>

<style scoped>
.video-wrapper {
  position: relative;
  width: 100%;
  padding-top: 56.25%;
  background-color: black;
}

.video-wrapper iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
}

.clickable {
  cursor: pointer;
  color: #409EFF;
  font-weight: bold;
}
.clickable:hover {
  text-decoration: underline;
}

.record-card-list {
  display: flex;
  flex-wrap: wrap;
  gap: 13px;
}

.record-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px 16px;
  width: calc(25% - 12px);
  box-shadow: 1px 1px 4px rgba(0, 0, 0, 0.05);
  background-color: #fafafa;
  transition: box-shadow 0.3s;
}

.record-card:hover {
  box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
}

.record-notes {
  margin-top: 6px;
  font-size: 13px;
  color: #333;
  white-space: pre-line;
}

.record-cover {
  width: 100%;
  height: 140px;
  object-fit: cover;
  border-radius: 6px;
  margin-bottom: 8px;
}
</style>

<style>
.el-overlay-dialog {
  z-index: 3000 !important;
}

.el-dialog__body {
  padding: 0 !important;
  background-color: #fff !important;
  max-height: 80vh;
  overflow-y: auto;
}

.song-list-container {
  z-index: auto !important;
  position: relative;
}
</style>
