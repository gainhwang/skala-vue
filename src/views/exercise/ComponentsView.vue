<script setup>
import WeatherParent from '@/components/exercise/WeatherParent.vue'
</script>

<template>
  <section aria-labelledby="components-title">
    <h2 id="components-title" class="sr-only">Weather Components</h2>
    <WeatherParent />
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
