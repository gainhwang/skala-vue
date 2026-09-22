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
RECENT_GAME_LOOKBACK_DAYS = 14
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

KBO_TEAM_PROFILES = [
    {
        "id": "KIA",
        "name": "KIA 타이거즈",
        "region": "광주",
        "colors": ["빨강", "검정"],
        "mascot": "🐯",
        "history": "오랜 역사와 우승 전통을 가진 구단",
        "cheering": "열정적이고 힘찬 응원 분위기",
        "outing": "광주의 다양한 먹거리와 함께 직관 여행을 즐기기 좋음",
    },
    {
        "id": "SAMSUNG",
        "name": "삼성 라이온즈",
        "region": "대구",
        "colors": ["파랑", "흰색"],
        "mascot": "🦁",
        "history": "꾸준한 성적과 오랜 전통을 가진 구단",
        "cheering": "전통적인 응원가와 가족적인 관람 분위기",
        "outing": "대구 지역 먹거리와 함께 즐기기 좋음",
    },
    {
        "id": "LG",
        "name": "LG 트윈스",
        "region": "서울 잠실",
        "colors": ["진분홍", "검정"],
        "mascot": "👯",
        "history": "서울을 연고로 오랜 팬층을 가진 구단",
        "cheering": "도시적이고 활기찬 응원 분위기",
        "outing": "대중교통 접근성과 주변 즐길 거리를 중요하게 보는 팬에게 어울림",
    },
    {
        "id": "DOOSAN",
        "name": "두산 베어스",
        "region": "서울 잠실",
        "colors": ["남색", "흰색"],
        "mascot": "🐻",
        "history": "끈기 있는 야구와 오랜 역사를 가진 구단",
        "cheering": "친숙한 응원가와 단단한 팬 문화를 즐길 수 있음",
        "outing": "서울 나들이와 함께 직관하기 편리함",
    },
    {
        "id": "KT",
        "name": "KT 위즈",
        "region": "수원",
        "colors": ["검정", "빨강"],
        "mascot": "🧙",
        "history": "젊고 현대적인 이미지를 가진 구단",
        "cheering": "가볍고 즐거운 관람 분위기",
        "outing": "수원의 먹거리와 함께 경기 관람을 즐기기 좋음",
    },
    {
        "id": "SSG",
        "name": "SSG 랜더스",
        "region": "인천",
        "colors": ["빨강", "흰색"],
        "mascot": "🚀",
        "history": "인천 야구의 전통을 이어가는 구단",
        "cheering": "볼거리와 현장 이벤트가 어우러진 활기찬 분위기",
        "outing": "경기장 먹거리와 야구장 경험을 함께 즐기려는 팬에게 어울림",
    },
    {
        "id": "LOTTE",
        "name": "롯데 자이언츠",
        "region": "부산 사직",
        "colors": ["남색", "빨강"],
        "mascot": "🐦",
        "history": "부산을 대표하는 깊은 야구 전통을 가진 구단",
        "cheering": "함께 노래하고 뛰는 열정적인 응원 문화",
        "outing": "부산의 다양한 먹거리와 직관 여행을 함께 즐기기 좋음",
    },
    {
        "id": "NC",
        "name": "NC 다이노스",
        "region": "창원",
        "colors": ["남색", "금색"],
        "mascot": "🦕",
        "history": "젊고 새로운 도전을 이어가는 구단",
        "cheering": "가족과 함께 즐기기 좋은 밝은 관람 분위기",
        "outing": "현대적인 야구장 경험을 중요하게 보는 팬에게 어울림",
    },
    {
        "id": "KIWOOM",
        "name": "키움 히어로즈",
        "region": "서울 고척",
        "colors": ["버건디", "흰색"],
        "mascot": "🦸",
        "history": "새로운 선수의 성장을 지켜보는 재미가 큰 구단",
        "cheering": "선수의 성장과 개성을 응원하는 분위기",
        "outing": "날씨와 관계없이 돔구장에서 관람하기 좋음",
    },
    {
        "id": "HANWHA",
        "name": "한화 이글스",
        "region": "대전",
        "colors": ["주황", "검정"],
        "mascot": "🦅",
        "history": "오랫동안 함께한 팬들의 끈끈한 이야기가 있는 구단",
        "cheering": "열정적이고 낭만적인 팬 문화를 느끼기 좋음",
        "outing": "대전의 먹거리와 함께 야구 여행을 즐기기 좋음",
    },
]

