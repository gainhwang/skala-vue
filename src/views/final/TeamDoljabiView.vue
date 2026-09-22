<script setup>
import { computed, ref } from 'vue'
import { useGameStore } from '@/stores/gameStore'
import { getKboApiErrorMessage, recommendTeam } from '@/services/kboApi'

const gameStore = useGameStore()
const preference = ref('')
const recommendation = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')
const savedMessage = ref('')
const resultKey = ref(0)

const examples = [
  '광주에 살고 역사가 깊은 팀이 좋아. 좋아하는 색은 빨강이야.',
  '응원가가 신나고 주변 먹거리까지 즐길 수 있는 구단이 좋아.',
  '비 오는 날에도 편하게 보고 젊은 선수들이 성장하는 팀을 응원하고 싶어.',
]

const teamMascots = [
  { id: 'KIA', name: '호랑이', image: '/mascots/kia.png' },
  { id: 'DOOSAN', name: '곰', image: '/mascots/doosan.png' },
  { id: 'LOTTE', name: '갈매기', image: '/mascots/lotte.png' },
  { id: 'NC', name: '공룡', image: '/mascots/nc.png' },
  { id: 'HANWHA', name: '독수리', image: '/mascots/hanwha.png' },
  { id: 'KIWOOM', name: '영웅', image: '/mascots/kiwoom.png' },
  { id: 'LG', name: '쌍둥이', image: '/mascots/lg.png' },
  { id: 'SSG', name: '강아지', image: '/mascots/ssg.png' },
  { id: 'SAMSUNG', name: '사자', image: '/mascots/samsung.png' },
  { id: 'KT', name: '마법사', image: '/mascots/kt.png' },
]

const spinningMascots = [...teamMascots, ...teamMascots]

const findMascot = (teamId) => {
  return teamMascots.find((mascot) => mascot.id === teamId)
}

const recommendedMascot = computed(() => {
  return findMascot(recommendation.value?.recommended_team_id)
})

const secondChoiceMascot = computed(() => {
  return findMascot(recommendation.value?.second_choice_team_id)
})

const canSubmit = computed(() => {
  return preference.value.trim().length >= 2 && !isLoading.value
})

const chooseExample = (example) => {
  preference.value = example
  errorMessage.value = ''
  savedMessage.value = ''
}

const runDoljabi = async () => {
  if (!canSubmit.value) {
    errorMessage.value = '좋아하는 지역, 색상, 응원 분위기를 조금만 더 알려 주세요.'
    return
  }

  isLoading.value = true
  errorMessage.value = ''
  savedMessage.value = ''
  recommendation.value = null

  try {
    recommendation.value = await recommendTeam(preference.value.trim())
    resultKey.value += 1
  } catch (error) {
    errorMessage.value = getKboApiErrorMessage(
      error,
      '야구팀 돌잡이 결과를 불러오지 못했습니다.',
    )
  } finally {
    isLoading.value = false
  }
}

const saveFavoriteTeam = () => {
  if (!recommendation.value) return

  gameStore.setFavoriteTeam(recommendation.value.recommended_team_id)
  savedMessage.value = `${recommendation.value.recommended_team}를 MY 구단으로 저장했어요!`
}
</script>

