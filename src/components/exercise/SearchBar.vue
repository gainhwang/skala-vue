<script setup>
defineEmits(['update-query'])

defineProps({
  currentQuery: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <div class="search-inner">
    <section class="search-box">
      <h2>🔍 구장 검색</h2>
      <input
        type="text"
        :value="currentQuery"
        @input="$emit('update-query', $event.target.value)"
        placeholder="검색할 구장 이름 입력"
      />
      <p>
        검색 중인 구장: <strong>{{ currentQuery }}</strong>
      </p>
    </section>
  </div>
</template>
<style scoped>
.search-inner {
  padding: 10px;
  margin-top: 20px;
  color: rgb(6, 4, 4);
  border-radius: 10px;
  background-color: rgb(251, 245, 198);
}
</style>
