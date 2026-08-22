<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import KakaoStadiumMap from '@/components/exercise/KakaoStadiumMap.vue'
import { findStadium } from '@/data/stadiums'
import { useGameStore } from '@/stores/gameStore'
import { usePreparationStore } from '@/stores/preparationStore'
import {
  fetchAirQuality,
  fetchCurrentWeather,
  fetchThreeHourForecast,
  getRequestErrorMessage,
  getWeatherStatus,
} from '@/services/weatherApi'

const props = defineProps({
  gameId: {
    type: String,
    required: true,
  },
})

const gameStore = useGameStore()
const preparationStore = usePreparationStore()

const currentWeather = ref(null)
const forecast = ref(null)
const airQuality = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')
const customItemName = ref('')
const customItemError = ref('')

const game = computed(() => {
  return gameStore.games.find((item) => item.id === props.gameId)
})

const stadium = computed(() => {
  return game.value ? findStadium(game.value.stadiumId) : null
})

const preparationProgress = computed(() => {
  if (preparationStore.items.length === 0) return 0

  return Math.round(
    (preparationStore.completedCount / preparationStore.items.length) * 100,
  )
})

const airQualityStatus = computed(() => {
  const aqi = airQuality.value?.aqi

  if (aqi <= 50) return '좋음'
  if (aqi <= 100) return '보통'
  if (aqi <= 150) return '민감군 주의'

  return '나쁨'
})

const viewingAdvice = computed(() => {
  if (!currentWeather.value || !forecast.value || !airQuality.value) return ''

  const currentStatus = getWeatherStatus(
    currentWeather.value.weather[0].main,
    currentWeather.value.weather[0].description,
  )

  if (currentStatus === '비') {
    return '현재 비가 내리고 있어 우비나 우산을 준비하는 것이 좋습니다.'
  }

  if (forecast.value.status.includes('비') || forecast.value.rainProbability >= 50) {
    return '약 3시간 이내 비가 올 가능성이 있어 우천 대비가 필요합니다.'
  }

  if (
    currentWeather.value.main.feels_like >= 30 ||
    forecast.value.feelsLike >= 30
  ) {
    return '체감 온도가 높아 생수를 준비하고 수분을 자주 섭취하세요.'
  }

  if (airQuality.value.aqi > 100) {
    return '대기질이 좋지 않아 야외 관람 시 마스크 착용을 권합니다.'
  }

  if (currentWeather.value.wind.speed >= 7) {
    return '바람이 강하게 불어 가벼운 소지품 관리에 주의해야 합니다.'
  }

  if (currentWeather.value.main.temp <= 15) {
    return '기온이 낮아 체온을 유지할 수 있는 겉옷을 준비하세요.'
  }

  return '야구를 관람하기에 비교적 무난한 날씨입니다.'
})

const kakaoDirectionsUrl = computed(() => {
  if (!stadium.value) return '#'

  const name = encodeURIComponent(stadium.value.name)
  return `https://map.kakao.com/link/to/${name},${stadium.value.lat},${stadium.value.lon}`
})

const addCustomItem = () => {
  const wasAdded = preparationStore.addCustomItem(customItemName.value)

  if (!wasAdded) {
    customItemError.value = '이미 목록에 있거나 입력 내용이 없습니다.'
    return
  }

  customItemName.value = ''
  customItemError.value = ''
}

const loadGameDetail = async () => {
  if (!stadium.value) return

  isLoading.value = true
  errorMessage.value = ''
  currentWeather.value = null
  forecast.value = null
  airQuality.value = null

  try {
    const [weatherResult, forecastResult, airQualityResult] = await Promise.all([
      fetchCurrentWeather(stadium.value),
      fetchThreeHourForecast(stadium.value),
      fetchAirQuality(stadium.value),
    ])

    currentWeather.value = weatherResult
    forecast.value = forecastResult
    airQuality.value = airQualityResult

    preparationStore.setRecommendations(
      {
        temp: weatherResult.main.temp,
        status: getWeatherStatus(
          weatherResult.weather[0].main,
          weatherResult.weather[0].description,
        ),
        windSpeed: weatherResult.wind.speed,
      },
      airQualityResult,
      `game:${game.value.id}`,
    )
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(
      error,
      '경기 관람 정보를 불러오지 못했습니다.',
    )
  } finally {
    isLoading.value = false
  }
}

