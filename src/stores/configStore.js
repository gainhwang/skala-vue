import { defineStore } from 'pinia'

export const useConfigStore = defineStore('config', {
  state: () => ({
    unit: 'celsius',
  }),

  getters: {
    unitSymbol: (state) => {
      return state.unit === 'celsius' ? '℃' : '℉'
    },
  },

  actions: {
    toggleUnit() {
      if (this.unit === 'celsius') {
        this.unit = 'fahrenheit'
      } else {
        this.unit = 'celsius'
      }
    },
  },
})