TEAM_COLORS = {
    "KIA": "#c8102e",
    "SAMSUNG": "#0066b3",
    "LG": "#c30452",
    "DOOSAN": "#131230",
    "KT": "#222222",
    "SSG": "#ce0e2d",
    "LOTTE": "#041e42",
    "NC": "#315288",
    "KIWOOM": "#820024",
    "HANWHA": "#f37321",
}

app = FastAPI(
    title="KBO Morning Briefing AI Service",
    description="직전 KBO 경기 결과를 LangChain으로 요약하는 API",
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
    winner: str | None = None
    loser: str | None = None
    winning_pitcher: str | None = None
    losing_pitcher: str | None = None
    save_pitcher: str | None = None
    winning_hit: str | None = None
    ai_summary: str | None = None


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


class GameBriefingCopy(BaseModel):
    game_id: str = Field(description="입력으로 제공된 경기의 id")
    summary: str = Field(
        description="해당 경기 기록만 근거로 작성한 1~2문장의 한국어 요약"
    )


class BriefingCopy(BaseModel):
    headline: str = Field(description="직전 경기일의 결과를 표현하는 짧은 한국어 제목")
    game_briefings: list[GameBriefingCopy] = Field(
        description="입력된 모든 경기를 같은 순서로 하나씩 요약한 목록"
    )


class MorningBriefingResponse(BaseModel):
    date: date
    total_games: int
    headline: str
    summary: str
    games: list[GameResult]
    source_note: str


class LatestGameResultsResponse(BaseModel):
    date: date
    total_games: int
    games: list[GameResult]
    source_note: str


class TeamRecommendationRequest(BaseModel):
    preference: str = Field(
        min_length=2,
        max_length=500,
        description="좋아하는 지역, 색상, 응원 분위기 등을 자유롭게 적은 문장",
    )


class TeamRecommendationCopy(BaseModel):
    recommended_team_id: str = Field(description="가장 잘 맞는 구단의 id")
    title: str = Field(description="돌잡이 결과를 알리는 짧고 재미있는 제목")
    preference_summary: str = Field(description="사용자 취향을 한 문장으로 정리한 내용")
    reasons: list[str] = Field(
        min_length=2,
        max_length=3,
        description="제공된 구단 프로필에 근거한 추천 이유",
    )
    second_choice_team_id: str = Field(description="두 번째로 잘 맞는 구단의 id")
    second_choice_reason: str = Field(description="차선 구단을 추천한 짧은 이유")


class TeamRecommendationResponse(BaseModel):
    recommended_team_id: str
    recommended_team: str
    color: str
    mascot: str
    title: str
    preference_summary: str
    reasons: list[str]
    second_choice_team_id: str
    second_choice_team: str
    second_choice_mascot: str
    second_choice_reason: str
    source_note: str


SYSTEM_PROMPT = """
당신은 KBO 경기 결과를 전달하는 아침 브리핑 작성자입니다.
반드시 제공된 팀 이름, 최종 점수, 승리·패전·세이브 투수, 결승타 기록만 사용하세요.
winner는 승리팀, loser는 패배팀입니다. winning_pitcher는 승리팀의 승리투수이고 losing_pitcher는 패배팀의 패전투수입니다.
승리투수와 패전투수의 역할을 절대로 서로 바꾸어 표현하지 마세요.
선수 이름, 경기 장면, 이닝 상황, 경기장, 순위 등 입력에 없는 사실은 추측하지 마세요.
값이 null이거나 비어 있는 항목은 언급하지 마세요.
각 경기마다 입력의 id를 game_id에 그대로 복사하고, 1~2문장으로 각각 요약하세요.
입력된 모든 경기를 빠짐없이 같은 순서로 game_briefings에 포함하세요.
서로 다른 경기의 선수 기록을 섞지 마세요.
과장된 표현이나 특정 팀을 비하하는 표현은 사용하지 마세요.
""".strip()

USER_PROMPT = """
[경기 날짜]
{game_date}

[최종 경기 결과 JSON]
{game_results}

이 결과를 바탕으로 전체 제목 하나와 경기별 1~2문장의 브리핑을 작성하세요.
""".strip()

TEAM_PICK_SYSTEM_PROMPT = """
당신은 사용자의 취향과 가장 잘 맞는 KBO 구단을 찾아주는 '야구팀 돌잡이' 안내자입니다.
반드시 제공된 10개 구단 프로필 안에서만 1순위와 2순위를 선택하세요.
지역, 색상, 역사, 응원 분위기, 직관과 먹거리 취향 등 사용자가 말한 여러 조건을 함께 고려하세요.
사용자가 중요하게 표현한 조건을 우선하되, 입력에 없는 취향을 임의로 만들어내지 마세요.
구단 프로필에 없는 선수, 성적, 순위, 특정 식당이나 시설은 언급하지 마세요.
recommended_team_id와 second_choice_team_id에는 프로필의 id를 정확히 복사하세요.
두 구단은 서로 달라야 하며, reasons에는 2~3개의 간결한 한국어 추천 이유를 작성하세요.
추천은 취향에 따른 가벼운 안내이며 절대적인 평가처럼 표현하지 마세요.
""".strip()

TEAM_PICK_USER_PROMPT = """
[KBO 구단 프로필 JSON]
{team_profiles}

[사용자가 입력한 취향]
{preference}

사용자에게 가장 잘 맞는 구단과 차선 구단을 골라 돌잡이 결과를 작성하세요.
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
            if home_score > away_score:
                winner, loser = home_team, away_team
            elif away_score > home_score:
                winner, loser = away_team, home_team
            else:
                winner, loser = None, None
            winning_hit = await fetch_winning_hit(client, event, game_date)

            games.append(
                GameResult(
                    id=clean_text(event.get("G_ID")) or "",
                    home_team=home_team,
                    away_team=away_team,
                    home_score=home_score,
                    away_score=away_score,
                    winner=winner,
                    loser=loser,
                    winning_pitcher=clean_text(event.get("W_PIT_P_NM")),
                    losing_pitcher=clean_text(event.get("L_PIT_P_NM")),
                    save_pitcher=clean_text(event.get("SV_PIT_P_NM")),
                    winning_hit=winning_hit,
                )
            )

    return games


async def find_latest_kbo_results(
    start_date: date,
    lookback_days: int = RECENT_GAME_LOOKBACK_DAYS,
) -> tuple[date, list[GameResult]]:
    for days_ago in range(lookback_days):
        candidate_date = start_date - timedelta(days=days_ago)
        games = await fetch_kbo_results(candidate_date)
        if games:
            return candidate_date, games

    return start_date, []


def build_game_summary_fallback(game: GameResult) -> str:
    score = (
        f"{game.away_team} {game.away_score}-{game.home_score} "
        f"{game.home_team} 경기"
    )
    if game.winner:
        return f"{score}에서 {game.winner}가 승리했습니다."

    return f"{score}는 무승부로 끝났습니다."


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


def get_team_profile(team_id: str) -> dict[str, Any] | None:
    return next(
        (team for team in KBO_TEAM_PROFILES if team["id"] == team_id),
        None,
    )


def create_team_recommendation_chain():
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY가 설정되지 않았습니다.",
        )

    model = init_chat_model(
        os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        model_provider="openai",
        temperature=0.4,
    )
    structured_model = model.with_structured_output(TeamRecommendationCopy)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", TEAM_PICK_SYSTEM_PROMPT),
            ("human", TEAM_PICK_USER_PROMPT),
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


@app.get(
    "/api/games/latest-results",
    response_model=LatestGameResultsResponse,
)
async def get_latest_game_results(
    game_date: date | None = Query(default=None, alias="date"),
):
    if game_date:
        target_date = game_date
        games = await fetch_kbo_results(target_date)
    else:
        target_date, games = await find_latest_kbo_results(yesterday_in_korea())

    return LatestGameResultsResponse(
        date=target_date,
        total_games=len(games),
        games=games,
        source_note=(
            "KBO 공식 홈페이지 경기 기록 기준입니다. "
            "이 조회에서는 OpenAI를 사용하지 않습니다."
        ),
    )


@app.post("/api/briefings/latest", response_model=MorningBriefingResponse)
@app.post(
    "/api/briefings/yesterday",
    response_model=MorningBriefingResponse,
    include_in_schema=False,
)
async def create_latest_briefing(
    game_date: date | None = Query(default=None, alias="date"),
):
    if game_date:
        target_date = game_date
        games = await fetch_kbo_results(target_date)
    else:
        target_date, games = await find_latest_kbo_results(yesterday_in_korea())

    source_note = "KBO 공식 홈페이지 경기 기록 기준입니다."

    if not games:
        return MorningBriefingResponse(
            date=target_date,
            total_games=0,
            headline="최근 완료된 KBO 경기를 찾지 못했습니다",
            summary=(
                f"최근 {RECENT_GAME_LOOKBACK_DAYS}일 동안 확인 가능한 "
                "경기 결과가 없습니다."
            ),
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

    valid_game_ids = {game.id for game in games}
    summaries_by_id = {
        item.game_id: item.summary
        for item in briefing.game_briefings
        if item.game_id in valid_game_ids
    }
    games_with_summaries = [
        game.model_copy(
            update={
                "ai_summary": summaries_by_id.get(game.id)
                or build_game_summary_fallback(game)
            }
        )
        for game in games
    ]
    combined_summary = "\n".join(
        game.ai_summary or "" for game in games_with_summaries
    )

    return MorningBriefingResponse(
        date=target_date,
        total_games=len(games),
        headline=briefing.headline,
        summary=combined_summary,
        games=games_with_summaries,
        source_note=source_note,
    )


@app.post(
    "/api/team-recommendations",
    response_model=TeamRecommendationResponse,
)
async def recommend_kbo_team(request: TeamRecommendationRequest):
    preference = request.preference.strip()
    if len(preference) < 2:
        raise HTTPException(
            status_code=422,
            detail="좋아하는 지역이나 색상, 응원 분위기를 조금 더 적어 주세요.",
        )

    chain = create_team_recommendation_chain()

    try:
        recommendation = await chain.ainvoke(
            {
                "team_profiles": json.dumps(
                    KBO_TEAM_PROFILES,
                    ensure_ascii=False,
                ),
                "preference": preference,
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="야구팀 돌잡이 결과를 만드는 데 실패했습니다.",
        ) from exc

    recommended_team = get_team_profile(recommendation.recommended_team_id)
    second_choice_team = get_team_profile(recommendation.second_choice_team_id)

    if (
        recommended_team is None
        or second_choice_team is None
        or recommended_team["id"] == second_choice_team["id"]
    ):
        raise HTTPException(
            status_code=502,
            detail="추천 결과에서 구단 정보를 확인하지 못했습니다. 다시 시도해 주세요.",
        )

    return TeamRecommendationResponse(
        recommended_team_id=recommended_team["id"],
        recommended_team=recommended_team["name"],
        color=TEAM_COLORS[recommended_team["id"]],
        mascot=recommended_team["mascot"],
        title=recommendation.title,
        preference_summary=recommendation.preference_summary,
        reasons=recommendation.reasons,
        second_choice_team_id=second_choice_team["id"],
        second_choice_team=second_choice_team["name"],
        second_choice_mascot=second_choice_team["mascot"],
        second_choice_reason=recommendation.second_choice_reason,
        source_note="미리 정리한 KBO 10개 구단 프로필과 입력한 취향을 바탕으로 한 AI 추천입니다.",
    )
