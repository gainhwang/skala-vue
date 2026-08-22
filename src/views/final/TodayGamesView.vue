<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useGameStore } from '@/stores/gameStore'
import { findStadium } from '@/data/stadiums'
import {
  fetchCurrentWeather,
  getRequestErrorMessage,
} from '@/services/weatherApi'

const gameStore = useGameStore()

const weatherByGame = ref({})
const isLoading = ref(false)
const errorMessage = ref('')

const todayText = new Intl.DateTimeFormat('ko-KR', {
  month: 'long',
  day: 'numeric',
  weekday: 'long',
}).format(new Date())

const getTagType = (weatherMain) => {
  if (weatherMain === 'Clear') return 'success'
  if (['Rain', 'Drizzle', 'Thunderstorm'].includes(weatherMain)) return 'danger'
  if (weatherMain === 'Clouds') return 'info'

  return 'warning'
}

const loadTodayWeather = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const entries = await Promise.all(
      gameStore.games.map(async (game) => {
        const stadium = findStadium(game.stadiumId)
        const weather = await fetchCurrentWeather(stadium)

        return [game.id, weather]
      }),
    )

    weatherByGame.value = Object.fromEntries(entries)
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(
      error,
      '오늘 경기 날씨를 불러오지 못했습니다.',
    )
  } finally {
    isLoading.value = false
  }
}

onMounted(loadTodayWeather)
</script>

<template>
  <section class="today-page">
    <div class="page-heading">
      <div>
        <h2>오늘의 경기</h2>
        <p>{{ todayText }} · 경기를 선택하면 자세한 관람 정보를 볼 수 있습니다.</p>
      </div>

      <el-button :loading="isLoading" @click="loadTodayWeather">
        날씨 새로고침
      </el-button>
    </div>

    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      :closable="false"
      show-icon
    />

    <el-row :gutter="16" class="game-grid">
      <el-col
        v-for="game in gameStore.games"
        :key="game.id"
        :xs="24"
        :md="12"
        class="game-column"
      >
        <RouterLink
          class="game-link"
          :to="{ name: 'final-game-detail', params: { gameId: game.id } }"
        >
          <el-card class="game-card" shadow="hover">
            <div class="game-meta">
              <span>{{ game.stadiumName }}</span>
              <strong>{{ game.startTime }}</strong>
            </div>

            <div class="matchup">
              <div
                class="team-panel"
                :style="{ borderTopColor: game.homeTeam.color }"
              >
                <small>홈</small>
                <strong class="team-name">
                  <span
                    class="team-color-dot"
                    :style="{ backgroundColor: game.homeTeam.color }"
                  />
                  {{ game.homeTeam.name }}
                </strong>
              </div>

              <span>VS</span>

              <div
                class="team-panel"
                :style="{ borderTopColor: game.awayTeam.color }"
              >
                <small>원정</small>
                <strong class="team-name">
                  <span
                    class="team-color-dot"
                    :style="{ backgroundColor: game.awayTeam.color }"
                  />
                  {{ game.awayTeam.name }}
                </strong>
              </div>
            </div>

            <el-skeleton v-if="isLoading" :rows="1" animated />

            <div v-else-if="weatherByGame[game.id]" class="weather-summary">
              <el-tag
                :type="getTagType(weatherByGame[game.id].weather[0].main)"
                effect="plain"
              >
                {{ weatherByGame[game.id].weather[0].description }}
              </el-tag>
              <span>현재 {{ weatherByGame[game.id].main.temp.toFixed(1) }}℃</span>
              <span>습도 {{ weatherByGame[game.id].main.humidity }}%</span>
            </div>

            <p v-else class="weather-empty">날씨 정보를 확인해 주세요.</p>

            <div class="detail-text">경기 상세 보기 →</div>
          </el-card>
        </RouterLink>
      </el-col>
    </el-row>
  </section>
</template>

<style scoped>
.today-page {
  padding: 1.5rem;
  border: 1px solid #dfe5ec;
  border-radius: 10px;
  background: #fff;
}

.page-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.page-heading h2 {
  margin: 0;
}

.page-heading p {
  margin: 0.4rem 0 0;
  color: #6b7785;
}

.game-grid {
  margin-top: 0.25rem;
}

.game-column {
  margin-top: 1rem;
}

.game-link {
  display: block;
  height: 100%;
  padding: 0;
  color: inherit;
}

.game-link:hover {
  background: transparent;
}

.game-card {
  height: 100%;
}

.game-meta,
.weather-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.game-meta {
  padding-bottom: 0.75rem;
  color: #6b7785;
  border-bottom: 1px solid #ebeef5;
}

.matchup {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 1rem;
  align-items: center;
  padding: 1.25rem 0;
  text-align: center;
}

.team-panel {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0.75rem 0.5rem;
  border: 1px solid #ebeef5;
  border-top: 4px solid #8492a6;
  border-radius: 6px;
  background: #fafafa;
}

.team-name {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
}

.team-color-dot {
  width: 0.7rem;
  height: 0.7rem;
  flex: 0 0 auto;
  border-radius: 50%;
}

.matchup small,
.weather-empty {
  color: #8492a6;
}

.weather-summary {
  justify-content: flex-start;
  padding: 0.75rem;
  font-size: 0.9rem;
  border-radius: 6px;
  background: #f5f7fa;
}

.weather-empty {
  padding: 0.75rem;
  margin: 0;
  text-align: center;
  background: #f5f7fa;
}

.detail-text {
  margin-top: 1rem;
  color: #409eff;
  font-size: 0.9rem;
  text-align: right;
}

@media (max-width: 640px) {
  .today-page {
    padding: 1rem;
  }

  .page-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .weather-summary {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
