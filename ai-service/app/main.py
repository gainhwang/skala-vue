import json
import os
from datetime import date, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


load_dotenv()

KBO_GAME_LIST_URL = "https://www.koreabaseball.com/ws/Main.asmx/GetKboGameList"
KBO_BOX_SCORE_URL = (
    "https://www.koreabaseball.com/ws/Schedule.asmx/GetBoxScoreScroll"
)
KBO_SERIES_IDS = "0,1,3,4,5,6,7,8,9"
KBO_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx",
}
KST = ZoneInfo("Asia/Seoul")

KBO_TEAMS = {
    "HT": ("KIA", "KIA 타이거즈"),
    "SS": ("SAMSUNG", "삼성 라이온즈"),
    "LG": ("LG", "LG 트윈스"),
    "OB": ("DOOSAN", "두산 베어스"),
    "KT": ("KT", "KT 위즈"),
    "SK": ("SSG", "SSG 랜더스"),
    "LT": ("LOTTE", "롯데 자이언츠"),
    "NC": ("NC", "NC 다이노스"),
    "WO": ("KIWOOM", "키움 히어로즈"),
    "HH": ("HANWHA", "한화 이글스"),
}

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
    id: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    winning_pitcher: str | None = None
    losing_pitcher: str | None = None
    save_pitcher: str | None = None
    winning_hit: str | None = None


class TodayGame(BaseModel):
    id: str
    date: date
    start_time: str
    stadium_name: str
    status: str
    is_finished: bool
    is_cancelled: bool
    home_team_id: str
    home_team: str
    away_team_id: str
    away_team: str
    home_score: int | None = None
    away_score: int | None = None
    home_starting_pitcher: str | None = None
    away_starting_pitcher: str | None = None


class TodayGamesResponse(BaseModel):
    date: date
    total_games: int
    games: list[TodayGame]
    source_note: str


class BriefingCopy(BaseModel):
    headline: str = Field(description="전날 경기 결과를 표현하는 짧은 한국어 제목")
    summary: str = Field(
        description="제공된 경기 기록만 근거로 작성한 3~5문장의 한국어 요약"
    )


class MorningBriefingResponse(BaseModel):
    date: date
    total_games: int
    headline: str
    summary: str
    games: list[GameResult]
    source_note: str


SYSTEM_PROMPT = """
당신은 KBO 경기 결과를 전달하는 아침 브리핑 작성자입니다.
반드시 제공된 팀 이름, 최종 점수, 승리·패전·세이브 투수, 결승타 기록만 사용하세요.
선수 이름, 경기 장면, 이닝 상황, 경기장, 순위 등 입력에 없는 사실은 추측하지 마세요.
값이 null이거나 비어 있는 항목은 언급하지 마세요.
승패와 선수 기록을 자연스러운 한국어로 요약하세요.
과장된 표현이나 특정 팀을 비하하는 표현은 사용하지 마세요.
""".strip()

USER_PROMPT = """
[경기 날짜]
{game_date}

[최종 경기 결과 JSON]
{game_results}

이 결과를 바탕으로 짧은 제목과 3~5문장의 아침 브리핑을 작성하세요.
""".strip()


def yesterday_in_korea() -> date:
    return datetime.now(KST).date() - timedelta(days=1)


def today_in_korea() -> date:
    return datetime.now(KST).date()


def clean_text(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).replace("&nbsp;", " ").strip()
    return text or None


def parse_score(value: Any) -> int | None:
    text = clean_text(value)
    if text is None:
        return None

    try:
        return int(text)
    except ValueError:
        return None


def get_team(team_code: Any, fallback_name: Any) -> tuple[str, str]:
    code = clean_text(team_code) or ""
    if code in KBO_TEAMS:
        return KBO_TEAMS[code]

    fallback = clean_text(fallback_name) or code or "팀 정보 없음"
    return code, fallback


def get_game_status(game: dict[str, Any]) -> str:
    if str(game.get("CANCEL_SC_ID", "0")) != "0":
        return clean_text(game.get("CANCEL_SC_NM")) or "경기 취소"

    if game.get("GAME_RESULT_CK") == 1:
        return "경기 종료"

    if parse_score(game.get("T_SCORE_CN")) is not None:
        return "경기 중"

    return "경기 예정"


async def fetch_kbo_game_list(
    client: httpx.AsyncClient,
    game_date: date,
) -> list[dict[str, Any]]:
    form_data = {
        "leId": "1",
        "srId": KBO_SERIES_IDS,
        "date": game_date.strftime("%Y%m%d"),
    }

    try:
        response = await client.post(
            KBO_GAME_LIST_URL,
            data=form_data,
            headers=KBO_HEADERS,
        )
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="KBO 경기 목록을 불러오지 못했습니다.",
        ) from exc
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail="KBO 경기 목록 응답을 해석하지 못했습니다.",
        ) from exc

    return payload.get("game") or []


