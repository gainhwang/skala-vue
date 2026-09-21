<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  fetchYesterdayBriefing,
  getKboApiErrorMessage,
} from '@/services/kboApi'

const briefing = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')

const briefingDate = computed(() => {
  if (!briefing.value?.date) return ''

  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'short',
  }).format(new Date(`${briefing.value.date}T00:00:00`))
})

const loadBriefing = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    briefing.value = await fetchYesterdayBriefing()
  } catch (error) {
    errorMessage.value = getKboApiErrorMessage(
      error,
      '어제의 AI 경기 브리핑을 불러오지 못했습니다.',
    )
  } finally {
    isLoading.value = false
  }
}

onMounted(loadBriefing)
</script>

<template>
  <el-card class="briefing-card" shadow="never">
    <template #header>
      <div class="briefing-heading">
        <div>
          <div class="title-line">
            <h2>AI KBO 모닝 브리핑</h2>
            <el-tag type="success" effect="dark" size="small">LangChain</el-tag>
          </div>
          <p>어제의 공식 경기 기록을 AI가 간단히 정리해 드립니다.</p>
        </div>

        <el-button :loading="isLoading" @click="loadBriefing">다시 생성</el-button>
      </div>
    </template>

    <el-skeleton v-if="isLoading" :rows="5" animated />

    <el-alert
      v-else-if="errorMessage"
      :title="errorMessage"
      type="error"
      :closable="false"
      show-icon
    />

    <template v-else-if="briefing">
      <el-empty
        v-if="briefing.total_games === 0"
        description="어제 완료된 KBO 경기가 없습니다."
      />

      <template v-else>
        <div class="ai-summary">
          <div class="summary-meta">
            <el-tag type="info" effect="plain">{{ briefingDate }}</el-tag>
            <span>{{ briefing.total_games }}경기</span>
          </div>
          <h3>{{ briefing.headline }}</h3>
          <p>{{ briefing.summary }}</p>
        </div>

        <div class="result-grid">
          <article v-for="game in briefing.games" :key="game.id" class="result-item">
            <div class="score-line">
              <span>{{ game.away_team }}</span>
              <strong>{{ game.away_score }} : {{ game.home_score }}</strong>
              <span>{{ game.home_team }}</span>
            </div>

            <div class="record-list">
              <span><b>승리투수</b> {{ game.winning_pitcher || '기록 없음' }}</span>
              <span><b>패전투수</b> {{ game.losing_pitcher || '기록 없음' }}</span>
              <span v-if="game.save_pitcher"><b>세이브</b> {{ game.save_pitcher }}</span>
              <span v-if="game.winning_hit"><b>결승타</b> {{ game.winning_hit }}</span>
            </div>
          </article>
        </div>

        <p class="source-note">{{ briefing.source_note }}</p>
      </template>
    </template>
  </el-card>
</template>

<style scoped>
.briefing-card {
  border-color: #cfe1ff;
  background: linear-gradient(135deg, #f5f9ff 0%, #ffffff 65%);
}

.briefing-heading,
.title-line,
.summary-meta,
.score-line {
  display: flex;
  align-items: center;
}

.briefing-heading {
  justify-content: space-between;
  gap: 1rem;
}

.title-line {
  gap: 0.6rem;
}

.title-line h2,
.ai-summary h3 {
  margin: 0;
}

.briefing-heading p,
.ai-summary p {
  margin: 0.45rem 0 0;
  line-height: 1.65;
  color: #526273;
}

.summary-meta {
  gap: 0.65rem;
  margin-bottom: 0.75rem;
  color: #6b7785;
  font-size: 0.9rem;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
  margin-top: 1.25rem;
}

.result-item {
  padding: 1rem;
  border: 1px solid #dfe8f5;
  border-radius: 8px;
  background: rgb(255 255 255 / 88%);
}

.score-line {
  justify-content: space-between;
  gap: 0.75rem;
}

.score-line span {
  flex: 1;
  font-weight: 600;
}

.score-line span:last-child {
  text-align: right;
}

.score-line strong {
  flex: 0 0 auto;
  color: #245da8;
  font-size: 1.1rem;
}

.record-list {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding-top: 0.75rem;
  margin-top: 0.75rem;
  color: #596b7e;
  font-size: 0.86rem;
  border-top: 1px solid #edf1f6;
}

.record-list b {
  margin-right: 0.35rem;
  color: #34495e;
}

.source-note {
  margin: 1rem 0 0;
  color: #8492a6;
  font-size: 0.8rem;
  text-align: right;
}

@media (max-width: 720px) {
  .briefing-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .result-grid {
    grid-template-columns: 1fr;
  }
}
</style>
