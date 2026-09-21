# KBO Morning Briefing AI Service

KBO 공식 사이트에서 오늘의 경기 일정과 직전 완료 경기 결과를 가져오는 FastAPI 서비스입니다. 직전 경기일의 결과는 LangChain과 OpenAI를 통해 경기별 한국어 모닝 브리핑으로 요약합니다.

수업 예제와 동일하게 `init_chat_model`, `ChatPromptTemplate`, `with_structured_output()`을 사용하며, 프롬프트와 모델을 `|` 연산자로 연결하는 LCEL 체인으로 구성했습니다.

## 제공 기능

- 오늘의 실제 KBO 경기 일정, 시간, 구장, 상태, 점수와 선발투수 조회
- 어제부터 최대 14일 전까지 탐색해 가장 최근에 종료된 경기일 조회
- 최종 점수, 승리·패전·세이브투수와 결승타 조회
- 공식 경기 기록만 사용하도록 제한한 경기별 한국어 AI 브리핑 생성
- Pydantic 기반 구조화 출력으로 `headline`, `game_briefings` 형식 고정

## 환경 설정

```bash
cd ai-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env`에 발급받은 OpenAI API 키를 입력합니다. 실제 `.env` 파일은 Git에 커밋하지 않습니다.

```env
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini
FRONTEND_ORIGIN=http://localhost:5173
```

## 실행

```bash
uvicorn app.main:app --reload --port 8000
```

- 상태 확인: `http://localhost:8000/health`
- Swagger UI: `http://localhost:8000/docs`

## 오늘의 경기 요청

기본값은 한국 시간 기준 오늘입니다.

```bash
curl http://localhost:8000/api/games/today
```

원하는 날짜를 `YYYY-MM-DD` 형식으로 지정할 수도 있습니다.

```bash
curl 'http://localhost:8000/api/games/today?date=2026-09-20'
```

## 브리핑 요청

날짜를 생략하면 한국 시간 기준 어제부터 최대 14일 전까지 확인하여 가장 최근에 완료된 경기일을 사용합니다. 빈 날짜를 확인할 때는 OpenAI를 호출하지 않고, 경기일을 찾은 뒤 한 번만 호출합니다.

```bash
curl -X POST http://localhost:8000/api/briefings/latest
```

재현할 날짜를 직접 지정하면 직전 경기일 탐색 없이 해당 날짜만 사용합니다.

```bash
curl -X POST 'http://localhost:8000/api/briefings/latest?date=2026-09-20'
```

브리핑 API를 호출하려면 `.env`에 유효한 `OPENAI_API_KEY`가 있어야 합니다. 경기 데이터 조회에 실패하면 `502`, API 키가 없으면 `503` 응답을 반환합니다.

## 데이터 사용 시 주의사항

- 경기 데이터는 KBO 공식 웹사이트가 화면에 사용하는 내부 요청에서 가져옵니다.
- 별도의 공개 개발자 API가 아니므로 주소나 응답 형식이 바뀌면 코드 수정이 필요할 수 있습니다.
- 과도하게 반복 호출하지 않고, AI가 경기 기록에 없는 내용을 추측하지 않도록 프롬프트에서 제한합니다.
- `.env`와 실제 OpenAI API 키는 Git에 커밋하지 않습니다.