watch(() => props.gameId, loadGameDetail, { immediate: true })
</script>

<template>
  <section v-if="game && stadium" class="detail-page">
    <div class="detail-heading">
      <div>
        <RouterLink class="back-link" :to="{ name: 'weather-final' }">
          ← 오늘의 경기
        </RouterLink>
        <h2>{{ game.homeTeam.name }} vs {{ game.awayTeam.name }}</h2>
        <p>{{ stadium.name }} · {{ game.startTime }}</p>
      </div>

      <a :href="kakaoDirectionsUrl" target="_blank" rel="noopener noreferrer">
        <el-button>카카오맵 길찾기</el-button>
      </a>
    </div>

    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      :closable="false"
      show-icon
    />

    <el-card v-if="isLoading" shadow="never">
      <el-skeleton :rows="8" animated />
    </el-card>

    <template v-else-if="currentWeather && forecast && airQuality">
      <el-row :gutter="16" class="information-grid">
        <el-col :xs="24" :md="8" class="information-column">
          <el-card shadow="never">
            <template #header><strong>현재 날씨</strong></template>
            <dl class="weather-list">
              <div>
                <dt>날씨</dt>
                <dd>{{ currentWeather.weather[0].description }}</dd>
              </div>
              <div>
                <dt>기온</dt>
                <dd>{{ currentWeather.main.temp.toFixed(1) }}℃</dd>
              </div>
              <div>
                <dt>체감 온도</dt>
                <dd>{{ currentWeather.main.feels_like.toFixed(1) }}℃</dd>
              </div>
              <div>
                <dt>습도 / 풍속</dt>
                <dd>{{ currentWeather.main.humidity }}% / {{ currentWeather.wind.speed }}m/s</dd>
              </div>
            </dl>
          </el-card>
        </el-col>

        <el-col :xs="24" :md="8" class="information-column">
          <el-card shadow="never">
            <template #header><strong>약 3시간 뒤 예보</strong></template>
            <dl class="weather-list">
              <div>
                <dt>예보 시각</dt>
                <dd>{{ forecast.dateText }}</dd>
              </div>
              <div>
                <dt>날씨</dt>
                <dd>{{ forecast.status }}</dd>
              </div>
              <div>
                <dt>기온 / 체감</dt>
                <dd>{{ forecast.temp }}℃ / {{ forecast.feelsLike }}℃</dd>
              </div>
              <div>
                <dt>강수 확률</dt>
                <dd>{{ forecast.rainProbability }}%</dd>
              </div>
            </dl>
          </el-card>
        </el-col>

        <el-col :xs="24" :md="8" class="information-column">
          <el-card shadow="never">
            <template #header><strong>현재 대기질</strong></template>
            <dl class="weather-list">
              <div>
                <dt>상태</dt>
                <dd>{{ airQualityStatus }}</dd>
              </div>
              <div>
                <dt>미세먼지 PM10</dt>
                <dd>{{ airQuality.pm10 }}㎍/㎥</dd>
              </div>
              <div>
                <dt>초미세먼지 PM2.5</dt>
                <dd>{{ airQuality.pm2_5 }}㎍/㎥</dd>
              </div>
              <div>
                <dt>대기질 지수</dt>
                <dd>{{ airQuality.aqi }}</dd>
              </div>
            </dl>
          </el-card>
        </el-col>
      </el-row>

      <div class="viewing-advice">
        <strong>관람 안내</strong>
        <span>{{ viewingAdvice }}</span>
      </div>

      <el-card class="checklist-card" shadow="never">
        <template #header>
          <div class="card-heading">
            <div>
              <strong>관람 준비물</strong>
              <small>추천 준비물을 확인하고 개인 준비물도 추가할 수 있습니다.</small>
            </div>

            <el-button size="small" @click="preparationStore.resetItems">
              체크 초기화
            </el-button>
          </div>
        </template>

        <el-progress :percentage="preparationProgress" />

        <div class="custom-item-form">
          <el-input
            v-model="customItemName"
            maxlength="30"
            placeholder="개인 준비물 입력"
            @input="customItemError = ''"
            @keyup.enter="addCustomItem"
          />
          <el-button
            type="primary"
            plain
            :disabled="!customItemName.trim()"
            @click="addCustomItem"
          >
            추가
          </el-button>
        </div>

        <p v-if="customItemError" class="custom-item-error">
          {{ customItemError }}
        </p>

        <div class="checklist-items">
          <div
            v-for="item in preparationStore.items"
            :key="item.id"
            class="checklist-item"
          >
            <el-checkbox
              :model-value="item.checked"
              @change="preparationStore.toggleItem(item.id)"
            >
              {{ item.name }}
            </el-checkbox>

            <el-button
              v-if="item.isCustom"
              type="danger"
              link
              size="small"
              @click="preparationStore.removeCustomItem(item.id)"
            >
              삭제
            </el-button>
          </div>
        </div>
      </el-card>

      <el-card class="map-card" shadow="never">
        <template #header><strong>{{ stadium.name }} 위치</strong></template>
        <KakaoStadiumMap :stadiums="[stadium]" />
      </el-card>
    </template>
  </section>

  <el-empty v-else description="경기 정보를 찾을 수 없습니다.">
    <RouterLink :to="{ name: 'weather-final' }">오늘의 경기로 돌아가기</RouterLink>
  </el-empty>
