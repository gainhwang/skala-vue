<script setup>
import { ref, computed, watch, watchEffect } from 'vue'

const weatherList = ref([
  { id: 'city_01', name: '광주기아챔피언스필드', temp: 35, status: '맑음' },
  { id: 'city_02', name: '대전한화생명볼파크', temp: 32, status: '비' },
  { id: 'city_03', name: '수원KT위즈파크', temp: 33, status: '흐림' },
  { id: 'city_04', name: '창원NC파크', temp: 34, status: '흐림' },
  { id: 'city_05', name: '대구삼성라이온즈파크', temp: 36, status: '맑음' },
])

const searchQuery = ref('')
const selectedCityInfo = ref('구장을 클릭하거나 검색해 보세요')
const showDetail = (cityName, status) => {
  window.alert(`${cityName}의 현재 날씨는 [${status}] 상태입니다.`)
}
const count = ref(0)

const cheerMessage = computed(() => {
  if (count.value === 0) return '아직 모인 승리 기운이 없습니다.'

  return `현재 ${count.value}번의 승리 기운이 모였습니다.`
})

const filteredWeatherList = computed(() => {
  const query = searchQuery.value.trim()
  if (!query) {
    return weatherList.value
  }
  return weatherList.value.filter((item) => item.name.includes(query))
})

watch(selectedCityInfo, (newInfo) => {
  console.log(`[watch 감지] 상태 바 문구가 업데이트되었습니다 -> "${newInfo}"`)
})

watch(count, (newCount) => {
  console.log(`[추가 watch 감지] 승리 기운이 ${newCount}번으로 변경되었습니다.`)
})

watchEffect(() => {
  console.log(
    `[watchEffect 자동 호출] 현재 검색어 '${searchQuery.value}'에 매칭되는 API 데이터를 필터링합니다.`,
  )
})
</script>

<template>
  <div class="dashboard-wrapper">
    <section class="search-box">
      <h3>🔍 구장 검색</h3>
      <input
        type="text"
        :value="searchQuery"
        @input="(e) => (searchQuery = e.target.value)"
        placeholder="검색할 구장 이름 입력"
      />
      <p>
        검색 중인 구장: <strong>{{ searchQuery }}</strong>
      </p>
    </section>

    <section class="list-box">
      <h3>🏟️ 구장별 날씨 현황</h3>

      <div
        v-for="item in filteredWeatherList"
        :key="item.id"
        class="weather-card"
        @click="selectedCityInfo = `${item.name}가 선택되었습니다.`"
      >
        <br />
        <h4>{{ item.name }} ({{ item.status }})</h4>
        <p>현재 기온: {{ item.temp }}°C</p>

        <span v-if="item.temp <= 32" class="badge cool">🍃 폭염주의보 해제</span>
        <span v-else-if="item.temp >= 35" class="heat wave warning">🚨 폭염경보 발령</span>
        <span v-else class="heat wave">🔥 폭염주의보 발령</span>
        <p></p>
        <button class="btn-detail" @click.stop="showDetail(item.name, item.status)">
          상세보기
        </button>
      </div>
      <p
        v-if="filteredWeatherList.length === 0"
        style="text-align: center; color: #e74c3c; padding: 10px 0"
      >
        오늘 경기가 없는 구장입니다.
      </p>
    </section>

    <div class="status-bar">
      {{ selectedCityInfo }}
    </div>

    <div class="cheerup">
      <h3>❤️‍🔥 응원하기 ❤️‍🔥</h3>
      <h4>{{ cheerMessage }}</h4>
      <button @click="count++">승리 버튼</button>
    </div>
  </div>
</template>

<style scoped>
.dashboard-wrapper {
  padding: 10px;
  margin-top: 20px;
  color: rgb(6, 4, 4);
  border-radius: 10px;
  background-color: rgb(251, 245, 198);
}
.search-box {
  padding: 5px;
  align-items: center;
  text-align: center;
  color: rgb(6, 4, 4);
  border-radius: 10px;
  background-color: rgba(164, 216, 239, 0.507);
}
.list-box {
  padding: 10px;
  margin-top: 10px;
  align-items: center;
  text-align: center;
  color: rgb(6, 4, 4);
  border-radius: 10px;
  background-color: rgba(164, 216, 239, 0.473);
}
.status-bar {
  padding: 10px;
  margin-top: 10px;
  align-items: center;
  text-align: center;
  color: rgb(6, 4, 4);
  border-radius: 10px;
  background-color: rgba(164, 216, 239, 0.498);
}
.cheerup {
  padding: 10px;
  margin-top: 10px;
  align-items: center;
  text-align: center;
  color: rgb(6, 4, 4);
  border-radius: 10px;
  background-color: rgba(255, 0, 221, 0.16);
}
</style>
