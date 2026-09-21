import json
import os
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


load_dotenv()

SPORTS_DB_URL = "https://www.thesportsdb.com/api/v1/json/123/eventsday.php"
KBO_LEAGUE_ID = "4830"
KST = ZoneInfo("Asia/Seoul")

app = FastAPI(
    title="KBO Morning Briefing AI Service",
    description="전날 KBO 경기 결과를 LangChain으로 요약하는 API",
    version="0.1.0",
)

frontend_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class GameResult(BaseModel):
    home_team: str
    away_team: str
    home_score: int
    away_score: int


class BriefingCopy(BaseModel):
    headline: str = Field(description="전날 경기 결과를 표현하는 짧은 한국어 제목")
    summary: str = Field(description="확인 가능한 점수만 근거로 작성한 2~3문장의 한국어 요약")


class MorningBriefingResponse(BaseModel):
    date: date
    total_games: int
    headline: str
    summary: str
    games: list[GameResult]
    source_note: str


SYSTEM_PROMPT = """
당신은 KBO 경기 결과를 전달하는 아침 브리핑 작성자입니다.
반드시 제공된 팀 이름과 최종 점수만 사용하세요.
선수 이름, 경기 장면, 이닝 상황, 경기장, 순위 등 입력에 없는 사실을 추측하지 마세요.
승패와 점수 차처럼 최종 점수로 직접 확인할 수 있는 사실만 자연스러운 한국어로 요약하세요.
과장된 표현이나 특정 팀을 비하하는 표현은 사용하지 마세요.
""".strip()

USER_PROMPT = """
[경기 날짜]
{game_date}

[최종 경기 결과 JSON]
{game_results}

이 결과를 바탕으로 짧은 제목과 2~3문장의 아침 브리핑을 작성하세요.
""".strip()


def yesterday_in_korea() -> date:
    return datetime.now(KST).date() - timedelta(days=1)


async def fetch_kbo_results(game_date: date) -> list[GameResult]:
    params = {
        "d": game_date.isoformat(),
        "l": KBO_LEAGUE_ID,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(SPORTS_DB_URL, params=params)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="KBO 경기 결과를 불러오지 못했습니다.",
        ) from exc

    events = response.json().get("events") or []
    games = []

    for event in events:
        home_score = event.get("intHomeScore")
        away_score = event.get("intAwayScore")
        home_team = event.get("strHomeTeam")
        away_team = event.get("strAwayTeam")

        if None in (home_score, away_score, home_team, away_team):
            continue

        games.append(
            GameResult(
                home_team=home_team,
                away_team=away_team,
                home_score=int(home_score),
                away_score=int(away_score),
            )
        )

    return games


def create_briefing_chain():
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY가 설정되지 않았습니다.",
        )

    model = init_chat_model(
        os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        model_provider="openai",
        temperature=0.2,
    )
    structured_model = model.with_structured_output(BriefingCopy)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT),
        ]
    )
    return prompt | structured_model


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/briefings/yesterday", response_model=MorningBriefingResponse)
async def create_yesterday_briefing(
    game_date: date | None = Query(default=None, alias="date"),
):
    target_date = game_date or yesterday_in_korea()
    games = await fetch_kbo_results(target_date)
    source_note = "TheSportsDB 무료 API는 날짜별 최대 3경기를 제공합니다."

    if not games:
        return MorningBriefingResponse(
            date=target_date,
            total_games=0,
            headline="어제는 완료된 KBO 경기가 없었습니다",
            summary="확인 가능한 경기 결과가 없어 오늘의 브리핑을 쉬어갑니다.",
            games=[],
            source_note=source_note,
        )

    chain = create_briefing_chain()
    game_results = [game.model_dump() for game in games]

    try:
        briefing = await chain.ainvoke(
            {
                "game_date": target_date.isoformat(),
                "game_results": json.dumps(game_results, ensure_ascii=False),
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="AI 브리핑 생성에 실패했습니다.",
        ) from exc

    return MorningBriefingResponse(
        date=target_date,
        total_games=len(games),
        headline=briefing.headline,
        summary=briefing.summary,
        games=games,
        source_note=source_note,
    )
