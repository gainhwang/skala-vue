<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import axios from 'axios'
import { usePreparationStore } from '@/stores/preparationStore'
import KakaoStadiumMap from '@/components/exercise/KakaoStadiumMap.vue'

const preparationStore = usePreparationStore()

const weatherList = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const selectedForecast = ref(null)
const forecastLoadingId = ref('')
const selectedAirQuality = ref(null)
const airQualityLoadingId = ref('')
const selectedPreparation = ref(null)

const API_KEY = import.meta.env.VITE_OPENWEATHER_API_KEY
const BASE_URL = import.meta.env.VITE_OPENWEATHER_BASE_URL
const AIR_QUALITY_URL = 'https://air-quality-api.open-meteo.com/v1/air-quality'

const stadiums = [
  {
    id: 'city_01',
    name: '광주기아챔피언스필드',
    homeTeam: 'KIA 타이거즈',
    lat: 35.1684282,
    lon: 126.888283,
  },
  {
    id: 'city_02',
    name: '대전한화생명볼파크',
    homeTeam: '한화 이글스',
    lat: 36.3171,
    lon: 127.4291,
  },
  {
    id: 'city_03',
    name: '수원KT위즈파크',
    homeTeam: 'KT 위즈',
    lat: 37.2997,
    lon: 127.0097,
  },
  {
    id: 'city_04',
    name: '창원NC파크',
    homeTeam: 'NC 다이노스',
    lat: 35.2225,
    lon: 128.5822,
  },
  {
    id: 'city_05',
    name: '대구삼성라이온즈파크',
    homeTeam: '삼성 라이온즈',
    lat: 35.8412,
    lon: 128.6816,
  },
  {
    id: 'city_06',
    name: '서울잠실야구장',
    homeTeam: 'LG 트윈스 · 두산 베어스',
    lat: 37.5122,
    lon: 127.0719,
  },
  {
    id: 'city_07',
    name: '인천SSG랜더스필드',
    homeTeam: 'SSG 랜더스',
    lat: 37.437,
    lon: 126.6933,
  },
  {
    id: 'city_08',
    name: '고척스카이돔',
    homeTeam: '키움 히어로즈',
    lat: 37.4983,
    lon: 126.8672,
  },
  {
    id: 'city_09',
    name: '부산사직야구장',
    homeTeam: '롯데 자이언츠',
    lat: 35.194,
    lon: 129.0615,
  },
]

const preparationProgress = computed(() => {
  if (preparationStore.items.length === 0) return 0

  return Math.round((preparationStore.completedCount / preparationStore.items.length) * 100)
})

const getWeatherTagType = (weatherMain) => {
  if (weatherMain === 'Clear') return 'success'
  if (['Rain', 'Drizzle', 'Thunderstorm'].includes(weatherMain)) return 'danger'
  if (weatherMain === 'Clouds') return 'info'

  return 'warning'
}

const getAirQualityStatus = (aqi) => {
  if (aqi <= 50) return '좋음'
  if (aqi <= 100) return '보통'
  if (aqi <= 150) return '민감군 주의'

  return '나쁨'
}

const getAirQualityTagType = (aqi) => {
  if (aqi <= 50) return 'success'
  if (aqi <= 100) return 'warning'

  return 'danger'
}

