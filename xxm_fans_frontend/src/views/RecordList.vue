<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const props = defineProps({
  songId: {
    type: Number,
    required: true,
  },
})

// ✅ 弹窗状态
const showDialog = ref(false)
const currentUrl = ref('')

// ✅ 播放弹窗
const openPlayer = (url) => {
  if (!url) {
    ElMessage.warning('暂无视频链接')
    return
  }
  currentUrl.value = url
  showDialog.value = true
}

// ✅ 缓存机制：静态全局变量
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
    records.value = res.data
    recordCache.set(props.songId, res.data)
  } catch (err) {
    console.error(`❌ 获取演唱记录失败（id=${props.songId}）:`, err)
    records.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchRecords)
</script>

<template>
  <!-- ✅ 视频弹窗 -->
  <el-dialog
    v-model="showDialog"
    title="播放视频"
    width="80%"
    destroy-on-close
    :before-close="() => (showDialog = false)"
    class="video-dialog"
  >
    <div class="video-wrapper">
      <iframe
        v-if="currentUrl"
        :src="currentUrl"
        frameborder="0"
        allowfullscreen
      ></iframe>
    </div>
  </el-dialog>


  <div style="padding: 10px 30px">
    <div v-if="loading" style="text-align: center; color: #666;">加载中...</div>
    <div v-else-if="records && records.length > 0">
      <div class="record-card-list">
        <div
          v-for="(record, index) in records"
          :key="index"
          class="record-card"
        >
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


</template>

<style scoped>
/* dialog 提高优先级 */
.video-dialog {
  max-width: 960px;
  z-index: 99999 !important;
}

.video-wrapper {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 比例 */
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
  gap: 12px;
}

.record-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px 16px;
  width: calc(33.333% - 12px);
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
</style>

<style>
/* ✅ 全局覆盖 el-dialog 的遮罩层和主体 z-index */
.el-overlay {
  z-index: 9999 !important;
}
.el-overlay .el-dialog {
  z-index: 10000 !important;
}

/* ✅ 去除 el-dialog 默认的白色背景和 padding */
.el-dialog__body {
  padding: 0 !important;
  background-color: transparent !important;
}
</style>

