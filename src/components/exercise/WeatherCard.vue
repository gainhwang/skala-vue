<script setup>
import { computed } from 'vue'
import { useConfigStore } from '../../stores/configStore'

const props = defineProps({
  cityItem: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['select-card', 'click-detail'])

const configStore = useConfigStore()

const displayTemp = computed(() => {
  const rawTemp = props.cityItem.temp

  if (configStore.unit === 'fahrenheit') {
    return Math.round((rawTemp * 9) / 5 + 32)
  }

  return rawTemp
})
</script>

<template>
  <div class="weather-card" @click="emit('select-card', `${cityItem.name}가 선택되었습니다.`)">
    <h4>{{ cityItem.name }} ({{ cityItem.status }})</h4>
    <p>
      현재 기온:
      {{ displayTemp }}{{ configStore.unitSymbol }}
    </p>

    <span v-if="cityItem.temp <= 32" class="badge cool">🍃 폭염주의보 해제</span>
    <span v-else-if="cityItem.temp >= 35" class="heat wave warning">🚨 폭염경보 발령</span>
    <span v-else class="heat wave">🔥 폭염주의보 발령</span>
    <p></p>

    <button
      class="btn-detail"
      @click.stop="emit('click-detail', cityItem.name, cityItem.status)"
      style="border-radius: 10px"
    >
      상세보기
    </button>
  </div>
</template>

<style scoped>
.weather-card {
  padding: 10px;
  margin-top: 10px;
  align-items: center;
  text-align: center;
  color: rgb(6, 4, 4);
  border-radius: 10px;
  background-color: rgba(164, 216, 239, 0.473);
}
</style>
