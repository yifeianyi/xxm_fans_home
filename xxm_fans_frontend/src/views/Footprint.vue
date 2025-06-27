<script setup>
import { ref } from 'vue'
import MonthCalendar from '../components/MonthCalendar.vue'
import WorkTimeline from '../components/WorkTimeline.vue'
const activeTab = ref('calendar')

// 日历组件
import { computed } from 'vue'
const today = new Date()
const year = today.getFullYear()
const month = today.getMonth()
const date = today.getDate()

function getMonthDays(year, month) {
  return new Date(year, month + 1, 0).getDate()
}
function getFirstDayOfWeek(year, month) {
  return new Date(year, month, 1).getDay()
}
const days = computed(() => {
  const daysInMonth = getMonthDays(year, month)
  const firstDay = getFirstDayOfWeek(year, month)
  const arr = []
  for (let i = 0; i < firstDay; i++) arr.push(null)
  for (let d = 1; d <= daysInMonth; d++) arr.push(d)
  while (arr.length % 7 !== 0) arr.push(null)
  return arr
})
const weeks = computed(() => {
  const arr = []
  for (let i = 0; i < days.value.length; i += 7) {
    arr.push(days.value.slice(i, i + 7))
  }
  return arr
})
</script>


<template>
  <div class="footprint-page">
    <div class="custom-tabs">
      <div
        class="tab-btn"
        :class="{ active: activeTab === 'calendar' }"
        @click="activeTab = 'calendar'"
      >满国日历</div>
      <div
        class="tab-btn"
        :class="{ active: activeTab === 'timeline' }"
        @click="activeTab = 'timeline'"
      >作品时间线</div>
      <div
        class="tab-btn"
        :class="{ active: activeTab === 'creative' }"
        @click="activeTab = 'creative'"
      >精选二创</div>
    </div>
    <div class="card-content-bg">
      <div class="tab-content">
        <div v-if="activeTab === 'calendar'">
          <!-- 满国日历内容区域 -->
          <MonthCalendar />
        </div>
        <div v-else-if="activeTab === 'timeline'">
          <!-- 作品时间线内容区域 -->
          <WorkTimeline />
        </div>
        <div v-else-if="activeTab === 'creative'">
          <!-- 精选二创内容区域 -->
        </div>
      </div>
    </div>
  </div>
</template>



<style scoped>
.footprint-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 20px 40px 20px;
  min-height: 400px;
  text-align: center;
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
  width: 66vw;
  max-width: 1200px;
  min-width: 350px;
  margin: 0 auto;
}
.tab-content {
  padding: 32px 0 32px 0;
  min-height: 300px;
  background-color: rgb(250, 250, 250,0.6);
}
.calendar-table {
  margin: 30px auto 0 auto;
  max-width: 420px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  padding: 18px 12px 12px 12px;
}
.calendar-header {
  text-align: center;
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 10px;
}
.calendar-table table {
  width: 100%;
  border-collapse: collapse;
}
.calendar-table th, .calendar-table td {
  width: 14.2%;
  height: 36px;
  text-align: center;
  font-size: 16px;
  border-radius: 6px;
}
.calendar-table td {
  background: none;
}
.calendar-table .today {
  display: inline-block;
  background: #6fdc8c;
  color: #fff;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  line-height: 28px;
  font-weight: bold;
}
.timeline {
  margin: 40px auto 0 auto;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  gap: 32px;
  align-items: flex-start;
  position: relative;
}
.timeline-item {
  display: flex;
  align-items: flex-start;
  position: relative;
}
.timeline-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 8px;
  top: 20px;
  width: 4px;
  height: calc(100% + 12px);
  background: #222;
  border-radius: 2px;
  z-index: 0;
}
.timeline-dot {
  width: 16px;
  height: 16px;
  background: #fda5c1;
  border-radius: 50%;
  margin-right: 18px;
  margin-top: 4px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(253,165,193,0.15);
  z-index: 1;
}
.timeline-content {
  background: rgba(255,255,255,0.8);
  border-radius: 10px;
  padding: 10px 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  min-width: 180px;
}
.timeline-date {
  font-size: 14px;
  color: #888;
  margin-bottom: 4px;
}
.timeline-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}
</style> 