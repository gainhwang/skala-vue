<script setup>
import { computed } from 'vue'
import { useGameStore } from '@/stores/gameStore'

const gameStore = useGameStore()

const game = computed(() => {
  return gameStore.favoriteGame
})
</script>

<template>
  <section class="cheer-battle">
    <h3>❤️‍🔥 응원 대결</h3>

    <label class="team-selector">
      내 응원 구단

      <select
        :value="gameStore.favoriteTeam"
        @change="gameStore.setFavoriteTeam($event.target.value)"
      >
        <option v-for="team in gameStore.teamOptions" :key="team.id" :value="team.id">
          {{ team.name }}
        </option>
      </select>
    </label>

    <div v-if="game">
      <p class="game-info">{{ game.stadiumName }} · {{ game.startTime }}</p>

      <div class="battle-board">
        <article class="team-card" :style="{ backgroundColor: game.homeTeam.color }">
          <strong>{{ game.homeTeam.name }}</strong>

          <span class="count">
            {{ game.cheers.home }}
          </span>

          <button @click="gameStore.cheer(game.id, 'home')">
            {{ game.homeTeam.name }} 응원하기
          </button>
        </article>

        <span class="vs">VS</span>

        <article class="team-card" :style="{ backgroundColor: game.awayTeam.color }">
          <strong>{{ game.awayTeam.name }}</strong>

          <span class="count">
            {{ game.cheers.away }}
          </span>

          <button @click="gameStore.cheer(game.id, 'away')">
            {{ game.awayTeam.name }} 응원하기
          </button>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.cheer-battle {
  max-width: 600px;
  padding: 1rem;
  margin: 1.5rem auto;
  text-align: center;
  border-radius: 12px;
  background: #fff;
}

.team-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.team-selector select {
  padding: 0.5rem;
}

.game-info {
  color: #52606d;
}

.battle-board {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  align-items: stretch;
}

.team-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  justify-content: center;
  min-height: 170px;
  padding: 1rem;
  color: white;
  border-radius: 14px;
}

.count {
  font-size: 2rem;
  font-weight: 700;
}

.team-card button {
  padding: 0.5rem;
  cursor: pointer;
  border: 0;
  border-radius: 8px;
}

.vs {
  position: absolute;
  top: 50%;
  left: 50%;
  z-index: 1;
  padding: 0.75rem;
  font-weight: 700;
  color: #555;
  border-radius: 50%;
  background: white;
  transform: translate(-50%, -50%);
}

@media (max-width: 500px) {
  .battle-board {
    grid-template-columns: 1fr;
  }

  .vs {
    position: static;
    transform: none;
  }
}
</style>
