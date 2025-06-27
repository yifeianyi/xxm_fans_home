<template>
  <div class="calendar-table">
    <div class="calendar-header">{{ year }}年{{ month + 1 }}月</div>
    <table>
      <thead>
        <tr>
          <th>日</th><th>一</th><th>二</th><th>三</th><th>四</th><th>五</th><th>六</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(week, i) in weeks" :key="i">
          <td v-for="(d, j) in week" :key="j">
            <span v-if="d" :class="{ today: d === todayDate }">{{ d }}</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const todayObj = new Date()
const year = todayObj.getFullYear()
const month = todayObj.getMonth()
const todayDate = todayObj.getDate()

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

<style scoped>
.calendar-table {
  margin: 30px auto 0 auto;
  max-width: 100%;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  padding: 18px 12px 12px 12px;
  width: 100%;
}
.calendar-header {
  text-align: center;
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 10px;
}
.calendar-table table {
  width: 100%;
  max-width: 100%;
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
</style> 