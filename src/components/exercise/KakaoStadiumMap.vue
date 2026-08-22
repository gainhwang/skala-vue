<script setup>
import { onMounted, ref, watch } from 'vue'

const props = defineProps({
  stadiums: {
    type: Array,
    required: true,
  },
  selectedStadiumId: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['select', 'ready'])

const mapContainer = ref(null)
const mapError = ref('')
let map = null
const markerRecords = new Map()

const loadKakaoMap = () => {
  return new Promise((resolve, reject) => {
    const appKey = import.meta.env.VITE_KAKAO_MAP_KEY

    if (!appKey) {
      reject(new Error('카카오맵 JavaScript 키가 없습니다.'))
      return
    }

    if (window.kakao?.maps?.services) {
      window.kakao.maps.load(resolve)
      return
    }

    const script = document.createElement('script')

    script.src =
      `https://dapi.kakao.com/v2/maps/sdk.js` +
      `?appkey=${appKey}&autoload=false&libraries=services`

    script.onload = () => {
      window.kakao.maps.load(resolve)
    }

    script.onerror = () => {
      reject(new Error('카카오맵을 불러오지 못했습니다.'))
    }

    document.head.appendChild(script)
  })
}

const focusStadium = (stadiumId) => {
  const record = markerRecords.get(stadiumId)

  if (!map || !record) return

  map.setCenter(record.position)
  map.setLevel(4)
  record.infoWindow.open(map, record.marker)
}

const createMap = () => {
  const kakao = window.kakao

  map = new kakao.maps.Map(mapContainer.value, {
    center: new kakao.maps.LatLng(36.2, 127.8),
    level: 13,
  })

  const bounds = new kakao.maps.LatLngBounds()

  props.stadiums.forEach((stadium) => {
    const position = new kakao.maps.LatLng(stadium.lat, stadium.lon)

    const marker = new kakao.maps.Marker({
      map,
      position,
    })

    const infoWindow = new kakao.maps.InfoWindow({
      content: `
        <div class="kakao-info-window">
          <strong>${stadium.name}</strong><br>
          <span>${stadium.homeTeam} 홈구장</span>
        </div>
      `,
    })

    kakao.maps.event.addListener(marker, 'click', () => {
      infoWindow.open(map, marker)
      emit('select', stadium)
    })

    markerRecords.set(stadium.id, {
      marker,
      infoWindow,
      position,
    })

    bounds.extend(position)
  })

  if (props.stadiums.length === 1) {
    map.setCenter(
      new kakao.maps.LatLng(props.stadiums[0].lat, props.stadiums[0].lon),
    )
    map.setLevel(4)
  } else {
    map.setBounds(bounds)
  }

  if (props.selectedStadiumId) {
    focusStadium(props.selectedStadiumId)
  }

  emit('ready')
}

onMounted(async () => {
  try {
    await loadKakaoMap()
    createMap()
  } catch (error) {
    mapError.value = error.message
  }
})

watch(
  () => props.selectedStadiumId,
  (stadiumId) => {
    if (stadiumId) focusStadium(stadiumId)
  },
)
</script>

<template>
  <div class="stadium-map-wrapper">
    <div ref="mapContainer" class="stadium-map"></div>

    <p v-if="mapError" class="map-error">
      {{ mapError }}
    </p>
  </div>
</template>

<style>
.stadium-map-wrapper {
  width: 100%;
}

.stadium-map {
  width: 100%;
  height: 420px;
  border-radius: 16px;
}

.kakao-info-window {
  min-width: 170px;
  padding: 12px;
  color: #26364a;
  line-height: 1.6;
  text-align: center;
}

.map-error {
  padding: 1rem;
  color: #d03050;
  text-align: center;
}
</style>