<template>
  <section class="doljabi-page">
    <header class="doljabi-hero">
      <span class="hanging-knot knot-left" aria-hidden="true">🎀</span>
      <span class="hanging-knot knot-right" aria-hidden="true">🎀</span>

      <div class="mascot-parade" aria-label="야구팀 돌잡이 캐릭터">
        <img
          v-for="mascot in teamMascots.slice(0, 5)"
          :key="mascot.id"
          :src="mascot.image"
          :alt="`${mascot.name} 캐릭터`"
        />
      </div>

      <p class="eyebrow">오늘 처음 만나는 나의 야구 취향</p>
      <h2>⚾ 야구팀 돌잡이</h2>
      <p class="hero-copy">
        좋아하는 색, 연고지, 응원 분위기를 말해 주세요.<br />
        마스코트들이 나와 꼭 맞는 KBO 구단을 골라 드려요.
      </p>
    </header>

    <div class="doljabi-table">
      <div class="table-decoration" aria-hidden="true">
        <span>⚾</span>
        <span>🎊</span>
        <span>🏟️</span>
      </div>

      <label for="team-preference">나는 이런 야구팀이 좋아요</label>
      <textarea
        id="team-preference"
        v-model="preference"
        maxlength="500"
        placeholder="예: 나는 재밌는 팀이 좋아. 응원가도 즐겁고, 주변에 맛집이 많은 구장을 가진 구단이면 좋겠어!"
        @keydown.ctrl.enter="runDoljabi"
      />

      <div class="input-meta">
        <span>자유롭게 문장으로 적어 주세요.</span>
        <span>{{ preference.length }}/500</span>
      </div>

      <div class="example-area">
        <strong>어떻게 쓸지 고민된다면?</strong>
        <div class="example-chips">
          <button
            v-for="(example, index) in examples"
            :key="example"
            type="button"
            @click="chooseExample(example)"
          >
            예시 {{ index + 1 }}
          </button>
        </div>
      </div>

      <button
        type="button"
        class="pick-button"
        :disabled="!canSubmit"
        @click="runDoljabi"
      >
        <span aria-hidden="true">✨</span>
        {{ isLoading ? '구단을 고르는 중...' : '나의 야구팀 뽑기' }}
        <span aria-hidden="true">✨</span>
      </button>

      <p v-if="errorMessage" class="error-message" role="alert">
        {{ errorMessage }}
      </p>
    </div>

    <div v-if="isLoading" class="pachinko-loading" aria-live="polite">
      <div class="pachinko-machine" aria-hidden="true">
        <div class="machine-sign">TEAM DOLJABI</div>
        <div class="reel-window">
          <div class="reel-pointer reel-pointer-left">▶</div>
          <div class="reel-track">
            <div
              v-for="(mascot, index) in spinningMascots"
              :key="`${mascot.id}-${index}`"
              class="reel-face"
            >
              <img :src="mascot.image" alt="" />
            </div>
          </div>
          <div class="reel-pointer reel-pointer-right">◀</div>
        </div>
        <div class="machine-lights">
          <span v-for="light in 7" :key="light" />
        </div>
      </div>
      <strong>빙글빙글, 운명의 구단을 뽑는 중!</strong>
      <p>어떤 마스코트 앞에서 멈출까요?</p>
    </div>

    <article
      v-else-if="recommendation"
      :key="resultKey"
      class="result-card"
      :style="{ '--team-color': recommendation.color }"
    >
      <div class="result-confetti" aria-hidden="true">✦ · 🎉 · ✦</div>
      <p class="result-label">뾰로롱! 당신이 잡은 야구공은</p>

      <div class="result-team">
        <div class="result-mascot">
          <span class="landed-badge">딱!</span>
          <img
            v-if="recommendedMascot"
            :src="recommendedMascot.image"
            :alt="`${recommendedMascot.name} 캐릭터`"
          />
        </div>
        <div>
          <span>{{ recommendation.title }}</span>
          <h3>{{ recommendation.recommended_team }}</h3>
        </div>
      </div>

      <blockquote>“{{ recommendation.preference_summary }}”</blockquote>

      <div class="reason-list">
        <div
          v-for="(reason, index) in recommendation.reasons"
          :key="reason"
          class="reason-item"
        >
          <span>{{ index + 1 }}</span>
          <p>{{ reason }}</p>
        </div>
      </div>

      <div class="second-choice">
        <img
          v-if="secondChoiceMascot"
          class="second-mascot"
          :src="secondChoiceMascot.image"
          :alt="`${secondChoiceMascot.name} 캐릭터`"
        />
        <div>
          <small>차선으로 잘 맞는 구단</small>
          <strong>{{ recommendation.second_choice_team }}</strong>
          <p>{{ recommendation.second_choice_reason }}</p>
        </div>
      </div>

      <button type="button" class="save-button" @click="saveFavoriteTeam">
        {{ recommendation.recommended_team }}를 MY 구단으로 저장
      </button>
      <p v-if="savedMessage" class="saved-message" role="status">
        🎁 {{ savedMessage }}
      </p>
      <p class="source-note">{{ recommendation.source_note }}</p>
    </article>

    <p class="doljabi-notice">
      야구팀 돌잡이는 구단의 우열을 정하지 않아요. 입력한 취향을 바탕으로 재미있게 추천해 드립니다.
    </p>
  </section>
</template>

