<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
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
const router = useRouter()

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

  return Math.round((preparationStore.completedCount / preparationStore.items.length) * 100)
})

const airQualityStatus = computed(() => {
  const aqi = airQuality.value?.aqi

  if (aqi <= 50) return '좋음'
  if (aqi <= 100) return '보통'
  if (aqi <= 150) return '민감군 주의'

  return '나쁨'
})

const currentWeatherTagType = computed(() => {
  const weatherMain = currentWeather.value?.weather[0]?.main

  if (weatherMain === 'Clear') return 'success'
  if (['Rain', 'Drizzle', 'Thunderstorm'].includes(weatherMain)) return 'danger'
  if (weatherMain === 'Clouds') return 'info'

  return 'warning'
})

const forecastTagType = computed(() => {
  const status = forecast.value?.status ?? ''

  if (status.includes('비')) return 'danger'
  if (status.includes('맑')) return 'success'

  return 'info'
})

const airQualityTagType = computed(() => {
  const aqi = airQuality.value?.aqi

  if (aqi <= 50) return 'success'
  if (aqi <= 100) return 'warning'

  return 'danger'
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

  if (currentWeather.value.main.feels_like >= 30 || forecast.value.feelsLike >= 30) {
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

const viewingAdviceType = computed(() => {
  if (!currentWeather.value || !forecast.value || !airQuality.value) return 'info'

  const currentStatus = getWeatherStatus(
    currentWeather.value.weather[0].main,
    currentWeather.value.weather[0].description,
  )

  if (
    currentStatus === '비' ||
    forecast.value.status.includes('비') ||
    forecast.value.rainProbability >= 50 ||
    currentWeather.value.main.feels_like >= 30 ||
    forecast.value.feelsLike >= 30
  ) {
    return 'warning'
  }

  if (airQuality.value.aqi > 100) return 'error'

  if (currentWeather.value.wind.speed >= 7 || currentWeather.value.main.temp <= 15) {
    return 'warning'
  }

  return 'success'
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

const goBackToGames = () => {
  router.push({ name: 'weather-final' })
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
        feelsLike: weatherResult.main.feels_like,
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
    errorMessage.value = getRequestErrorMessage(error, '경기 관람 정보를 불러오지 못했습니다.')
  } finally {
    isLoading.value = false
  }
}

watch(() => props.gameId, loadGameDetail, { immediate: true })
</script>

<template>
  <section v-if="game && stadium" class="detail-page">
    <el-page-header class="detail-heading" title="오늘의 경기" @back="goBackToGames">
      <template #content>
        <div class="match-title">
          <strong>{{ game.homeTeam.name }} vs {{ game.awayTeam.name }}</strong>
          <el-tag type="info" effect="plain">{{ game.startTime }}</el-tag>
        </div>
      </template>

      <template #extra>
        <a :href="kakaoDirectionsUrl" target="_blank" rel="noopener noreferrer">
          <el-button type="primary" plain>카카오맵 길찾기</el-button>
        </a>
      </template>

      <p class="stadium-name">🏟️ {{ stadium.name }}</p>
    </el-page-header>

    <el-alert v-if="errorMessage" :title="errorMessage" type="error" :closable="false" show-icon />

    <el-card v-if="isLoading" shadow="never">
      <el-skeleton :rows="8" animated />
    </el-card>

    <template v-else-if="currentWeather && forecast && airQuality">
      <el-row :gutter="16" class="information-grid">
        <el-col :xs="24" :md="8" class="information-column">
          <el-card class="information-card" shadow="never">
            <template #header>
              <div class="card-title">
                <strong>현재 날씨</strong>
                <el-tag :type="currentWeatherTagType" effect="plain">
                  {{ currentWeather.weather[0].description }}
                </el-tag>
              </div>
            </template>

            <el-descriptions :column="1" border>
              <el-descriptions-item label="기온">
                {{ currentWeather.main.temp.toFixed(1) }}℃
              </el-descriptions-item>
              <el-descriptions-item label="체감 온도">
                <el-tag
                  :type="currentWeather.main.feels_like >= 30 ? 'danger' : 'info'"
                  effect="plain"
                >
                  {{ currentWeather.main.feels_like.toFixed(1) }}℃
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="습도">
                {{ currentWeather.main.humidity }}%
              </el-descriptions-item>
              <el-descriptions-item label="풍속">
                {{ currentWeather.wind.speed }}m/s
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>

        <el-col :xs="24" :md="8" class="information-column">
          <el-card class="information-card" shadow="never">
            <template #header>
              <div class="card-title">
                <strong>약 3시간 뒤 예보</strong>
                <el-tag :type="forecastTagType" effect="plain">
                  {{ forecast.status }}
                </el-tag>
              </div>
            </template>

            <el-descriptions :column="1" border>
              <el-descriptions-item label="예보 시각">
                {{ forecast.dateText }}
              </el-descriptions-item>
              <el-descriptions-item label="기온"> {{ forecast.temp }}℃ </el-descriptions-item>
              <el-descriptions-item label="체감 온도">
                {{ forecast.feelsLike }}℃
              </el-descriptions-item>
              <el-descriptions-item label="강수 확률">
                <el-tag :type="forecast.rainProbability >= 50 ? 'danger' : 'info'" effect="plain">
                  {{ forecast.rainProbability }}%
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>

        <el-col :xs="24" :md="8" class="information-column">
          <el-card class="information-card" shadow="never">
            <template #header>
              <div class="card-title">
                <strong>현재 대기질</strong>
                <el-tag :type="airQualityTagType" effect="plain">
                  {{ airQualityStatus }}
                </el-tag>
              </div>
            </template>

            <el-descriptions :column="1" border>
              <el-descriptions-item label="미세먼지 PM10">
                {{ airQuality.pm10 }}㎍/㎥
              </el-descriptions-item>
              <el-descriptions-item label="초미세먼지 PM2.5">
                {{ airQuality.pm2_5 }}㎍/㎥
              </el-descriptions-item>
              <el-descriptions-item label="대기질 지수">
                {{ airQuality.aqi }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>

      <el-alert
        class="viewing-advice"
        title="관람 안내"
        :description="viewingAdvice"
        :type="viewingAdviceType"
        :closable="false"
        show-icon
      />

      <el-divider content-position="left">관람 준비</el-divider>

      <el-card class="checklist-card" shadow="never">
        <template #header>
          <div class="card-heading">
            <div>
              <strong>관람 준비물</strong>
              <small>추천 준비물을 확인하고 개인 준비물도 추가할 수 있습니다.</small>
            </div>

            <el-button size="small" @click="preparationStore.resetItems"> 체크 초기화 </el-button>
          </div>
        </template>

        <el-progress
          :percentage="preparationProgress"
          :status="preparationProgress === 100 ? 'success' : undefined"
        />

        <div class="custom-item-form">
          <el-input
            v-model="customItemName"
            maxlength="30"
            placeholder="개인 준비물 입력"
            @input="customItemError = ''"
            @keyup.enter="addCustomItem"
          />
          <el-button type="primary" plain :disabled="!customItemName.trim()" @click="addCustomItem">
            추가
          </el-button>
        </div>

        <el-text v-if="customItemError" class="custom-item-error" type="danger" tag="p">
          {{ customItemError }}
        </el-text>

        <div class="checklist-items">
          <div v-for="item in preparationStore.items" :key="item.id" class="checklist-item">
            <div class="checklist-label">
              <el-checkbox
                :model-value="item.checked"
                @change="preparationStore.toggleItem(item.id)"
              >
                {{ item.name }}
              </el-checkbox>

              <el-tag v-if="item.name === '생수'" type="danger" effect="plain" size="small">
                더위 대비
              </el-tag>
            </div>

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
        <template #header
          ><strong>{{ stadium.name }} 위치</strong></template
        >
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

.card-heading,
.card-title,
.match-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.detail-heading {
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #ebeef5;
}

.match-title {
  justify-content: flex-start;
}

.match-title strong {
  font-size: 1.2rem;
}

.stadium-name {
  margin: 1rem 0 0;
  color: #6b7785;
}

.information-grid,
.checklist-card,
.map-card {
  margin-top: 1rem;
}

.viewing-advice {
  margin-top: 0;
}

.information-column {
  margin-bottom: 1rem;
}

.information-card {
  height: 100%;
}

.card-title {
  flex-wrap: wrap;
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

.checklist-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

@media (max-width: 640px) {
  .detail-page {
    padding: 1rem;
  }

  .custom-item-form {
    flex-direction: column;
  }

  .match-title {
    align-items: flex-start;
    flex-direction: column;
    gap: 0.35rem;
  }
}
</style>
