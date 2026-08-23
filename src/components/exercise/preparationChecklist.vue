<script setup>
import { computed, watch } from 'vue'
import { useGameStore } from '@/stores/gameStore'
import { usePreparationStore } from '@/stores/preparationStore'

const gameStore = useGameStore()
const preparationStore = usePreparationStore()

const selectedGame = computed(() => {
  return gameStore.favoriteGame
})

watch(
  () => selectedGame.value?.id,

  () => {
    const weather = selectedGame.value?.weather

    if (weather) {
      preparationStore.setRecommendations(weather)
    }
  },

  {
    immediate: true,
  },
)
</script>

<template>
  <section class="checklist">
    <h3>⚾ 야구장 관람 준비물</h3>

    <p v-if="selectedGame" class="recommendation-info">
      {{ selectedGame.stadiumName }}의 {{ selectedGame.weather.status }} 날씨 기준 추천
    </p>

    <p>
      준비 완료:
      {{ preparationStore.completedCount }} /
      {{ preparationStore.items.length }}
    </p>

    <ul>
      <li v-for="item in preparationStore.items" :key="item.id">
        <label>
          <input
            type="checkbox"
            :checked="item.checked"
            @change="preparationStore.toggleItem(item.id)"
          />

          <span :class="{ completed: item.checked }">
            {{ item.name }}
          </span>
        </label>
      </li>
    </ul>

    <p>
      남은 준비물:
      {{ preparationStore.remainingCount }}개
    </p>

    <button :disabled="preparationStore.completedCount === 0" @click="preparationStore.resetItems">
      체크 초기화
    </button>
  </section>
</template>

<style scoped>
.checklist {
  max-width: 600px;
  padding: 1rem;
  margin: 1.5rem auto 0;
  border: 1px solid #c8d9e8;
  border-radius: 10px;
  background: #eef6ff;
}

.checklist ul {
  padding: 0;
  list-style: none;
}

.checklist li {
  margin: 0.75rem 0;
}

.checklist label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.completed {
  color: #8a949f;
  text-decoration: line-through;
}

.checklist button {
  padding: 0.5rem 0.75rem;
  cursor: pointer;
}

.checklist button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
</style>
