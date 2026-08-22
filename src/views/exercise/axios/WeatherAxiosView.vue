<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { usePreparationStore } from '@/stores/preparationStore'

const preparationStore = usePreparationStore()
const weatherList = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const selectedForecast = ref(null)
const forecastLoadingId = ref('')
const selectedAirQuality = ref(null)
const airQualityLoadingId = ref('')
const selectedPreparation = ref(null)

const AIR_QUALITY_URL = 'https://air-quality-api.open-meteo.com/v1/air-quality'

const API_KEY = import.meta.env.VITE_OPENWEATHER_API_KEY

const BASE_URL = import.meta.env.VITE_OPENWEATHER_BASE_URL

const stadiums = [
  {
    id: 'city_01',
    name: '광주기아챔피언스필드',
    lat: 35.1684282,
    lon: 126.888283,
  },
  {
    id: 'city_02',
    name: '대전한화생명볼파크',
    lat: 36.3171,
    lon: 127.4291,
  },
  {
    id: 'city_03',
    name: '수원KT위즈파크',
    lat: 37.2997,
    lon: 127.0097,
  },
  {
    id: 'city_04',
    name: '창원NC파크',
    lat: 35.2225,
    lon: 128.5822,
  },
  {
    id: 'city_05',
    name: '대구삼성라이온즈파크',
    lat: 35.8412,
    lon: 128.6816,
  },
]

