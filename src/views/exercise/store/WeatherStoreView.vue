<script setup>
import WeatherParent from '@/components/exercise/WeatherParent.vue'
import PreparationChecklist from '@/components/exercise/preparationChecklist.vue'
import CheerBattle from '@/components/exercise/CheerBattle.vue'
</script>

<template>
  <section>
    <h2 class="store-title">⚾ 야구장 날씨 Store</h2>

    <CheerBattle />

    <WeatherParent
      details-as-route
      detail-route-name="exercise-store-detail"
      :show-cheer-up="false"
    />

    <PreparationChecklist />
  </section>
</template>

<style scoped>
.store-title {
  margin-bottom: 1rem;
  text-align: center;
}
</style>