<style scoped>
.doljabi-page {
  --cream: #fffaf0;
  --peach: #ffe3d7;
  --pink: #ef7692;
  --deep-pink: #c94c6b;
  --mint: #dcefe7;
  --gold: #dcae55;
  padding: 1.5rem;
  overflow: hidden;
  border: 1px solid #ecd8c3;
  border-radius: 18px;
  background:
    radial-gradient(circle at 8% 12%, #fff0e5 0 5rem, transparent 5.1rem),
    radial-gradient(circle at 92% 10%, #eaf6ee 0 5.5rem, transparent 5.6rem),
    #fffdf9;
}

.doljabi-hero {
  position: relative;
  max-width: 760px;
  padding: 1.5rem 1rem 1rem;
  margin: 0 auto;
  text-align: center;
}

.hanging-knot {
  position: absolute;
  top: -1rem;
  font-size: 2.1rem;
  filter: saturate(0.85);
}

.knot-left {
  left: 0;
  transform: rotate(-12deg);
}

.knot-right {
  right: 0;
  transform: rotate(12deg);
}

.mascot-parade {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 0.15rem;
  margin-bottom: 0.25rem;
}

.mascot-parade img {
  width: clamp(3.6rem, 8vw, 5.3rem);
  aspect-ratio: 1;
  object-fit: contain;
  filter: drop-shadow(0 5px 6px rgb(95 65 35 / 14%));
  animation: mascot-bounce 2.8s ease-in-out infinite;
}

.mascot-parade img:nth-child(2) {
  animation-delay: 0.2s;
}

.mascot-parade img:nth-child(3) {
  animation-delay: 0.4s;
}

.mascot-parade img:nth-child(4) {
  animation-delay: 0.6s;
}

.mascot-parade img:nth-child(5) {
  animation-delay: 0.8s;
}

.eyebrow {
  margin: 0;
  color: var(--deep-pink);
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.12em;
}

.doljabi-hero h2 {
  margin: 0.45rem 0;
  color: #3e3031;
  font-size: clamp(2rem, 5vw, 3.15rem);
}

.hero-copy {
  margin: 0;
  color: #756265;
  font-size: 1.05rem;
  line-height: 1.7;
}

.doljabi-table {
  position: relative;
  max-width: 760px;
  padding: 2rem;
  margin: 1rem auto 2rem;
  border: 1px solid #efd2c5;
  border-radius: 20px;
  background: rgb(255 255 255 / 92%);
  box-shadow: 0 18px 45px rgb(104 74 49 / 10%);
}

.doljabi-table::before {
  position: absolute;
  top: -11px;
  right: 10%;
  left: 10%;
  height: 20px;
  content: '';
  border-radius: 50%;
  background: repeating-linear-gradient(
    90deg,
    var(--peach) 0 34px,
    var(--mint) 34px 68px,
    #fff0bd 68px 102px
  );
  opacity: 0.9;
}

.table-decoration {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin: 0 0 1rem;
  font-size: 1.6rem;
}

.doljabi-table label {
  display: block;
  margin-bottom: 0.7rem;
  color: #493c3d;
  font-size: 1.05rem;
  font-weight: 800;
}

.doljabi-table textarea {
  width: 100%;
  min-height: 138px;
  padding: 1rem 1.1rem;
  resize: vertical;
  color: #3d4148;
  font: inherit;
  line-height: 1.65;
  border: 2px solid #eadbd3;
  border-radius: 14px;
  outline: none;
  background: var(--cream);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.doljabi-table textarea:focus {
  border-color: var(--pink);
  box-shadow: 0 0 0 4px rgb(239 118 146 / 13%);
}

.input-meta {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  color: #9a8887;
  font-size: 0.78rem;
}

.example-area {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1.15rem;
}

.example-area strong {
  color: #776467;
  font-size: 0.88rem;
}

.example-chips {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.4rem;
}

.example-chips button {
  padding: 0.38rem 0.7rem;
  color: #8a5d66;
  font: inherit;
  font-size: 0.78rem;
  cursor: pointer;
  border: 1px solid #efc6cf;
  border-radius: 999px;
  background: #fff5f7;
}

.example-chips button:hover {
  background: #ffe8ed;
}

.pick-button,
.save-button {
  display: block;
  border: 0;
  cursor: pointer;
  font: inherit;
  font-weight: 800;
}

.pick-button {
  width: min(100%, 390px);
  padding: 0.9rem 1.2rem;
  margin: 1.5rem auto 0;
  color: white;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--deep-pink), #e89064);
  box-shadow: 0 8px 18px rgb(201 76 107 / 24%);
  transition: transform 0.2s, box-shadow 0.2s;
}

.pick-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgb(201 76 107 / 28%);
}

.pick-button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.error-message {
  padding: 0.7rem 0.9rem;
  margin: 1rem 0 0;
  color: #a33b4e;
  font-size: 0.9rem;
  text-align: center;
  border-radius: 10px;
  background: #fff0f2;
}

.pachinko-loading {
  max-width: 760px;
  padding: 0 1rem 2rem;
  margin: 0 auto;
  text-align: center;
}

.pachinko-loading strong {
  display: block;
  margin-top: 1.15rem;
  color: #514345;
  font-size: 1.1rem;
}

.pachinko-loading p {
  margin: 0.4rem 0 0;
  color: #988487;
}

.pachinko-machine {
  position: relative;
  width: 250px;
  padding: 1rem 1rem 0.8rem;
  margin: 0 auto;
  border: 4px solid #8f354e;
  border-radius: 30px 30px 22px 22px;
  background: linear-gradient(145deg, #f798a9, #e0637d);
  box-shadow:
    inset 0 0 0 3px rgb(255 255 255 / 28%),
    0 15px 30px rgb(111 61 69 / 22%);
}

.machine-sign {
  padding: 0.35rem 0.55rem;
  margin-bottom: 0.65rem;
  color: #7a3e2e;
  font-size: 0.78rem;
  font-weight: 900;
  letter-spacing: 0.14em;
  border: 2px solid #d39d47;
  border-radius: 999px;
  background: #fff0b8;
}

.reel-window {
  position: relative;
  height: 140px;
  overflow: hidden;
  border: 4px solid #6f2d41;
  border-radius: 18px;
  background: linear-gradient(#f9e9df, white 28%, white 72%, #f9e9df);
  box-shadow: inset 0 7px 13px rgb(75 46 48 / 14%);
}

.reel-window::before,
.reel-window::after {
  position: absolute;
  right: 0;
  left: 0;
  z-index: 2;
  height: 26px;
  pointer-events: none;
  content: '';
}

.reel-window::before {
  top: 0;
  background: linear-gradient(#ead5cf, transparent);
}

.reel-window::after {
  bottom: 0;
  background: linear-gradient(transparent, #ead5cf);
}

.reel-track {
  display: flex;
  align-items: center;
  flex-direction: column;
  animation: reel-spin 0.8s steps(10) infinite;
}

.reel-face {
  width: 124px;
  height: 124px;
  flex: 0 0 124px;
  padding: 4px;
}

.reel-face img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.reel-pointer {
  position: absolute;
  top: 50%;
  z-index: 4;
  color: #f1b949;
  font-size: 1.5rem;
  filter: drop-shadow(0 1px 0 #6f2d41);
  transform: translateY(-50%);
}

.reel-pointer-left {
  left: 4px;
}

.reel-pointer-right {
  right: 4px;
}

.machine-lights {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.7rem;
}

.machine-lights span {
  width: 0.58rem;
  height: 0.58rem;
  border-radius: 50%;
  background: #fff0ae;
  box-shadow: 0 0 8px #fff1a1;
  animation: light-blink 0.65s ease-in-out infinite alternate;
}

.machine-lights span:nth-child(even) {
  animation-delay: 0.3s;
}

.result-card {
  position: relative;
  max-width: 760px;
  padding: 2rem;
  margin: 0 auto 1.5rem;
  overflow: hidden;
  border: 2px solid color-mix(in srgb, var(--team-color) 42%, white);
  border-radius: 22px;
  background: white;
  box-shadow: 0 18px 45px rgb(69 47 39 / 13%);
  animation: result-pop 0.55s cubic-bezier(0.17, 0.89, 0.32, 1.28);
}

.result-card::after {
  position: absolute;
  right: -70px;
  bottom: -80px;
  width: 210px;
  height: 210px;
  content: '';
  border-radius: 50%;
  background: color-mix(in srgb, var(--team-color) 10%, white);
}

.result-confetti,
.result-label {
  text-align: center;
}

.result-confetti {
  color: var(--gold);
  font-size: 1.4rem;
  letter-spacing: 0.2em;
}

.result-label {
  margin: 0.7rem 0 1rem;
  color: #8d7779;
  font-size: 0.9rem;
  font-weight: 700;
}

.result-team {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  text-align: left;
}

.result-mascot {
  position: relative;
  display: grid;
  width: 8rem;
  height: 8rem;
  flex: 0 0 auto;
  place-items: center;
  border: 3px solid color-mix(in srgb, var(--team-color) 35%, white);
  border-radius: 50%;
  background: color-mix(in srgb, var(--team-color) 8%, white);
  box-shadow: 0 9px 20px rgb(47 38 40 / 15%);
}

.result-mascot img {
  width: 108%;
  height: 108%;
  object-fit: contain;
}

.result-mascot .landed-badge {
  position: absolute;
  top: -0.65rem;
  right: -0.75rem;
  z-index: 2;
  display: grid;
  width: 2.7rem;
  height: 2.7rem;
  place-items: center;
  color: #7b382c;
  font-size: 0.85rem;
  font-weight: 900;
  border: 2px solid #d69b3d;
  border-radius: 50%;
  background: #ffe695;
  box-shadow: 0 5px 10px rgb(81 49 43 / 18%);
  animation: landed-pop 0.5s 0.25s both;
}

.result-team span {
  color: #8c7778;
  font-size: 0.85rem;
}

.result-team h3 {
  margin: 0.25rem 0 0;
  color: var(--team-color);
  font-size: clamp(1.75rem, 4vw, 2.45rem);
}

.result-card blockquote {
  padding: 0.9rem 1.1rem;
  margin: 1.5rem 0;
  color: #65575a;
  line-height: 1.6;
  text-align: center;
  border: 0;
  border-radius: 12px;
  background: #faf7f4;
}

.reason-list {
  display: grid;
  gap: 0.65rem;
}

.reason-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.8rem 0.95rem;
  border: 1px solid #eee5df;
  border-radius: 12px;
}

.reason-item > span {
  display: grid;
  width: 1.7rem;
  height: 1.7rem;
  flex: 0 0 auto;
  place-items: center;
  color: white;
  font-size: 0.8rem;
  font-weight: 800;
  border-radius: 50%;
  background: var(--team-color);
}

.reason-item p {
  margin: 0;
  color: #51484a;
  line-height: 1.5;
}

.second-choice {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 1rem;
  margin-top: 1rem;
  border-radius: 14px;
  background: var(--cream);
}

.second-mascot {
  width: 4.2rem;
  height: 4.2rem;
  flex: 0 0 auto;
  object-fit: contain;
}

.second-choice small,
.second-choice strong {
  display: block;
}

.second-choice small {
  color: #a18b8c;
}

.second-choice strong {
  margin-top: 0.15rem;
  color: #514244;
}

.second-choice p {
  margin: 0.25rem 0 0;
  color: #76696b;
  font-size: 0.88rem;
  line-height: 1.5;
}

.save-button {
  position: relative;
  z-index: 1;
  padding: 0.8rem 1.1rem;
  margin: 1.25rem auto 0;
  color: var(--team-color);
  border: 1px solid color-mix(in srgb, var(--team-color) 55%, white);
  border-radius: 999px;
  background: color-mix(in srgb, var(--team-color) 7%, white);
}

.saved-message {
  position: relative;
  z-index: 1;
  margin: 0.8rem 0 0;
  color: #526953;
  font-size: 0.9rem;
  font-weight: 700;
  text-align: center;
}

.source-note,
.doljabi-notice {
  color: #9a8a8b;
  font-size: 0.78rem;
  text-align: center;
}

.source-note {
  position: relative;
  z-index: 1;
  margin: 1rem 0 0;
}

.doljabi-notice {
  margin: 0.8rem auto 0;
}

@keyframes mascot-bounce {
  0%,
  100% {
    transform: translateY(0) rotate(-2deg);
  }

  50% {
    transform: translateY(-5px) rotate(2deg);
  }
}

@keyframes reel-spin {
  from {
    transform: translateY(8px);
  }

  to {
    transform: translateY(-1232px);
  }
}

@keyframes light-blink {
  from {
    opacity: 0.45;
    transform: scale(0.8);
  }

  to {
    opacity: 1;
    transform: scale(1.08);
  }
}

@keyframes landed-pop {
  from {
    opacity: 0;
    transform: rotate(-18deg) scale(0.45);
  }

  to {
    opacity: 1;
    transform: rotate(8deg) scale(1);
  }
}

@keyframes result-pop {
  from {
    opacity: 0;
    transform: translateY(18px) scale(0.96);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@media (max-width: 640px) {
  .doljabi-page {
    padding: 1rem;
    border-radius: 12px;
  }

  .doljabi-table,
  .result-card {
    padding: 1.25rem;
  }

  .hanging-knot {
    display: none;
  }

  .mascot-parade img {
    width: 3.35rem;
  }

  .example-area {
    align-items: flex-start;
    flex-direction: column;
  }

  .example-chips {
    justify-content: flex-start;
  }

  .result-team {
    align-items: center;
    flex-direction: column;
    text-align: center;
  }
}

@media (prefers-reduced-motion: reduce) {
  .mascot-parade img,
  .reel-track,
  .machine-lights span,
  .landed-badge,
  .result-card {
    animation: none;
  }
}
</style>
