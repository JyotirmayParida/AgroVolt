import { create } from 'zustand'

const useStore = create((set) => ({
  // Selected farm
  selectedFarm: null,
  setSelectedFarm: (farm) => set({ selectedFarm: farm }),

  // All farms list
  farms: [],
  setFarms: (farms) => set({ farms }),

  // Last prediction results
  cropResult: null,
  setCropResult: (data) => set({ cropResult: data }),

  solarResult: null,
  setSolarResult: (data) => set({ solarResult: data }),

  irrigationResult: null,
  setIrrigationResult: (data) => set({ irrigationResult: data }),

  // Weather
  weatherData: null,
  setWeatherData: (data) => set({ weatherData: data }),

  // Loading / error
  loading: false,
  setLoading: (v) => set({ loading: v }),

  error: null,
  setError: (msg) => set({ error: msg }),
}))

export default useStore
