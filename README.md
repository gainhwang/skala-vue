# KBO 야구장 직관 날씨 & AI 모닝 브리핑

KBO 경기 관람 전에 오늘의 실제 경기 일정, 구장 날씨, 대기질과 준비물을 한 번에 확인하는 Vue 3 프로젝트입니다. FastAPI와 LangChain을 연결해 전날 경기 결과를 한국어 모닝 브리핑으로 요약하는 AI 기능도 제공합니다. 수업 과제를 단계별로 보관하면서, 각 단계에서 학습한 기능을 하나의 최종 서비스로 통합했습니다.

- GitHub: https://github.com/gainhwang/skala-vue
- 배포 주소: https://skala-vue-tan.vercel.app/

## 주요 기능

### 오늘의 경기

- KBO 공식 사이트 데이터로 당일 경기 일정 조회
- 홈·원정 구단, 경기 시간, 구장, 경기 상태, 선발투수와 점수 표시
- 경기가 없는 날에는 빈 경기 안내 표시
- 각 구단의 상징색 표시
- OpenWeatherMap으로 경기 구장의 현재 날씨 조회
- 경기 카드를 선택하면 구장별 상세 페이지로 이동

### AI KBO 모닝 브리핑

- 전날 종료된 KBO 경기의 최종 점수와 승리팀 표시
- 승리투수, 패전투수, 세이브투수와 결승타 기록 표시
- LangChain과 OpenAI를 이용해 전체 경기 결과를 짧은 제목과 3~5문장의 한국어 브리핑으로 생성
- 구조화 출력으로 제목과 요약의 응답 형식을 고정
- 공식 경기 기록에 없는 선수나 상황을 추측하지 않도록 프롬프트에 제한 조건 적용

### 경기 상세 정보

- 현재 날씨와 체감 온도, 습도, 풍속 표시
- OpenWeatherMap의 3시간 단위 예보 중 현재부터 약 3시간 뒤에 가까운 데이터 표시
- Open-Meteo를 이용한 PM10, PM2.5, 대기질 지수 표시
- 비, 더위, 대기질, 강풍, 추위를 기준으로 관람 안내 제공
- 날씨에 따른 준비물 추천과 개인 준비물 추가·삭제·체크
- 경기별 개인 준비물과 체크 상태를 `localStorage`에 저장
- 카카오맵 구장 위치와 길찾기 제공

### 구장 가이드

- 전국 9개 KBO 홈구장 마커 표시
- 선택한 구장 반경 3km 안의 맛집, 숙소, 주차장 검색
- 가까운 장소부터 최대 6개 표시
- 카카오맵 장소 상세 정보 및 구장 길찾기 제공

### MY 구단

- 10개 구단 중 선호 구단 선택 및 브라우저 저장
- 선택한 구단의 실제 당일 경기와 응원 대결 표시
- 구단 응원가 YouTube 검색
- KBO 예매 안내와 각 구단 공식 홈페이지 연결

## 과제 요구사항 충족 현황

강의 자료의 과제 페이지(116, 145, 178, 196, 212, 230, 249, 274쪽)를 기준으로 확인했습니다.

### 1. Mockup - 완료

- 요구사항: `v-for`, 고유 `:key`, 조건부 렌더링, `:value`와 `@input`, 클릭 이벤트와 `.stop`, 추가 데이터
- 구현 내용: 구장 날씨 반복 출력, 폭염 단계 표시, 한글 검색어 출력, 카드 선택 및 상세 알림, 응원 카운트

### 2. Composition API - 완료

- 요구사항: `ref`, `computed`, `watch`, `watchEffect`, 검색 결과 분기, 추가 반응형 기능
- 구현 내용: 검색 필터, 선택 문구 감시, 검색어 감시, 빈 결과 안내, 응원 메시지 computed와 count watcher

### 3. Components - 완료

- 요구사항: 4개 컴포넌트 분리, Slot, Props, Emits, scoped style, 추가 컴포넌트
- 구현 내용: `WeatherParent`, `BaseDashboardCard`, `SearchBar`, `WeatherCard`와 추가 `CheerUp` 컴포넌트

