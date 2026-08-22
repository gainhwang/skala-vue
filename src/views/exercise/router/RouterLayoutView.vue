<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <section class="router-layout">
    <header class="router-header">
      <h2>날씨 Router 실습</h2>
      <nav class="router-tabs" aria-label="날씨 라우터 메뉴">
        <RouterLink :to="{ name: 'exercise-router-home' }">날씨 홈</RouterLink>
        <RouterLink :to="{ name: 'exercise-router-about' }">소개</RouterLink>
      </nav>
    </header>

    <RouterView />
  </section>
</template>

<style scoped>
.router-header {
  margin-bottom: 1rem;
  text-align: center;
}

.router-header h2 {
  margin-bottom: 0.75rem;
}

.router-tabs {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

.router-tabs a {
  padding: 0.4rem 0.7rem;
  border-radius: 6px;
  background: rgba(66, 184, 131, 0.12);
}

.router-tabs a.router-link-exact-active {
  color: #fff;
  background: #42b883;
}
</style>
