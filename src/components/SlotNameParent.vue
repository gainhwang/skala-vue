<script setup>
import SlotNameChild from './SlotNameChild.vue'
</script>

<template>
  <div class="practice-section">
    <h2>Named Slot 주입 실습</h2>
    <SlotNameChild>
      <template v-slot:header>
        <h3>Child 주입 제목</h3>
      </template>
      <p>"dddddd"</p>
    </SlotNameChild>
  </div>
</template>
