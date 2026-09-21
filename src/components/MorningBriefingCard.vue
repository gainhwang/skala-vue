<script setup>
import { computed, onMounted, ref } from 'vue'
import { teams } from '@/data/teams'
import { fetchLatestBriefing, getKboApiErrorMessage } from '@/services/kboApi'

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

const isWinner = (game, teamName) => game.winner === teamName

const hexToRgba = (hex, alpha) => {
  const value = hex.replace('#', '')
  const red = Number.parseInt(value.slice(0, 2), 16)
  const green = Number.parseInt(value.slice(2, 4), 16)
  const blue = Number.parseInt(value.slice(4, 6), 16)

  return `rgba(${red}, ${green}, ${blue}, ${alpha})`
}

const getWinnerStyle = (game, teamName) => {
  if (!isWinner(game, teamName)) return undefined

  const team = teams.find((item) => item.name === teamName)
  if (!team) return undefined

  return {
    color: team.color,
    backgroundColor: hexToRgba(team.color, 0.12),
    borderColor: hexToRgba(team.color, 0.38),
  }
}

const loadBriefing = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    briefing.value = await fetchLatestBriefing()
  } catch (error) {
    errorMessage.value = getKboApiErrorMessage(
      error,
      '직전 경기의 AI 브리핑을 불러오지 못했습니다.',
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
          <p>가장 최근에 완료된 공식 경기 기록을 AI가 경기별로 정리합니다.</p>
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
        description="최근 완료된 KBO 경기를 찾지 못했습니다."
      />

      <template v-else>
        <div class="ai-summary">
          <div class="summary-meta">
            <el-tag type="info" effect="plain">{{ briefingDate }}</el-tag>
            <span>{{ briefing.total_games }}경기</span>
          </div>
          <h3>{{ briefing.headline }}</h3>
        </div>

        <div class="result-grid">
          <article v-for="game in briefing.games" :key="game.id" class="result-item">
            <div class="score-line">
              <span
                class="team-name"
                :class="{ 'is-winner': isWinner(game, game.away_team) }"
                :style="getWinnerStyle(game, game.away_team)"
              >
                <small v-if="isWinner(game, game.away_team)">승</small>
                {{ game.away_team }}
              </span>
              <strong>{{ game.away_score }} : {{ game.home_score }}</strong>
              <span
                class="team-name home-team"
                :class="{ 'is-winner': isWinner(game, game.home_team) }"
                :style="getWinnerStyle(game, game.home_team)"
              >
                {{ game.home_team }}
                <small v-if="isWinner(game, game.home_team)">승</small>
              </span>
            </div>

            <div class="record-list">
              <span><b>승리투수</b> {{ game.winning_pitcher || '기록 없음' }}</span>
              <span><b>패전투수</b> {{ game.losing_pitcher || '기록 없음' }}</span>
              <span v-if="game.save_pitcher"><b>세이브</b> {{ game.save_pitcher }}</span>
              <span v-if="game.winning_hit"><b>결승타</b> {{ game.winning_hit }}</span>
            </div>

            <p class="game-summary">
              <b>AI 브리핑</b>
              {{ game.ai_summary }}
            </p>
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

.briefing-heading p {
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

.team-name {
  flex: 1;
  padding: 0.45rem 0.55rem;
  border: 1px solid transparent;
  border-radius: 6px;
  font-weight: 600;
}

.team-name.home-team {
  text-align: right;
}

.team-name.is-winner {
  font-weight: 700;
}

.team-name small {
  margin-right: 0.25rem;
  font-size: 0.68rem;
}

.team-name.home-team small {
  margin-right: 0;
  margin-left: 0.25rem;
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

.game-summary {
  padding: 0.75rem;
  margin: 0.85rem 0 0;
  color: #42566c;
  font-size: 0.86rem;
  line-height: 1.55;
  background: #f4f7fb;
  border-radius: 6px;
}

.game-summary b {
  display: block;
  margin-bottom: 0.25rem;
  color: #245da8;
  font-size: 0.76rem;
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
