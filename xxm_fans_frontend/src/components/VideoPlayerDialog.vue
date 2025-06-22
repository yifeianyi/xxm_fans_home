<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  songName: String,
  url: String,
  visible: Boolean,
})

const emit = defineEmits(['update:visible'])

const showDialog = ref(props.visible)

watch(
  () => props.visible,
  (val) => {
    showDialog.value = val
  }
)

const handleClose = () => {
  emit('update:visible', false)
}
</script>

<template>
  <el-dialog
    v-model="showDialog"
    :title="songName"
    width="60%"
    destroy-on-close
    :before-close="handleClose"
    append-to-body
    :lock-scroll="true"
  >
    <div class="video-wrapper">
      <iframe
        v-if="url"
        :src="url"
        frameborder="0"
        allowfullscreen
      ></iframe>
    </div>
  </el-dialog>
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
</style>
