import { defineStore } from 'pinia'

export const useGameStore = defineStore('game', {
  state: () => ({
    favoriteTeam: window.localStorage.getItem('favoriteTeam') || 'KIA',

    games: [
      {
        id: 'game_01',
        stadiumId: 'city_01',
        stadiumName: '광주기아챔피언스필드',
        startTime: '18:30',
        weather: {
          temp: 35,
          status: '맑음',
          humidity: 55,
          windSpeed: 2.5,
        },

        homeTeam: {
          id: 'KIA',
          name: 'KIA 타이거즈',
          color: '#c8102e',
        },

        awayTeam: {
          id: 'SSG',
          name: 'SSG 랜더스',
          color: '#ce0e2d',
        },

        cheers: {
          home: 0,
          away: 0,
        },
      },
      {
        id: 'game_02',
        stadiumId: 'city_03',
        stadiumName: '수원KT위즈파크',
        startTime: '18:30',
        weather: {
          temp: 33,
          status: '흐림',
          humidity: 70,
          windSpeed: 4,
        },

        homeTeam: {
          id: 'KT',
          name: 'KT 위즈',
          color: '#222222',
        },

        awayTeam: {
          id: 'LG',
          name: 'LG 트윈스',
          color: '#c30452',
        },

        cheers: {
          home: 0,
          away: 0,
        },
      },
      {
        id: 'game_03',
        stadiumId: 'city_05',
        stadiumName: '대구삼성라이온즈파크',
        startTime: '18:30',
        weather: {
          temp: 36,
          status: '맑음',
          humidity: 50,
          windSpeed: 3,
        },

        homeTeam: {
          id: 'SAMSUNG',
          name: '삼성 라이온즈',
          color: '#0066b3',
        },

        awayTeam: {
          id: 'LOTTE',
          name: '롯데 자이언츠',
          color: '#041e42',
        },

        cheers: {
          home: 0,
          away: 0,
        },
      },
      {
        id: 'game_04',
        stadiumId: 'city_04',
        stadiumName: '창원NC파크',
        startTime: '18:30',
        weather: {
          temp: 34,
          status: '흐림',
          humidity: 68,
          windSpeed: 8,
        },

        homeTeam: {
          id: 'NC',
          name: 'NC 다이노스',
          color: '#315288',
        },

        awayTeam: {
          id: 'DOOSAN',
          name: '두산 베어스',
          color: '#131230',
        },

        cheers: {
          home: 0,
          away: 0,
        },
      },
      {
        id: 'game_05',
        stadiumId: 'city_02',
        stadiumName: '대전한화생명볼파크',
        startTime: '18:30',
        weather: {
          temp: 32,
          status: '비',
          humidity: 90,
          windSpeed: 6,
        },

        homeTeam: {
          id: 'HANWHA',
          name: '한화 이글스',
          color: '#f37321',
        },

        awayTeam: {
          id: 'KIWOOM',
          name: '키움 히어로즈',
          color: '#820024',
        },

        cheers: {
          home: 0,
          away: 0,
        },
      },
    ],
  }),

  getters: {
    teamOptions: (state) => {
      const teams = state.games.flatMap((game) => [game.homeTeam, game.awayTeam])

      return [...new Map(teams.map((team) => [team.id, team])).values()]
    },

    favoriteGame: (state) => {
      return state.games.find((game) => {
        return game.homeTeam.id === state.favoriteTeam || game.awayTeam.id === state.favoriteTeam
      })
    },
  },

  actions: {
    setFavoriteTeam(teamId) {
      this.favoriteTeam = teamId
      window.localStorage.setItem('favoriteTeam', teamId)
    },

    cheer(gameId, side) {
      const game = this.games.find((game) => game.id === gameId)

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
