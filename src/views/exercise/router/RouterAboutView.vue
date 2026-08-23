<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <article class="info-card">
    <h3>Router 실습 소개</h3>
    <p>
      이 화면은 중첩 라우트로 렌더링됩니다. 날씨 홈과 소개 화면은 같은 Router 레이아웃을
      공유합니다.
    </p>

    <RouterLink :to="{ name: 'exercise-router-home' }">
      메인 날씨 대시보드로 돌아가기
    </RouterLink>
  </article>
</template>

<style scoped>
.info-card {
  padding: 1.5rem;
  text-align: center;
  border-radius: 10px;
  background: rgba(164, 216, 239, 0.5);
}

.info-card h3 {
  margin-bottom: 0.75rem;
}

.info-card a {
  display: inline-block;
  margin-top: 1rem;
}
</style>
