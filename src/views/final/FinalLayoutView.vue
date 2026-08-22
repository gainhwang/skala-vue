<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="final-layout">
    <header class="service-header">
      <div class="service-title">
        <h1>⚾ 야구장 직관 가이드</h1>
        <p>경기와 날씨를 확인하고 필요한 준비물을 챙겨 보세요.</p>
      </div>

      <nav class="service-nav" aria-label="최종 프로젝트 메뉴">
        <RouterLink :to="{ name: 'weather-final' }">오늘의 경기</RouterLink>
        <RouterLink :to="{ name: 'final-stadiums' }">구장 가이드</RouterLink>
        <RouterLink :to="{ name: 'final-favorite' }">MY 구단</RouterLink>
        <RouterLink class="exercise-link" to="/exercise">이전 과제</RouterLink>
      </nav>
    </header>

    <main class="service-content">
      <RouterView />
    </main>

    <footer class="service-footer">
      OpenWeather 날씨·예보 API · Open-Meteo 대기질 API · Kakao Maps API
    </footer>
  </div>
</template>

<style scoped>
.final-layout {
  width: min(100%, 1120px);
  margin: 0 auto;
  color: #25364a;
}

.service-header {
  padding: 1.5rem;
  border: 1px solid #dfe5ec;
  border-radius: 10px;
  background: #fff;
}

.service-title h1 {
  margin: 0;
  font-size: 1.75rem;
}

.service-title p {
  margin: 0.5rem 0 0;
  color: #6b7785;
}

.service-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1.25rem;
}

.service-nav a {
  padding: 0.55rem 0.85rem;
  color: #34495e;
  border: 1px solid #d7dee8;
  border-radius: 6px;
  background: #fff;
}

.service-nav a:hover {
  background: #f5f7fa;
}

.service-nav a.router-link-exact-active:not(.exercise-link) {
  color: #fff;
  border-color: #409eff;
  background: #409eff;
}

.exercise-link {
  margin-left: auto;
}

.service-content {
  margin-top: 1rem;
}

.service-footer {
  padding: 1.5rem 0;
  margin-top: 1.5rem;
  color: #8492a6;
  font-size: 0.85rem;
  text-align: center;
  border-top: 1px solid #e4e7ed;
}

@media (max-width: 640px) {
  .service-header {
    padding: 1rem;
  }

  .service-nav a {
    flex: 1 1 40%;
    text-align: center;
  }

  .exercise-link {
    margin-left: 0;
  }
}
</style>
