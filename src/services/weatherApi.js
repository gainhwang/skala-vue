import axios from 'axios'

const API_KEY = import.meta.env.VITE_OPENWEATHER_API_KEY
const BASE_URL = import.meta.env.VITE_OPENWEATHER_BASE_URL
const AIR_QUALITY_URL = 'https://air-quality-api.open-meteo.com/v1/air-quality'

const checkWeatherConfig = () => {
  if (!API_KEY || !BASE_URL) {
    throw new Error('.env.local의 OpenWeather API 설정을 확인해 주세요.')
  }
}

export const getWeatherStatus = (weatherMain, description = '') => {
  if (weatherMain === 'Clear') return '맑음'
  if (['Rain', 'Drizzle', 'Thunderstorm'].includes(weatherMain)) return '비'

  return description
}

export const fetchCurrentWeather = async (stadium) => {
  checkWeatherConfig()

  const response = await axios.get(`${BASE_URL}/weather`, {
    params: {
      lat: stadium.lat,
      lon: stadium.lon,
      appid: API_KEY,
      units: 'metric',
      lang: 'kr',
    },
  })

  return response.data
}

export const fetchThreeHourForecast = async (stadium) => {
  checkWeatherConfig()

  const response = await axios.get(`${BASE_URL}/forecast`, {
    params: {
      lat: stadium.lat,
      lon: stadium.lon,
      appid: API_KEY,
      units: 'metric',
      lang: 'kr',
    },
  })

  const forecasts = response.data.list

  if (!forecasts?.length) {
    throw new Error('예보 데이터가 없습니다.')
  }

  const targetTime = Math.floor(Date.now() / 1000) + 3 * 60 * 60
  const forecast = forecasts.reduce((closest, item) => {
    const closestDifference = Math.abs(closest.dt - targetTime)
    const itemDifference = Math.abs(item.dt - targetTime)

    return itemDifference < closestDifference ? item : closest
  }, forecasts[0])

  const timezoneOffset = response.data.city.timezone
  const localDate = new Date((forecast.dt + timezoneOffset) * 1000)

  return {
    dateText: localDate.toLocaleString('ko-KR', {
      timeZone: 'UTC',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }),
    temp: forecast.main.temp,
    feelsLike: forecast.main.feels_like,
    status: forecast.weather[0].description,
    humidity: forecast.main.humidity,
    windSpeed: forecast.wind.speed,
    rainProbability: Math.round((forecast.pop ?? 0) * 100),
  }
}

export const fetchAirQuality = async (stadium) => {
  const response = await axios.get(AIR_QUALITY_URL, {
    params: {
      latitude: stadium.lat,
      longitude: stadium.lon,
      current: 'pm10,pm2_5,us_aqi',
      timezone: 'Asia/Seoul',
    },
  })

  return {
    pm10: response.data.current.pm10,
    pm2_5: response.data.current.pm2_5,
    aqi: response.data.current.us_aqi,
  }
}

export const getRequestErrorMessage = (error, fallback) => {
  return error.response?.data?.message ?? error.response?.data?.reason ?? error.message ?? fallback
}
