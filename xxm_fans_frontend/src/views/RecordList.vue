<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  songId: {
    type: Number,
    required: true,
  },
})

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
  <div style="padding: 10px 30px">
    <div v-if="loading" style="text-align: center; color: #666;">加载中...</div>
    <div v-else-if="records && records.length > 0">
      <div class="record-card-list">
        <div
          v-for="(record, index) in records"
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

<style scoped>
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
