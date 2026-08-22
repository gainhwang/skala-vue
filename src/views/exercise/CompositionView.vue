<script setup>
import WeatherComposition from '@/components/exercise/WeatherComposition.vue'
</script>

<template>
  <section aria-labelledby="composition-title">
    <h2 id="composition-title" class="sr-only">Weather Composition</h2>
    <WeatherComposition />
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
