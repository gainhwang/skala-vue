<script setup>
import { computed, ref, watch } from 'vue'
import { useGameStore } from '@/stores/gameStore'

const gameStore = useGameStore()
const youtubeKeyword = ref('')

const teamHomepageUrls = {
  KIA: 'https://tigers.co.kr/',
  SSG: 'https://www.ssglanders.com/',
  KT: 'https://www.ktwiz.co.kr/',
  LG: 'https://www.lgtwins.com/',
  SAMSUNG: 'https://www.samsunglions.com/',
  LOTTE: 'https://www.giantsclub.com/',
  NC: 'https://www.ncdinos.com/',
  DOOSAN: 'https://www.doosanbears.com/',
  HANWHA: 'https://www.hanwhaeagles.co.kr/',
  KIWOOM: 'https://heroesbaseball.co.kr/',
}

const selectedTeamId = computed({
  get: () => gameStore.favoriteTeam,
  set: (teamId) => gameStore.setFavoriteTeam(teamId),
})

const selectedTeam = computed(() => {
  return gameStore.teamOptions.find((team) => team.id === selectedTeamId.value)
})

const favoriteGame = computed(() => gameStore.favoriteGame)

const selectedTeamHomepageUrl = computed(() => {
  return teamHomepageUrls[selectedTeamId.value]
})

const youtubeSearchUrl = computed(() => {
  return `https://www.youtube.com/results?search_query=${encodeURIComponent(youtubeKeyword.value)}`
})

watch(
  selectedTeam,
  (team) => {
    youtubeKeyword.value = team ? `${team.name} 응원가` : ''
  },
  { immediate: true },
)
</script>

<template>
  <section class="favorite-page">
    <div class="page-heading">
      <div>
        <h2>MY 구단</h2>
        <p>선호 구단을 선택하고 오늘 경기에서 응원해 보세요.</p>
      </div>

      <div class="team-selector">
        <span
          v-if="selectedTeam"
          class="team-color-dot"
          :style="{ backgroundColor: selectedTeam.color }"
        />

        <el-select v-model="selectedTeamId" class="team-select">
          <el-option
            v-for="team in gameStore.teamOptions"
            :key="team.id"
            :label="team.name"
            :value="team.id"
          >
            <div class="team-option">
              <span
                class="team-color-dot"
                :style="{ backgroundColor: team.color }"
              />
              <span>{{ team.name }}</span>
            </div>
          </el-option>
        </el-select>
      </div>
    </div>

    <el-card
      v-if="favoriteGame"
      class="favorite-game-card"
      shadow="never"
      :style="{ borderLeftColor: selectedTeam?.color }"
    >
      <template #header>
        <div class="game-heading">
          <div>
            <strong>오늘의 선호 구단 경기</strong>
            <p>{{ favoriteGame.stadiumName }} · {{ favoriteGame.startTime }}</p>
          </div>
        </div>
      </template>

      <div class="cheer-board">
        <article :style="{ borderTopColor: favoriteGame.homeTeam.color }">
          <small>홈</small>
          <strong class="team-name">
            <span
              class="team-color-dot"
              :style="{ backgroundColor: favoriteGame.homeTeam.color }"
            />
            {{ favoriteGame.homeTeam.name }}
          </strong>
          <span :style="{ color: favoriteGame.homeTeam.color }">
            {{ favoriteGame.cheers.home }}
          </span>
          <el-button
            :style="{
              borderColor: favoriteGame.homeTeam.color,
              color: favoriteGame.homeTeam.color,
            }"
            @click="gameStore.cheer(favoriteGame.id, 'home')"
          >
            응원하기
          </el-button>
        </article>

        <div class="vs-text">VS</div>

        <article :style="{ borderTopColor: favoriteGame.awayTeam.color }">
          <small>원정</small>
          <strong class="team-name">
            <span
              class="team-color-dot"
              :style="{ backgroundColor: favoriteGame.awayTeam.color }"
            />
            {{ favoriteGame.awayTeam.name }}
          </strong>
          <span :style="{ color: favoriteGame.awayTeam.color }">
            {{ favoriteGame.cheers.away }}
          </span>
          <el-button
            :style="{
              borderColor: favoriteGame.awayTeam.color,
              color: favoriteGame.awayTeam.color,
            }"
            @click="gameStore.cheer(favoriteGame.id, 'away')"
          >
            응원하기
          </el-button>
        </article>
      </div>

      <p class="local-note">응원 수는 현재 브라우저에서 누른 횟수입니다.</p>
    </el-card>

    <el-row :gutter="16" class="link-grid">
      <el-col :xs="24" :md="12" class="link-column">
        <el-card shadow="never">
          <template #header><strong>응원가 찾기</strong></template>

          <p>검색어를 확인하고 YouTube 검색 결과로 이동할 수 있습니다.</p>

          <el-input v-model="youtubeKeyword" placeholder="구단 응원가 검색">
            <template #append>
              <a
                :href="youtubeSearchUrl"
                target="_blank"
                rel="noopener noreferrer"
              >
                검색
              </a>
            </template>
          </el-input>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12" class="link-column">
        <el-card shadow="never">
          <template #header><strong>경기 관람 링크</strong></template>

          <p>예매 안내와 선택한 구단의 공식 홈페이지를 확인할 수 있습니다.</p>

          <div class="link-actions">
            <a
              href="https://www.koreabaseball.com/Kbo/League/Map.aspx"
              target="_blank"
              rel="noopener noreferrer"
            >
              <el-button>예매 안내</el-button>
            </a>
            <a
              :href="selectedTeamHomepageUrl"
              target="_blank"
              rel="noopener noreferrer"
            >
              <el-button>구단 홈페이지</el-button>
            </a>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </section>
