<script setup>
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import UnitToggler from '@/components/exercise/UnitToggler.vue'

const route = useRoute()

const showUnitToggler = computed(() => {
  return ['exercise-store', 'exercise-store-detail'].includes(route.name)
})
</script>

<template>
  <main class="exercise-layout">
    <header class="exercise-header">
      <h1>날씨 과제 모음</h1>

      <div class="exercise-navigation">
        <nav class="exercise-tabs" aria-label="날씨 과제 단계">
          <RouterLink :to="{ name: 'exercise-mockup' }">1. Mockup</RouterLink>
          <RouterLink :to="{ name: 'exercise-composition' }">2. Composition</RouterLink>
          <RouterLink :to="{ name: 'exercise-components' }">3. Components</RouterLink>
          <RouterLink :to="{ name: 'exercise-router-home' }">4. Router</RouterLink>
          <RouterLink :to="{ name: 'exercise-store' }">5. Store</RouterLink>
          <RouterLink :to="{ name: 'exercise-axios' }">6. Axios</RouterLink>
        </nav>

        <UnitToggler v-if="showUnitToggler" />
      </div>

      <RouterLink class="final-link" to="/">← 최종본으로 돌아가기</RouterLink>
    </header>

    <div class="exercise-content">
      <RouterView />
    </div>
  </main>
</template>

<style scoped>
.exercise-layout {
  width: min(100%, 768px);
  margin: 0 auto;
  padding: 2rem;
}

.exercise-header {
  margin-bottom: 1.5rem;
  text-align: center;
}

.exercise-header h1 {
  margin-bottom: 1rem;
}

.exercise-tabs {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.5rem;
}

.exercise-navigation {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.exercise-tabs a {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d7dee8;
  border-radius: 8px;
}

.exercise-tabs a.router-link-active {
  color: #fff;
  background: #42b883;
  border-color: #42b883;
}

.final-link {
  display: inline-block;
  padding: 0.5rem 0.85rem;
  margin-top: 1rem;
  color: #fff;
  border-radius: 8px;
  background: #34495e;
}

.final-link:hover {
  background: #263849;
}

.exercise-content {
  padding: 1.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fbf5c6;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

@media (max-width: 640px) {
  .exercise-layout {
    padding: 1rem;
  }

  .exercise-content {
    padding: 1rem;
  }

  .exercise-navigation {
    flex-direction: column;
  }
}
</style>
