import axios from 'axios'

const KBO_API_BASE_URL = import.meta.env.VITE_AI_API_BASE_URL || 'http://localhost:8000'

const kboApi = axios.create({
  baseURL: KBO_API_BASE_URL,
  timeout: 30000,
})

export const fetchTodayGames = async (date) => {
  const response = await kboApi.get('/api/games/today', {
    params: date ? { date } : undefined,
  })

  return response.data
}

export const fetchYesterdayBriefing = async (date) => {
  const response = await kboApi.post('/api/briefings/yesterday', null, {
    params: date ? { date } : undefined,
  })

  return response.data
}

export const getKboApiErrorMessage = (error, fallback) => {
  return error.response?.data?.detail ?? error.message ?? fallback
}
