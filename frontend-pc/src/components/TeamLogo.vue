<template>
  <div class="team-logo" :style="{ width: size, height: size }">
    <img
      v-if="logoUrl && !imgError"
      :src="logoUrl"
      :alt="teamName"
      class="logo-img"
      @error="imgError = true"
    />
    <div v-else class="logo-default">
      <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="20" cy="20" r="19" stroke="#c0c4cc" stroke-width="2" fill="#f5f7fa"/>
        <circle cx="20" cy="14" r="5" fill="#c0c4cc"/>
        <path d="M10 34c0-5.523 4.477-10 10-10s10 4.477 10 10" fill="#c0c4cc"/>
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  logoUrl?: string
  size?: string
  teamName?: string
}>()

const imgError = ref(false)
</script>

<style scoped>
.team-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.logo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.logo-default {
  width: 100%;
  height: 100%;
}

.logo-default svg {
  width: 100%;
  height: 100%;
}
</style>
