import { defineStore } from 'pinia'

const getStorageKey = (listKey) => `preparation-items:${listKey}`

const loadSavedItems = (listKey) => {
  try {
    const savedItems = window.localStorage.getItem(getStorageKey(listKey))
    return savedItems ? JSON.parse(savedItems) : []
  } catch {
    return []
  }
}

export const usePreparationStore = defineStore('preparation', {
  state: () => ({
    items: [],
    currentListKey: 'default',
  }),

  getters: {
    completedCount: (state) => {
      return state.items.filter((item) => item.checked).length
    },

    remainingCount: (state) => {
      return state.items.filter((item) => !item.checked).length
    },
  },

  actions: {
    setRecommendations(weather, airQuality = null, listKey = 'default') {
      const recommendations = ['응원 도구']

      if (weather.temp >= 30) {
        recommendations.push('생수')
      }

      if (weather.status === '맑음') {
        recommendations.push('모자')
        recommendations.push('선크림')
      }

      if (weather.status === '비') {
        recommendations.push('우비')
        recommendations.push('우산')
      }

      if (weather.windSpeed >= 7) {
        recommendations.push('바람막이')
      }

      if (weather.temp <= 15) {
        recommendations.push('따뜻한 겉옷')
      }

      if (airQuality?.aqi > 100) {
        recommendations.push('마스크')
      }

      this.currentListKey = listKey

      const savedItems = loadSavedItems(listKey)
      const savedCheckState = new Map(
        savedItems.map((item) => [item.name, item.checked]),
      )
      const customItems = savedItems.filter((item) => item.isCustom)

      this.items = recommendations.map((name) => ({
        id: `recommended:${name}`,
        name,
        checked: savedCheckState.get(name) ?? false,
        isCustom: false,
      })).concat(customItems)

      this.persistItems()
    },

    toggleItem(itemId) {
      const item = this.items.find((item) => item.id === itemId)

      if (item) {
        item.checked = !item.checked
        this.persistItems()
      }
    },

    addCustomItem(name) {
      const trimmedName = name.trim()

      if (!trimmedName) return false

      const isDuplicated = this.items.some(
        (item) => item.name.toLowerCase() === trimmedName.toLowerCase(),
      )

      if (isDuplicated) return false

      this.items.push({
        id: `custom:${Date.now()}`,
        name: trimmedName,
        checked: false,
        isCustom: true,
      })
      this.persistItems()

      return true
    },

    removeCustomItem(itemId) {
      this.items = this.items.filter(
        (item) => item.id !== itemId || !item.isCustom,
      )
      this.persistItems()
    },

    resetItems() {
      this.items.forEach((item) => {
        item.checked = false
      })
      this.persistItems()
    },

    persistItems() {
      window.localStorage.setItem(
        getStorageKey(this.currentListKey),
        JSON.stringify(this.items),
      )
    },
  },
})