</template>

<style scoped>
.favorite-page {
  padding: 1.5rem;
  border: 1px solid #dfe5ec;
  border-radius: 10px;
  background: #fff;
}

.page-heading,
.game-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.page-heading h2 {
  margin: 0;
}

.page-heading p,
.game-heading p,
.link-column p {
  margin: 0.4rem 0 0;
  color: #6b7785;
}

.team-select {
  width: 220px;
}

.team-selector,
.team-option,
.team-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.team-color-dot {
  width: 0.75rem;
  height: 0.75rem;
  flex: 0 0 auto;
  border-radius: 50%;
}

.favorite-game-card,
.link-grid {
  margin-top: 1rem;
}

.favorite-game-card {
  border-left: 5px solid #409eff;
}

.cheer-board {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 1rem;
  align-items: center;
}

.cheer-board article {
  display: flex;
  align-items: center;
  flex-direction: column;
  gap: 0.65rem;
  padding: 1rem;
  border: 1px solid #dfe5ec;
  border-top: 4px solid #8492a6;
  border-radius: 8px;
  background: #fafafa;
}

.cheer-board small,
.local-note {
  color: #8492a6;
}

.cheer-board span {
  font-size: 1.75rem;
  font-weight: 700;
}

.vs-text {
  font-weight: 700;
  color: #6b7785;
}

.local-note {
  margin: 0.75rem 0 0;
  font-size: 0.85rem;
  text-align: center;
}

.link-column {
  margin-bottom: 1rem;
}

.link-column .el-card {
  height: 100%;
}

.link-column p {
  margin-bottom: 1rem;
}

.link-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.link-actions a,
.el-input a {
  padding: 0;
}

@media (max-width: 640px) {
  .favorite-page {
    padding: 1rem;
  }

  .page-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .team-select {
    width: auto;
    min-width: 0;
    flex: 1;
  }

  .team-selector {
    width: 100%;
  }

  .cheer-board {
    grid-template-columns: 1fr;
  }

  .vs-text {
    text-align: center;
  }
}
</style>
