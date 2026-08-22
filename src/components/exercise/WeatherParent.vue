<script setup>
import { ref, computed, watch, watchEffect } from 'vue'
import { useRouter } from 'vue-router'
import BaseDashboardCard from './BaseDashboardCard.vue'
import SearchBar from './SearchBar.vue'
import WeatherCard from './WeatherCard.vue'
import CheerUp from './CheerUp.vue'

const props = defineProps({
  detailsAsRoute: {
    type: Boolean,
    default: false,
  },
  detailRouteName: {
    type: String,
    default: 'exercise-weather-detail',
  },
  stadiumId: {
    type: String,
    default: '',
  },

  showCheerUp: {
    type: Boolean,
    default: true,
  },
})

const router = useRouter()

const weatherList = ref([
  { id: 'city_01', name: '광주기아챔피언스필드', temp: 35, status: '맑음' },
  { id: 'city_02', name: '대전한화생명볼파크', temp: 32, status: '비' },
  { id: 'city_03', name: '수원KT위즈파크', temp: 33, status: '흐림' },
  { id: 'city_04', name: '창원NC파크', temp: 34, status: '흐림' },
  { id: 'city_05', name: '대구삼성라이온즈파크', temp: 36, status: '맑음' },
])

const searchQuery = ref('')
const selectedCityInfo = ref('구장을 클릭하거나 검색해 보세요')
const showDetail = (item) => {
  if (props.detailsAsRoute) {
    router.push({ name: props.detailRouteName, params: { cityId: item.id } })
    return
  }

  window.alert(`${item.name}의 현재 날씨는 [${item.status}] 상태입니다.`)
}

const filteredWeatherList = computed(() => {
  let result = weatherList.value

  if (props.stadiumId) {
    result = result.filter((item) => {
      return item.id === props.stadiumId
    })
  }

  const query = searchQuery.value.trim()

  if (query) {
    result = result.filter((item) => {
      return item.name.includes(query)
    })
  }

  return result
})

watch(selectedCityInfo, (newInfo) => {
  console.log(`[watch 감지] 상태 바 문구가 업데이트되었습니다 -> "${newInfo}"`)
})

watchEffect(() => {
  console.log(
    `[watchEffect 자동 호출] 현재 검색어 '${searchQuery.value}'에 매칭되는 API 데이터를 필터링합니다.`,
  )
})
</script>

<template>
  <div class="dashboard-wrapper">
    <div class="status-bar">
      {{ selectedCityInfo }}
    </div>

    <BaseDashboardCard>
      <SearchBar :current-query="searchQuery" @update-query="(val) => (searchQuery = val)" />
    </BaseDashboardCard>

    <BaseDashboardCard>
      <h3>🏟️ 구장별 날씨 현황</h3>
      <WeatherCard
        v-for="item in filteredWeatherList"
        :key="item.id"
        :city-item="item"
        @select-card="(msg) => (selectedCityInfo = msg)"
        @click-detail="showDetail(item)"
      />

      <p
        v-if="filteredWeatherList.length === 0"
        style="text-align: center; color: #e74c3c; padding: 10px 0"
      >
        오늘 경기가 없는 구장입니다.
      </p>
    </BaseDashboardCard>
    <CheerUp v-if="showCheerUp" />
  </div>
</template>

<style scoped>
.dashboard-wrapper {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  align-items: center;
  text-align: center;
}
</style>