const fetchAllStadiumWeather = async () => {
  isLoading.value = true
  errorMessage.value = ''
  weatherList.value = []

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
    const targetTime = Math.floor(Date.now() / 1000) + 3 * 60 * 60

    // OpenWeather의 3시간 단위 예보 중 현재로부터 3시간 뒤에 가장 가까운 항목을 선택합니다.
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
    errorMessage.value = error.response?.data?.message ?? '3시간 뒤 예보를 가져오지 못했습니다.'
  } finally {
    forecastLoadingId.value = ''
  }
}
const getAirQualityStatus = (aqi) => {
  if (aqi <= 50) return '좋음'
  if (aqi <= 100) return '보통'
  if (aqi <= 150) return '민감군 주의'

  return '나쁨'
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

    if (weatherMain === 'Clear') {
      normalizedStatus = '맑음'
    }

    if (['Rain', 'Drizzle', 'Thunderstorm'].includes(weatherMain)) {
      normalizedStatus = '비'
    }

    const actualWeather = {
      temp: stadium.weather.main.temp,
      status: normalizedStatus,
      windSpeed: stadium.weather.wind.speed,
    }

    preparationStore.setRecommendations(actualWeather, selectedAirQuality.value)

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
  <section class="axios-view">
    <h2>🌦️ 야구장 실시간 날씨 Axios</h2>

    <p>OpenWeatherMap API를 이용해 오늘 경기가 열리는 야구장의 실제 날씨를 가져옵니다.</p>

    <button :disabled="isLoading" @click="fetchAllStadiumWeather">
      {{ isLoading ? '날씨 불러오는 중...' : '전체 야구장 날씨 가져오기' }}
    </button>

    <p v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </p>

    <div v-if="weatherList.length > 0" class="weather-grid">
      <article v-for="stadium in weatherList" :key="stadium.id" class="weather-card">
        <h3>🏟️ {{ stadium.name }}</h3>

        <p>
          현재 기온:
          {{ stadium.weather.main.temp }}℃
        </p>

        <p>
          체감 온도:
          {{ stadium.weather.main.feels_like }}℃
        </p>

        <p>
          날씨:
          {{ stadium.weather.weather[0].description }}
        </p>

        <p>
          습도:
          {{ stadium.weather.main.humidity }}%
        </p>

        <p>
          풍속:
          {{ stadium.weather.wind.speed }}m/s
        </p>
        <button
          class="forecast-button"
          :disabled="forecastLoadingId === stadium.id"
          @click="fetchThreeHourForecast(stadium)"
        >
          {{ forecastLoadingId === stadium.id ? '예보 불러오는 중...' : '3시간 뒤 예보 보기' }}
        </button>
        <button
          class="air-quality-button"
          :disabled="airQualityLoadingId === stadium.id"
          @click="fetchAirQuality(stadium)"
        >
          {{ airQualityLoadingId === stadium.id ? '미세먼지 불러오는 중...' : '미세먼지 확인' }}
        </button>
      </article>
    </div>

    <article v-if="selectedForecast" class="forecast-result">
      <h3>⏰ 약 3시간 뒤 날씨 예보</h3>

      <p>구장: {{ selectedForecast.stadiumName }}</p>

      <p>예보 기준 시간: {{ selectedForecast.dateText }}</p>

      <p>
        예상 기온:
        {{ selectedForecast.temp }}℃
      </p>

      <p>
        체감 온도:
        {{ selectedForecast.feelsLike }}℃
      </p>

      <p>
        예상 날씨:
        {{ selectedForecast.status }}
      </p>

      <p>
        비 올 확률:
        {{ selectedForecast.rainProbability }}%
      </p>

      <p>
        예상 풍속:
        {{ selectedForecast.windSpeed }}m/s
      </p>
    </article>
    <article v-if="selectedAirQuality" class="air-quality-result">
      <h3>😷 야구장 미세먼지 정보</h3>

      <p>구장: {{ selectedAirQuality.stadiumName }}</p>

      <p>
        미세먼지(PM10):
        {{ selectedAirQuality.pm10 }}㎍/㎥
      </p>

      <p>
        초미세먼지(PM2.5):
        {{ selectedAirQuality.pm2_5 }}㎍/㎥
      </p>

      <p>
        대기질 지수:
        {{ selectedAirQuality.aqi }}
      </p>

      <p>
        대기 상태:
        <strong>{{ selectedAirQuality.status }}</strong>
      </p>

      <p v-if="selectedAirQuality.aqi > 100">😷 대기질이 좋지 않으니 마스크를 준비하세요.</p>

      <p v-else>✅ 야외 관람이 가능한 대기 상태입니다.</p>
    </article>
    <article v-if="selectedPreparation" class="preparation-result">
      <h3>🎒 실제 날씨 기반 관람 준비물</h3>

      <p>
        {{ selectedPreparation.stadiumName }}의 {{ selectedPreparation.weatherStatus }} 날씨와
        대기질 기준 추천
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

      <button
        :disabled="preparationStore.completedCount === 0"
        @click="preparationStore.resetItems"
      >
        체크 초기화
      </button>
    </article>

    <p v-if="weatherList.length === 0 && !isLoading && !errorMessage" class="empty-message">
      버튼을 눌러 야구장 날씨를 불러와 주세요.
    </p>
  </section>
</template>

<style scoped>
.axios-view {
  width: 100%;
  text-align: center;
}

.axios-view > button {
  padding: 0.7rem 1rem;
  margin: 1rem 0;
  cursor: pointer;
  border: 0;
  border-radius: 8px;
  background: #42b883;
  color: white;
}

.axios-view > button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.weather-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.weather-card {
  padding: 1rem;
  text-align: left;
  border: 1px solid #d7dee8;
  border-radius: 10px;
  background: #eef6ff;
}

.weather-card h3 {
  margin-bottom: 0.75rem;
}

.weather-card p {
  margin: 0.4rem 0;
}

.error-message {
  color: #d93025;
}

.empty-message {
  margin-top: 1rem;
  color: #68737d;
}

.forecast-button {
  width: 100%;
  padding: 0.5rem;
  margin-top: 0.75rem;
  cursor: pointer;
}

.forecast-result {
  max-width: 500px;
  padding: 1rem;
  margin: 1.5rem auto 0;
  text-align: left;
  border: 2px solid #42b883;
  border-radius: 10px;
  background: #f0fff8;
}

.forecast-result p {
  margin: 0.5rem 0;
}
.air-quality-button {
  width: 100%;
  padding: 0.5rem;
  margin-top: 0.5rem;
  cursor: pointer;
}

.air-quality-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.air-quality-result {
  max-width: 500px;
  padding: 1rem;
  margin: 1.5rem auto 0;
  text-align: left;
  border: 2px solid #5b8def;
  border-radius: 10px;
  background: #f2f7ff;
}

.air-quality-result p {
  margin: 0.5rem 0;
}

.preparation-result {
  max-width: 500px;
  padding: 1rem;
  margin: 1.5rem auto 0;
  text-align: left;
  border: 2px solid #f0a83b;
  border-radius: 10px;
  background: #fff9e8;
}

.preparation-result ul {
  padding: 0;
  list-style: none;
}

.preparation-result li {
  margin: 0.75rem 0;
}

.preparation-result label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.preparation-result button {
  padding: 0.5rem 0.75rem;
  cursor: pointer;
}

.preparation-result button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.completed {
  color: #8a949f;
  text-decoration: line-through;
}
</style>
