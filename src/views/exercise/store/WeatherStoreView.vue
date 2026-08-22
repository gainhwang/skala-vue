<script setup>
import UnitToggler from '@/components/exercise/UnitToggler.vue'
import WeatherParent from '@/components/exercise/WeatherParent.vue'
import PreparationChecklist from '@/components/exercise/preparationChecklist.vue'
import CheerBattle from '@/components/exercise/CheerBattle.vue'
</script>

<template>
  <section>
    <div class="store-header">
      <h2>⚾ 야구장 날씨 Store</h2>
      <UnitToggler />
    </div>

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
.store-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}
</style>