const fetchAllStadiumWeather = async () => {
  if (!API_KEY || !BASE_URL) {
    errorMessage.value = '.env.local의 OpenWeather API 설정을 확인해 주세요.'
    return
  }

  isLoading.value = true
  errorMessage.value = ''
  weatherList.value = []
  selectedForecast.value = null
  selectedAirQuality.value = null
  selectedPreparation.value = null

  try {
    const requests = stadiums.map(async (stadium) => {
      const response = await axios.get(`${BASE_URL}/weather`, {
        params: {
          lat: stadium.lat,
          lon: stadium.lon,
          appid: API_KEY,
          units: 'metric',
          lang: 'kr',
        },
      })

      return {
        ...stadium,
        weather: response.data,
      }
    })

    weatherList.value = await Promise.all(requests)
  } catch (error) {
    errorMessage.value = error.response?.data?.message ?? '야구장 날씨를 가져오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const fetchThreeHourForecast = async (stadium) => {
  forecastLoadingId.value = stadium.id
  errorMessage.value = ''

  try {
    const response = await axios.get(`${BASE_URL}/forecast`, {
      params: {
        lat: stadium.lat,
        lon: stadium.lon,
        appid: API_KEY,
        units: 'metric',
        lang: 'kr',
      },
    })

    const forecasts = response.data.list

    if (!forecasts?.length) {
      throw new Error('예보 데이터가 없습니다.')
    }

    const targetTime = Math.floor(Date.now() / 1000) + 3 * 60 * 60
    const forecast = forecasts.reduce((closest, item) => {
      const closestDifference = Math.abs(closest.dt - targetTime)
      const itemDifference = Math.abs(item.dt - targetTime)

      return itemDifference < closestDifference ? item : closest
    }, forecasts[0])

    const timezoneOffset = response.data.city.timezone
    const localDate = new Date((forecast.dt + timezoneOffset) * 1000)

    selectedForecast.value = {
      stadiumName: stadium.name,
      dateText: localDate.toLocaleString('ko-KR', {
        timeZone: 'UTC',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      }),
      temp: forecast.main.temp,
      feelsLike: forecast.main.feels_like,
      status: forecast.weather[0].description,
      humidity: forecast.main.humidity,
      windSpeed: forecast.wind.speed,
      rainProbability: Math.round((forecast.pop ?? 0) * 100),
    }
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ?? error.message ?? '3시간 뒤 예보를 가져오지 못했습니다.'
  } finally {
    forecastLoadingId.value = ''
  }
}

const fetchAirQuality = async (stadium) => {
  airQualityLoadingId.value = stadium.id
  errorMessage.value = ''

  try {
    const response = await axios.get(AIR_QUALITY_URL, {
      params: {
        latitude: stadium.lat,
        longitude: stadium.lon,
        current: 'pm10,pm2_5,us_aqi',
        timezone: 'Asia/Seoul',
      },
    })

    const current = response.data.current

    selectedAirQuality.value = {
      stadiumName: stadium.name,
      pm10: current.pm10,
      pm2_5: current.pm2_5,
      aqi: current.us_aqi,
      status: getAirQualityStatus(current.us_aqi),
    }

    const weatherMain = stadium.weather.weather[0].main
    let normalizedStatus = stadium.weather.weather[0].description

    if (weatherMain === 'Clear') normalizedStatus = '맑음'

    if (['Rain', 'Drizzle', 'Thunderstorm'].includes(weatherMain)) {
      normalizedStatus = '비'
    }

    preparationStore.setRecommendations(
      {
        temp: stadium.weather.main.temp,
        feelsLike: stadium.weather.main.feels_like,
        status: normalizedStatus,
        windSpeed: stadium.weather.wind.speed,
      },
      selectedAirQuality.value,
    )

    selectedPreparation.value = {
      stadiumName: stadium.name,
      weatherStatus: stadium.weather.weather[0].description,
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.reason ?? '미세먼지 정보를 가져오지 못했습니다.'
  } finally {
    airQualityLoadingId.value = ''
  }
}
</script>

<template>
  <section class="final-dashboard">
    <el-card class="hero-card" shadow="never">
      <div class="hero-content">
        <div>
          <el-tag type="success" effect="dark" round>FINAL PROJECT</el-tag>
          <h2>⚾ 야구장 관람 날씨 가이드</h2>
          <p>실시간 날씨·3시간 뒤 예보·대기질을 확인하고 준비물을 추천받아 보세요.</p>
        </div>

        <div class="hero-actions">
          <RouterLink class="exercise-link" to="/exercise">
            <el-button size="large" plain>📚 이전 과제 보기</el-button>
          </RouterLink>

          <el-button
            type="primary"
            size="large"
            :loading="isLoading"
            @click="fetchAllStadiumWeather"
          >
            {{ isLoading ? '날씨 불러오는 중' : '전체 야구장 날씨 조회' }}
          </el-button>
        </div>
      </div>
    </el-card>

    <el-alert
      class="source-alert"
      title="OpenWeather 실시간·예보 API와 Open-Meteo 대기질 API를 사용합니다."
      type="info"
      :closable="false"
      show-icon
    />

    <el-card class="map-card" shadow="never">
      <template #header>
        <div class="map-header">
          <div>
            <strong>🗺️ 전국 야구장 지도</strong>
            <small>마커를 누르면 홈구단을 확인할 수 있습니다.</small>
          </div>
        </div>
      </template>

      <KakaoStadiumMap :stadiums="stadiums" />
    </el-card>

    <el-alert
      v-if="errorMessage"
      class="error-alert"
      :title="errorMessage"
      type="error"
      :closable="false"
      show-icon
    />

    <el-card v-if="isLoading" class="loading-card" shadow="never">
      <el-skeleton :rows="6" animated />
    </el-card>

    <el-empty
      v-else-if="weatherList.length === 0"
      description="버튼을 눌러 야구장 날씨를 불러와 주세요."
    />

    <el-row v-else :gutter="16" class="stadium-grid">
      <el-col
        v-for="stadium in weatherList"
        :key="stadium.id"
        :xs="24"
        :sm="12"
        :lg="8"
        class="stadium-column"
      >
        <el-card class="stadium-card" shadow="hover">
          <template #header>
            <div class="stadium-header">
              <div>
                <strong>🏟️ {{ stadium.name }}</strong>
                <small>{{ stadium.homeTeam }}</small>
              </div>

              <el-tag
                :type="getWeatherTagType(stadium.weather.weather[0].main)"
                effect="dark"
                round
              >
                {{ stadium.weather.weather[0].description }}
              </el-tag>
            </div>
          </template>

          <el-statistic
            title="현재 기온"
            :value="stadium.weather.main.temp"
            :precision="1"
            suffix="℃"
          />

          <el-divider />

          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="체감 온도">
              {{ stadium.weather.main.feels_like }}℃
            </el-descriptions-item>
            <el-descriptions-item label="습도">
              {{ stadium.weather.main.humidity }}%
            </el-descriptions-item>
            <el-descriptions-item label="풍속">
              {{ stadium.weather.wind.speed }}m/s
            </el-descriptions-item>
          </el-descriptions>

          <div class="card-actions">
            <el-button
              type="primary"
              plain
              :loading="forecastLoadingId === stadium.id"
              @click="fetchThreeHourForecast(stadium)"
            >
              3시간 뒤 예보
            </el-button>

            <el-button
              type="success"
              plain
              :loading="airQualityLoadingId === stadium.id"
              @click="fetchAirQuality(stadium)"
            >
              대기질·준비물
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row v-if="selectedForecast || selectedAirQuality" :gutter="16" class="result-grid">
      <el-col v-if="selectedForecast" :xs="24" :md="12">
        <el-card class="result-card" shadow="never">
          <template #header>
            <strong>⏰ 약 3시간 뒤 예보</strong>
          </template>

          <el-descriptions :column="1" border>
            <el-descriptions-item label="구장">
              {{ selectedForecast.stadiumName }}
            </el-descriptions-item>
            <el-descriptions-item label="예보 시각">
              {{ selectedForecast.dateText }}
            </el-descriptions-item>
            <el-descriptions-item label="기온 / 체감">
              {{ selectedForecast.temp }}℃ / {{ selectedForecast.feelsLike }}℃
            </el-descriptions-item>
            <el-descriptions-item label="날씨">
              {{ selectedForecast.status }}
            </el-descriptions-item>
            <el-descriptions-item label="강수 확률">
              <el-tag :type="selectedForecast.rainProbability >= 60 ? 'danger' : 'info'">
                {{ selectedForecast.rainProbability }}%
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col v-if="selectedAirQuality" :xs="24" :md="12">
        <el-card class="result-card" shadow="never">
          <template #header>
            <div class="result-header">
              <strong>🌿 현재 대기질</strong>
              <el-tag :type="getAirQualityTagType(selectedAirQuality.aqi)" effect="dark">
                {{ selectedAirQuality.status }}
              </el-tag>
            </div>
          </template>

          <el-descriptions :column="1" border>
            <el-descriptions-item label="구장">
              {{ selectedAirQuality.stadiumName }}
            </el-descriptions-item>
            <el-descriptions-item label="미세먼지 PM10">
              {{ selectedAirQuality.pm10 }}㎍/㎥
            </el-descriptions-item>
            <el-descriptions-item label="초미세먼지 PM2.5">
              {{ selectedAirQuality.pm2_5 }}㎍/㎥
            </el-descriptions-item>
            <el-descriptions-item label="대기질 지수">
              {{ selectedAirQuality.aqi }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <el-card v-if="selectedPreparation" class="checklist-card" shadow="never">
      <template #header>
        <div class="result-header">
          <div>
            <strong>🎒 관람 준비물 체크리스트</strong>
            <small>
              {{ selectedPreparation.stadiumName }} · {{ selectedPreparation.weatherStatus }} 기준
            </small>
          </div>

          <el-button
            size="small"
            :disabled="preparationStore.completedCount === 0"
            @click="preparationStore.resetItems"
          >
            체크 초기화
          </el-button>
        </div>
      </template>

      <el-progress
        :percentage="preparationProgress"
        :status="preparationProgress === 100 ? 'success' : undefined"
      />

      <div class="checklist-items">
        <el-checkbox
          v-for="item in preparationStore.items"
          :key="item.id"
          :model-value="item.checked"
          @change="preparationStore.toggleItem(item.id)"
        >
          {{ item.name }}
        </el-checkbox>
      </div>

      <el-text type="info">
        {{ preparationStore.remainingCount }}개의 준비물이 남았습니다.
      </el-text>
    </el-card>
  </section>
</template>

<style scoped>
.final-dashboard {
  width: 100%;
}

.hero-card {
  border: 0;
  color: #17324d;
  background: linear-gradient(135deg, #e8f8ef 0%, #eaf3ff 100%);
}

.hero-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}

.hero-content h2 {
  margin: 0.75rem 0 0.4rem;
}

.hero-content p {
  margin: 0;
  color: #5a6b7d;
}

.hero-actions {
  display: flex;
  flex-shrink: 0;
  gap: 0.75rem;
}

.exercise-link {
  padding: 0;
}

.source-alert,
.error-alert,
.loading-card,
.stadium-grid,
.result-grid,
.checklist-card {
  margin-top: 1rem;
}

.stadium-column {
  margin-bottom: 1rem;
}

.stadium-card {
  height: 100%;
}

.stadium-header,
.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.stadium-header > div,
.result-header > div {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stadium-header small,
.result-header small {
  color: #8492a6;
}

.card-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  margin-top: 1rem;
}

.card-actions .el-button {
  width: 100%;
  margin: 0;
}

.result-card {
  height: 100%;
}

.checklist-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.75rem;
  padding: 1rem 0;
}

@media (max-width: 640px) {
  .hero-content {
    align-items: stretch;
    flex-direction: column;
  }

  .hero-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .hero-actions .el-button {
    width: 100%;
    margin: 0;
  }

  .card-actions {
    grid-template-columns: 1fr;
  }
}
.source-alert,
.error-alert,
.loading-card,
.map-card,
.stadium-grid,
.result-grid,
.checklist-card {
  margin-top: 1rem;
}
.map-header > div {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.map-header small {
  color: #8492a6;
}
</style>
