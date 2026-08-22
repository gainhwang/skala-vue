<script setup>
import WeatherParent from '@/components/exercise/WeatherParent.vue'
</script>

<template>
  <div>
    <p class="route-guide">상세보기 버튼을 누르면 해당 구장의 라우트로 이동합니다.</p>
    <WeatherParent details-as-route />
  </div>
</template>

<style scoped>
.route-guide {
  margin-bottom: 1rem;
  text-align: center;
  color: #52606d;
}
</style>
