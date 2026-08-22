<script setup>
import WeatherMockup from '@/components/exercise/WeatherMockup.vue'
</script>

<template>
  <section aria-labelledby="mockup-title">
    <h2 id="mockup-title" class="sr-only">Weather Mockup</h2>
    <WeatherMockup />
  </section>
</template>

<style scoped>
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