async def fetch_winning_hit(
    client: httpx.AsyncClient,
    game: dict[str, Any],
    game_date: date,
) -> str | None:
    game_id = clean_text(game.get("G_ID"))
    if not game_id:
        return None

    form_data = {
        "leId": "1",
        "srId": str(game.get("SR_ID", 0)),
        "seasonId": str(game.get("SEASON_ID", game_date.year)),
        "gameId": game_id,
    }

    try:
        response = await client.post(
            KBO_BOX_SCORE_URL,
            data=form_data,
            headers=KBO_HEADERS,
        )
        response.raise_for_status()
        payload = response.json()
        table_etc = json.loads(payload.get("tableEtc") or "{}")
    except (httpx.HTTPError, json.JSONDecodeError, TypeError, ValueError):
        return None

    for row_wrapper in table_etc.get("rows", []):
        cells = [clean_text(cell.get("Text")) for cell in row_wrapper.get("row", [])]
        if len(cells) >= 2 and cells[0] == "결승타":
            return cells[1]

    return None


def to_today_game(game: dict[str, Any], game_date: date) -> TodayGame:
    home_team_id, home_team = get_team(game.get("HOME_ID"), game.get("HOME_NM"))
    away_team_id, away_team = get_team(game.get("AWAY_ID"), game.get("AWAY_NM"))
    is_finished = game.get("GAME_RESULT_CK") == 1
    is_cancelled = str(game.get("CANCEL_SC_ID", "0")) != "0"

    return TodayGame(
        id=clean_text(game.get("G_ID")) or "",
        date=game_date,
        start_time=clean_text(game.get("G_TM")) or "시간 미정",
        stadium_name=clean_text(game.get("S_NM")) or "구장 미정",
        status=get_game_status(game),
        is_finished=is_finished,
        is_cancelled=is_cancelled,
        home_team_id=home_team_id,
        home_team=home_team,
        away_team_id=away_team_id,
        away_team=away_team,
        home_score=parse_score(game.get("B_SCORE_CN")),
        away_score=parse_score(game.get("T_SCORE_CN")),
        home_starting_pitcher=clean_text(game.get("B_PIT_P_NM")),
        away_starting_pitcher=clean_text(game.get("T_PIT_P_NM")),
    )


async def fetch_kbo_results(game_date: date) -> list[GameResult]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        events = await fetch_kbo_game_list(client, game_date)
        games = []

        for event in events:
            if event.get("GAME_RESULT_CK") != 1:
                continue

            home_score = parse_score(event.get("B_SCORE_CN"))
            away_score = parse_score(event.get("T_SCORE_CN"))
            if home_score is None or away_score is None:
                continue

            _, home_team = get_team(event.get("HOME_ID"), event.get("HOME_NM"))
            _, away_team = get_team(event.get("AWAY_ID"), event.get("AWAY_NM"))
            winning_hit = await fetch_winning_hit(client, event, game_date)

            games.append(
                GameResult(
                    id=clean_text(event.get("G_ID")) or "",
                    home_team=home_team,
                    away_team=away_team,
                    home_score=home_score,
                    away_score=away_score,
                    winning_pitcher=clean_text(event.get("W_PIT_P_NM")),
                    losing_pitcher=clean_text(event.get("L_PIT_P_NM")),
                    save_pitcher=clean_text(event.get("SV_PIT_P_NM")),
                    winning_hit=winning_hit,
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


@app.get("/api/games/today", response_model=TodayGamesResponse)
async def get_today_games(
    game_date: date | None = Query(default=None, alias="date"),
):
    target_date = game_date or today_in_korea()

    async with httpx.AsyncClient(timeout=10.0) as client:
        raw_games = await fetch_kbo_game_list(client, target_date)

    games = [to_today_game(game, target_date) for game in raw_games]

    return TodayGamesResponse(
        date=target_date,
        total_games=len(games),
        games=games,
        source_note="KBO 공식 홈페이지 경기 일정·결과 기준입니다.",
    )


@app.post("/api/briefings/yesterday", response_model=MorningBriefingResponse)
async def create_yesterday_briefing(
    game_date: date | None = Query(default=None, alias="date"),
):
    target_date = game_date or yesterday_in_korea()
    games = await fetch_kbo_results(target_date)
    source_note = "KBO 공식 홈페이지 경기 기록 기준입니다."

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
