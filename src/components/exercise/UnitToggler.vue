<script setup>
import { useConfigStore } from '../../stores/configStore'

const configStore = useConfigStore()
</script>

<template>
  <div class="unit-toggler">
    <span>
      날씨 단위:
      {{ configStore.unit === 'celsius' ? '섭씨' : '화씨' }}
      ({{ configStore.unitSymbol }})
    </span>

    <button @click="configStore.toggleUnit">단위 변경</button>
  </div>
</template>

<style scoped>
.unit-toggler {
  display: flex;
  align-items: center;
  gap: 10px;
}

button {
  padding: 6px 12px;
  cursor: pointer;
}
</style>