### 4. Router - 완료

- 요구사항: Lazy Loading, Catch-all, `RouterLink`, `RouterView`, `router.push`, 동적 경로, 소개·추가 View
- 구현 내용: 중첩 라우팅, `:cityId`, Mount 시점 Mock Data 선택, Not Found, 공통 Router Layout

### 5. Pinia - 완료

- 요구사항: 단위 state/getter/action, UnitToggler, 메인·상세 단위 변환, 추가 Store
- 구현 내용: `configStore`, Navigation 옆 UnitToggler, `WeatherCard`·상세 화면 변환, `gameStore`·`preparationStore`

### 6. Axios - 완료

- 요구사항: Axios 설치, 실제 날씨, OpenWeather 추가 API, 외부 API
- 구현 내용: OpenWeather 현재 날씨와 예보, Open-Meteo 대기질, 로딩·오류 처리

### 7. UI Library - 완료

- 요구사항: 외부 UI Library 적용
- 구현 내용: Element Plus의 Card, Button, Select, Alert, Progress, Skeleton 등을 최종 화면에 적용

### 8. Build & Deployment - Hosting 전

- 요구사항: ESLint 오류 제거, API 키 환경변수화·Git 제외, Build, Hosting
- 구현 내용: ESLint·Build 통과, `.env.local` Git 제외, Vercel SPA rewrite 설정

### 9. LangChain AI - 완료

- KBO 공식 경기 데이터를 가져오는 FastAPI 백엔드 구현
- `ChatPromptTemplate`, `init_chat_model`, `with_structured_output()`과 LCEL 체인 사용
- 전날 경기 결과를 근거로 한 AI 모닝 브리핑 API와 Vue 화면 구현
- 실행 결과가 저장된 제출용 Jupyter Notebook 작성

이전 단계별 결과는 `/exercise` 아래에서 확인할 수 있고, 최종 통합 화면은 `/`에서 시작합니다.

## 기술 스택

- Vue 3 Composition API
- Vite
- Vue Router
- Pinia
- Axios
- Element Plus
- Python / FastAPI
- LangChain / OpenAI API
- KBO 공식 경기 데이터
- OpenWeatherMap API
- Open-Meteo Air Quality API
- Kakao Maps JavaScript API 및 Places 서비스

## 주요 경로

| URL                     | 화면                       |
| ----------------------- | -------------------------- |
| `/`                     | 오늘의 경기                |
| `/game/:gameId`         | 경기 구장 날씨 상세        |
| `/stadiums`             | 전국 구장 지도와 주변 장소 |
| `/favorite`             | MY 구단과 응원 기능        |
| `/exercise/mockup`      | 1단계 Mockup 과제          |
| `/exercise/composition` | 2단계 Composition API 과제 |
| `/exercise/component`   | 3단계 Components 과제      |
| `/exercise/router`      | 4단계 Router 과제          |
| `/exercise/store`       | 5단계 Pinia Store 과제     |
| `/exercise/axios`       | 6단계 Axios 과제           |

## 프로젝트 구조

```text
ai-service/
├── app/main.py            # KBO 데이터 조회와 LangChain 브리핑 API
└── requirements.txt       # Python 패키지 목록
notebooks/
└── KBO_LangChain_Morning_Briefing.ipynb  # 실행 결과가 포함된 제출용 노트북
src/
├── components/            # AI 브리핑 카드와 단계별 재사용 컴포넌트
├── data/                  # KBO 구장·구단 정보
├── router/                # 최종 화면과 과제 화면 라우팅
├── services/              # KBO AI API와 날씨·대기질 요청 함수
├── stores/                # 단위, 경기, 준비물 Pinia Store
└── views/
    ├── exercise/          # 1~6단계 과제 화면
    └── final/             # 최종 UI 화면
```

## 실행 방법

### 1. 요구 환경

- Node.js `20.19.0` 이상 또는 `22.12.0` 이상
- npm
- Python 3.11 이상

### 2. 패키지 설치

```sh
npm install
```

### 3. 환경변수 설정

`.env.example`을 복사해 프로젝트 루트에 `.env.local`을 만듭니다.