</template>

<style scoped>
.detail-page {
  padding: 1.5rem;
  border: 1px solid #dfe5ec;
  border-radius: 10px;
  background: #fff;
}

.detail-heading,
.card-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.detail-heading {
  margin-bottom: 1.25rem;
}

.detail-heading h2 {
  margin: 0.5rem 0 0.25rem;
}

.detail-heading p {
  margin: 0;
  color: #6b7785;
}

.back-link {
  padding: 0;
  color: #409eff;
}

.information-grid,
.checklist-card,
.map-card {
  margin-top: 1rem;
}

.viewing-advice {
  display: flex;
  gap: 0.75rem;
  padding: 0.9rem 1rem;
  margin-top: 0;
  border: 1px solid #dfe5ec;
  border-radius: 8px;
  background: #f7f9fb;
}

.viewing-advice strong {
  flex: 0 0 auto;
}

.information-column {
  margin-bottom: 1rem;
}

.information-column .el-card {
  height: 100%;
}

.weather-list {
  margin: 0;
}

.weather-list > div {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.55rem 0;
  border-bottom: 1px solid #ebeef5;
}

.weather-list > div:last-child {
  border-bottom: 0;
}

.weather-list dt {
  color: #6b7785;
}

.weather-list dd {
  margin: 0;
  text-align: right;
}

.card-heading > div {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.card-heading small {
  color: #8492a6;
}

.custom-item-form {
  display: flex;
  gap: 0.5rem;
  max-width: 460px;
  margin-top: 1rem;
}

.custom-item-error {
  margin: 0.4rem 0 0;
  color: #f56c6c;
  font-size: 0.85rem;
}

.checklist-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.75rem;
  margin-top: 1rem;
}

.checklist-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

@media (max-width: 640px) {
  .detail-page {
    padding: 1rem;
  }

  .detail-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .viewing-advice,
  .custom-item-form {
    flex-direction: column;
  }
}
</style>
