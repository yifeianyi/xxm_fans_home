<template>
  <div class="timeline">
    <div class="timeline-item">
      <div class="timeline-dot"></div>
      <div class="timeline-content">
        <div class="timeline-date">2024-06-01</div>
        <div class="timeline-title">发布《满满来信》</div>
      </div>
    </div>
    <div class="timeline-item">
      <div class="timeline-dot"></div>
      <div class="timeline-content">
        <div class="timeline-date">2024-05-20</div>
        <div class="timeline-title">首场个人演唱会</div>
      </div>
    </div>
    <div class="timeline-item">
      <div class="timeline-dot"></div>
      <div class="timeline-content">
        <div class="timeline-date">2024-04-10</div>
        <div class="timeline-title">单曲《春日物语》上线</div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 静态内容，无需逻辑
</script>

<style scoped>
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