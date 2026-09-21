import { defineStore } from 'pinia'
import { findStadiumByKboName, findStadiumByTeamId } from '@/data/stadiums'
import { findTeam, teams } from '@/data/teams'
import {
  fetchTodayGames as requestTodayGames,
  getKboApiErrorMessage,
} from '@/services/kboApi'

let pendingGamesRequest = null

const fallbackTeam = (teamId, teamName) => ({
  id: teamId,
  name: teamName,
  color: '#8492a6',
})

const toGame = (apiGame, previousGame) => {
  const homeTeam = findTeam(apiGame.home_team_id)
    ?? fallbackTeam(apiGame.home_team_id, apiGame.home_team)
  const awayTeam = findTeam(apiGame.away_team_id)
    ?? fallbackTeam(apiGame.away_team_id, apiGame.away_team)
  const stadium = findStadiumByKboName(apiGame.stadium_name)
    ?? findStadiumByTeamId(apiGame.home_team_id)

  return {
    id: apiGame.id,
    date: apiGame.date,
    stadiumId: stadium?.id ?? null,
    stadiumName: stadium?.name ?? apiGame.stadium_name,
    kboStadiumName: apiGame.stadium_name,
    startTime: apiGame.start_time,
    status: apiGame.status,
    isFinished: apiGame.is_finished,
    isCancelled: apiGame.is_cancelled,
    homeScore: apiGame.home_score,
    awayScore: apiGame.away_score,
    homeStartingPitcher: apiGame.home_starting_pitcher,
    awayStartingPitcher: apiGame.away_starting_pitcher,
    homeTeam,
    awayTeam,
    cheers: previousGame?.cheers ?? {
      home: 0,
      away: 0,
    },
  }
}

export const useGameStore = defineStore('game', {
  state: () => ({
    favoriteTeam: window.localStorage.getItem('favoriteTeam') || 'KIA',
    games: [],
    loadedDate: '',
    sourceNote: '',
    isLoading: false,
    errorMessage: '',
  }),

  getters: {
    teamOptions: () => teams,

    favoriteGame: (state) => {
      return state.games.find((game) => {
        return game.homeTeam.id === state.favoriteTeam || game.awayTeam.id === state.favoriteTeam
      })
    },
  },

  actions: {
    async fetchTodayGames({ force = false, date } = {}) {
      if (!force && this.loadedDate && !date) {
        return this.games
      }

      if (pendingGamesRequest) {
        return pendingGamesRequest
      }

      this.isLoading = true
      this.errorMessage = ''

      pendingGamesRequest = (async () => {
        try {
          const response = await requestTodayGames(date)
          const previousGames = new Map(this.games.map((game) => [game.id, game]))

          this.games = response.games.map((game) => toGame(game, previousGames.get(game.id)))
          this.loadedDate = response.date
          this.sourceNote = response.source_note

          return this.games
        } catch (error) {
          this.errorMessage = getKboApiErrorMessage(
            error,
            '오늘의 KBO 경기 정보를 불러오지 못했습니다.',
          )
          throw error
        } finally {
          this.isLoading = false
          pendingGamesRequest = null
        }
      })()

      return pendingGamesRequest
    },

    setFavoriteTeam(teamId) {
      this.favoriteTeam = teamId
      window.localStorage.setItem('favoriteTeam', teamId)
    },

    cheer(gameId, side) {
      const game = this.games.find((item) => item.id === gameId)

      if (!game) {
        return
      }

      if (side === 'home') {
        game.cheers.home++
      }

      if (side === 'away') {
        game.cheers.away++
      }
    },
  },
})
