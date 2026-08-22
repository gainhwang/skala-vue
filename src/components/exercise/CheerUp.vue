<script setup>
import { ref } from 'vue'

const count = ref(0)
</script>

<template>
  <div class="cheerup">
    <h3>❤️‍🔥 응원하기 ❤️‍🔥</h3>
    <h4>승리 기운: {{ count }}</h4>
    <button @click="count++" style="border-radius: 10px">승리 버튼</button>
  </div>
</template>

<style scoped>
.cheerup {
  padding: 10px;
  margin-top: 10px;
  align-items: center;
  text-align: center;
  color: rgb(6, 4, 4);
  border-radius: 10px;
  background-color: rgba(255, 0, 221, 0.16);
}
</style>
