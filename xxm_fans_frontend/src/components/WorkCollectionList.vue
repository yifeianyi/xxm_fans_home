<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const collections = ref([])
const showDialog = ref(false)
const dialogWork = ref(null)

const fetchData = async () => {
  // 获取所有合集
  const res = await axios.get('/api/footprint/collections/')
  const list = res.data.results || []
  // 并发获取每个合集的作品
  const worksList = await Promise.all(
    list.map(async col => {
      const res2 = await axios.get('/api/footprint/works/', { params: { collection: col.id, limit: 12 } })
      return { ...col, works: res2.data.results || [] }
    })
  )
  collections.value = worksList
}

function openDialog(work) {
  dialogWork.value = work
  showDialog.value = true
}

function closeDialog() {
  showDialog.value = false
}

onMounted(fetchData)
</script>

<template>
  <div class="work-collection-list">
    <div
      v-for="col in collections"
      :key="col.id"
      class="collection-block"
    >
      <div class="collection-header">
        <span class="collection-title"> {{ col.name }}</span>
        <span class="collection-count">· {{ col.works_count }}</span>
      </div>
      <div class="work-list-scroll">
        <div
          v-for="work in col.works"
          :key="work.id"
          class="work-card"
          @click="openDialog(work)"
        >
          <img :src="work.cover_url" class="work-cover" :alt="work.title" />
          <div class="work-info">
            <div class="work-title" :title="work.title">{{ work.title }}</div>
            <div class="work-author">UP主：{{ work.author }}</div>
            <div class="work-notes" v-if="work.notes">{{ work.notes }}</div>
          </div>
        </div>
      </div>
    </div>
    <!-- 弹窗 -->
    <div v-if="showDialog" class="work-dialog-mask" @click.self="closeDialog">
      <div class="work-dialog">
        <div class="dialog-header">
          <span>{{ dialogWork?.title }}</span>
          <button class="close-btn" @click="closeDialog">×</button>
        </div>
        <div class="dialog-body">
          <iframe
            v-if="dialogWork?.view_url"
            :src="dialogWork.view_url"
            frameborder="0"
            allowfullscreen
            class="bili-iframe"
          ></iframe>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.work-collection-list {
  width: 100%;
}
.collection-block {
  margin-bottom: 36px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}
.collection-header {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
  gap: 10px;
}
.collection-title {
  color: #222;
}
.collection-count {
  color: #888;
  font-size: 15px;
  font-weight: normal;
}
.collection-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}
.work-list-scroll {
  display: flex;
  overflow-x: auto;
  gap: 18px;
  padding-bottom: 6px;
}
.work-card {
  width: 220px;
  min-width: 220px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  padding: 10px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  transition: box-shadow 0.2s;
  position: relative;
  cursor: pointer;
}
.work-card:hover {
  box-shadow: 0 4px 16px rgba(253,165,193,0.18);
}
.cover-link {
  display: block;
  width: 100%;
  position: relative;
}
.work-cover {
  width: 100%;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 8px;
  background: #f5f5f5;
}
.work-info {
  width: 100%;
}
.work-title {
  font-size: 15px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.work-author {
  font-size: 13px;
  color: #888;
  margin-bottom: 2px;
}
.work-notes {
  font-size: 13px;
  color: #666;
  margin-top: 2px;
  white-space: pre-line;
}
.work-dialog-mask {
  position: fixed;
  left: 0; top: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.25);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.work-dialog {
  background: #fff;
  border-radius: 12px;
  padding: 18px 24px 18px 24px;
  min-width: 340px;
  max-width: 90vw;
  max-height: 90vh;
  box-shadow: 0 4px 24px rgba(0,0,0,0.18);
  position: relative;
}
.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
}
.close-btn {
  background: none;
  border: none;
  font-size: 22px;
  cursor: pointer;
  color: #888;
}
.dialog-body {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.bili-iframe {
  width: 480px;
  height: 300px;
  border-radius: 8px;
  margin-bottom: 12px;
  background: #000;
}
.dialog-info {
  text-align: left;
  font-size: 15px;
  color: #444;
}
@media (max-width: 600px) {
  .bili-iframe {
    width: 90vw;
    height: 200px;
  }
  .work-card {
    width: 90vw;
    min-width: 0;
  }
}
</style> 