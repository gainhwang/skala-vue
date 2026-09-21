# KBO Morning Briefing AI Service

TheSportsDB에서 전날 KBO 경기 결과를 가져와 LangChain과 OpenAI로 한국어 브리핑을 생성합니다.
수업 예제와 동일하게 `init_chat_model`, `ChatPromptTemplate`, `with_structured_output()`을 사용합니다.

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

## 브리핑 요청

기본값은 한국 시간 기준 어제입니다.

```bash
curl -X POST http://localhost:8000/api/briefings/yesterday
```

시연할 날짜를 직접 지정할 수도 있습니다.

```bash
curl -X POST 'http://localhost:8000/api/briefings/yesterday?date=2026-09-20'
```

TheSportsDB 무료 API는 날짜별 최대 3경기만 반환하므로, 화면과 발표 자료에 데이터 범위를 명시합니다.
