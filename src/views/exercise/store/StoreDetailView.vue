<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useConfigStore } from '@/stores/configStore'

const props = defineProps({
  cityId: {
    type: String,
    required: true,
  },
})

const configStore = useConfigStore()

const weatherList = [
  { id: 'city_01', name: '광주기아챔피언스필드', temp: 35, status: '맑음' },
  { id: 'city_02', name: '대전한화생명볼파크', temp: 32, status: '비' },
  { id: 'city_03', name: '수원KT위즈파크', temp: 33, status: '흐림' },
  { id: 'city_04', name: '창원NC파크', temp: 34, status: '흐림' },
  { id: 'city_05', name: '대구삼성라이온즈파크', temp: 36, status: '맑음' },
]

const city = computed(() => {
  return weatherList.find((item) => item.id === props.cityId)
})

const displayTemp = computed(() => {
  if (!city.value) {
    return ''
  }

  const rawTemp = city.value.temp

  if (configStore.unit === 'fahrenheit') {
    return Math.round((rawTemp * 9) / 5 + 32)
  }

  return rawTemp
})
</script>

<template>
  <article class="detail-card">
    <template v-if="city">
      <h3>🏟️ {{ city.name }}</h3>
      <p>현재 날씨: {{ city.status }}</p>

      <p>
        현재 기온:
        {{ displayTemp }}{{ configStore.unitSymbol }}
      </p>
    </template>

    <template v-else>
      <h3>구장 정보를 찾을 수 없습니다.</h3>
      <p>잘못된 구장 ID: {{ cityId }}</p>
    </template>

    <RouterLink :to="{ name: 'exercise-store' }"> 야구장 날씨 홈으로 돌아가기 </RouterLink>
  </article>
</template>

<style scoped>
.detail-card {
  padding: 1.5rem;
  text-align: center;
  border-radius: 10px;
  background: rgba(164, 216, 239, 0.5);
}

.detail-card p {
  margin: 0.5rem 0;
}

.detail-card a {
  display: inline-block;
  margin-top: 1rem;
}
</style>