```sh
cp .env.example .env.local
```

발급받은 키를 입력합니다.

```env
VITE_OPENWEATHER_API_KEY=발급받은_OpenWeather_API_KEY
VITE_OPENWEATHER_BASE_URL=https://api.openweathermap.org/data/2.5
VITE_KAKAO_MAP_KEY=발급받은_카카오_JavaScript_KEY
VITE_AI_API_BASE_URL=http://localhost:8000
```

`.env.local`은 `.gitignore`의 `*.local` 규칙으로 Git에 업로드되지 않습니다.

### 4. AI 서버 설치와 환경변수 설정

```sh
cd ai-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`ai-service/.env`에 수업에서 발급받은 OpenAI API 키를 입력합니다.

```env
OPENAI_API_KEY=발급받은_sk-proj_키
OPENAI_MODEL=gpt-4o-mini
FRONTEND_ORIGIN=http://localhost:5173
```

`ai-service/.env`도 Git에 업로드되지 않습니다. API 키는 README, 소스 코드, Notebook에 직접 적지 않습니다.

### 5. 개발 서버 실행

터미널을 두 개 열어 AI 서버와 Vue 개발 서버를 각각 실행합니다.

터미널 1 - AI 서버:

```sh
cd ai-service
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

터미널 2 - Vue:

```sh
npm run dev
```

브라우저에서 `http://localhost:5173`을 열고, AI API 문서는 `http://localhost:8000/docs`에서 확인합니다.

### 6. 코드 검사와 빌드

```sh
npm run lint
npm run build
npm run preview
```

## 배포 방법

1. GitHub 저장소를 Vercel에 연결합니다.
2. Vercel 프로젝트 환경변수에 아래 값을 등록합니다.
   - `VITE_OPENWEATHER_API_KEY`
   - `VITE_OPENWEATHER_BASE_URL`
   - `VITE_KAKAO_MAP_KEY`
   - `VITE_AI_API_BASE_URL` (별도로 배포한 FastAPI 서버 주소)
3. Build Command는 `npm run build`, Output Directory는 `dist`로 설정합니다.
4. 배포된 도메인을 카카오 디벨로퍼스의 JavaScript SDK 도메인에 추가합니다.
5. 배포 화면의 새로고침과 동적 경로 접근을 확인합니다. `vercel.json`에 SPA rewrite가 설정되어 있습니다.
6. 이 README 상단의 배포 주소를 실제 URL로 교체합니다.

Vue와 FastAPI는 별도의 서버입니다. AI 기능까지 배포하려면 FastAPI 서버를 배포한 뒤 프론트엔드의 `VITE_AI_API_BASE_URL`을 해당 주소로 설정해야 합니다. 로컬 시연에서는 위의 두 터미널 실행 방법을 사용하면 됩니다.

## Notebook 제출

제출 파일은 [`notebooks/KBO_LangChain_Morning_Briefing.ipynb`](notebooks/KBO_LangChain_Morning_Briefing.ipynb)입니다. 재현 가능한 경기 날짜의 KBO 데이터 조회 결과와 LangChain AI 응답이 셀 출력으로 저장되어 있습니다. OpenAI API 키는 저장되어 있지 않으며, 다시 실행할 때 환경변수 또는 숨김 입력으로 받습니다.

## 데이터 및 기능 범위

- 날씨와 대기질은 외부 API의 실제 데이터를 사용합니다.
- 오늘의 경기와 전날 경기 결과는 KBO 공식 사이트의 경기 데이터를 사용합니다.
- KBO 웹사이트 내부 API는 별도의 공개 개발자 API가 아니므로 응답 형식이나 주소가 바뀌면 연동 코드 수정이 필요할 수 있습니다.
- AI는 수집한 경기 기록을 요약하며, 실시간 중계나 경기 결과 자체를 생성하지 않습니다.
- 응원 횟수는 현재 페이지의 Pinia 상태이므로 새로고침하면 초기화됩니다.
- 선호 구단과 개인 준비물은 브라우저 `localStorage`에 저장됩니다.
- 주변 장소는 카카오맵의 거리순 검색 결과이며 별점 기반 추천이 아닙니다.
