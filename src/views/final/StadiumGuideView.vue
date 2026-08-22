<script setup>
import { computed, ref, watch } from 'vue'
import KakaoStadiumMap from '@/components/exercise/KakaoStadiumMap.vue'
import { stadiums } from '@/data/stadiums'

const selectedStadiumId = ref('')
const selectedPlaceType = ref('맛집')
const nearbyPlaces = ref([])
const isPlaceLoading = ref(false)
const placeError = ref('')
const isMapReady = ref(false)

const placeTypes = ['맛집', '숙소', '주차장']

const selectedStadium = computed(() => {
  return stadiums.find((stadium) => stadium.id === selectedStadiumId.value)
})

const directionsUrl = computed(() => {
  if (!selectedStadium.value) return '#'

  const stadium = selectedStadium.value
  const name = encodeURIComponent(stadium.name)
  return `https://map.kakao.com/link/to/${name},${stadium.lat},${stadium.lon}`
})

const formatDistance = (distance) => {
  const meters = Number(distance)

  if (meters >= 1000) return `${(meters / 1000).toFixed(1)}km`

  return `${meters}m`
}

const searchNearbyPlaces = () => {
  if (!selectedStadium.value || !isMapReady.value) {
    nearbyPlaces.value = []
    return
  }

  const kakao = window.kakao

  if (!kakao?.maps?.services) {
    placeError.value = '카카오 장소 검색 서비스를 불러오지 못했습니다.'
    return
  }

  isPlaceLoading.value = true
  placeError.value = ''
  nearbyPlaces.value = []

  const stadium = selectedStadium.value
  const placesService = new kakao.maps.services.Places()
  const keyword = `${stadium.name} ${selectedPlaceType.value}`

  placesService.keywordSearch(
    keyword,
    (result, status) => {
      isPlaceLoading.value = false

      if (status === kakao.maps.services.Status.OK) {
        nearbyPlaces.value = result.slice(0, 6)
        return
      }

      if (status === kakao.maps.services.Status.ZERO_RESULT) {
        placeError.value = '주변 검색 결과가 없습니다.'
        return
      }

      placeError.value = '주변 장소를 검색하지 못했습니다.'
    },
    {
      location: new kakao.maps.LatLng(stadium.lat, stadium.lon),
      radius: 3000,
      size: 6,
      sort: kakao.maps.services.SortBy.DISTANCE,
    },
  )
}

const handleMapReady = () => {
  isMapReady.value = true
  searchNearbyPlaces()
}

watch([selectedStadiumId, selectedPlaceType], searchNearbyPlaces)
</script>

<template>
  <section class="stadium-page">
    <div class="page-heading">
      <h2>구장 가이드</h2>
      <p>전국 9개 KBO 홈구장의 위치와 주변 정보를 확인할 수 있습니다.</p>
    </div>

    <el-card class="map-card" shadow="never">
      <template #header>
        <div class="map-heading">
          <strong>전국 야구장 지도</strong>

          <el-select
            v-model="selectedStadiumId"
            placeholder="구장을 선택해 주세요"
            class="stadium-select"
          >
            <el-option
              v-for="stadium in stadiums"
              :key="stadium.id"
              :label="stadium.name"
              :value="stadium.id"
            />
          </el-select>
        </div>
      </template>

      <KakaoStadiumMap
        :stadiums="stadiums"
        :selected-stadium-id="selectedStadiumId"
        @select="selectedStadiumId = $event.id"
        @ready="handleMapReady"
      />
    </el-card>

    <el-card v-if="selectedStadium" class="nearby-card" shadow="never">
      <template #header>
        <div class="nearby-heading">
          <div>
            <strong>{{ selectedStadium.name }}</strong>
            <p>{{ selectedStadium.homeTeam }} 홈구장</p>
          </div>

          <a :href="directionsUrl" target="_blank" rel="noopener noreferrer">
            <el-button type="primary">구장 길찾기</el-button>
          </a>
        </div>
      </template>

      <p class="nearby-description">
        구장 반경 3km 안의 장소를 가까운 순으로 보여줍니다.
      </p>

      <el-radio-group v-model="selectedPlaceType" class="place-filter">
        <el-radio-button v-for="type in placeTypes" :key="type" :value="type">
          {{ type }}
        </el-radio-button>
      </el-radio-group>

      <div v-if="isPlaceLoading" class="place-loading">
        <el-skeleton :rows="4" animated />
      </div>

      <el-alert
        v-else-if="placeError"
        :title="placeError"
        type="warning"
        :closable="false"
        show-icon
      />

      <div v-else class="place-list">
        <article v-for="place in nearbyPlaces" :key="place.id" class="place-item">
          <div class="place-name-row">
            <strong>{{ place.place_name }}</strong>
            <span>{{ formatDistance(place.distance) }}</span>
          </div>

          <p>{{ place.road_address_name || place.address_name }}</p>
          <small v-if="place.phone">{{ place.phone }}</small>

          <a :href="place.place_url" target="_blank" rel="noopener noreferrer">
            카카오맵 상세 보기
          </a>
        </article>
      </div>
    </el-card>

    <el-alert
      v-else
      class="selection-guide"
      title="지도 마커나 구장 선택 메뉴에서 구장을 선택해 주세요."
      type="info"
      :closable="false"
      show-icon
    />
  </section>
</template>

<style scoped>
.stadium-page {
  padding: 1.5rem;
  border: 1px solid #dfe5ec;
  border-radius: 10px;
  background: #fff;
}

.page-heading h2 {
  margin: 0;
}

.page-heading p,
.nearby-card p {
  margin: 0.4rem 0 0;
  color: #6b7785;
}

.map-card,
.nearby-card,
.selection-guide {
  margin-top: 1rem;
}

.map-heading,
.nearby-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.stadium-select {
  width: 260px;
}

.nearby-description {
  margin: 0 0 1rem;
}

.nearby-heading a,
.place-item a {
  padding: 0;
}

.place-filter {
  margin-bottom: 1rem;
}

.place-loading {
  padding: 0.5rem 0;
}

.place-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.place-item {
  padding: 1rem;
  border: 1px solid #dfe5ec;
  border-radius: 8px;
  background: #fafafa;
}

.place-name-row {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
}

.place-name-row span,
.place-item small {
  color: #8492a6;
}

.place-item p {
  min-height: 2.6em;
  margin: 0.5rem 0;
}

.place-item small,
.place-item a {
  display: block;
}

.place-item a {
  margin-top: 0.75rem;
  color: #409eff;
  font-size: 0.9rem;
}

@media (max-width: 640px) {
  .stadium-page {
    padding: 1rem;
  }

  .map-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .stadium-select,
  .nearby-heading a,
  .nearby-heading .el-button {
    width: 100%;
  }

  .nearby-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .place-list {
    grid-template-columns: 1fr;
  }
}
</style>
