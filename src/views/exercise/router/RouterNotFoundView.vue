<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="not-found">
    <h3>요청한 날씨 페이지를 찾을 수 없습니다.</h3>
    <RouterLink :to="{ name: 'exercise-router-home' }">날씨 홈으로 돌아가기</RouterLink>
  </div>
</template>

<style scoped>
.not-found {
  padding: 2rem;
  text-align: center;
  border-radius: 10px;
  background: #fff3f3;
}

.not-found h3 {
  margin-bottom: 1rem;
}
</style>
