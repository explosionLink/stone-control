import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null as string | null,
    user: null as any,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(email: string, pass: string) {
      try {
        const res = await axios.post('/api/v1/auth/login', { email, pass })
        if (res.data.session) {
          this.token = res.data.session.access_token
          this.user = res.data.session.user
          localStorage.setItem('token', this.token!)
          axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
          return { success: true }
        }
        return { success: false, detail: 'Risposta inattesa dal server' }
      } catch (err: any) {
        return { success: false, detail: err.response?.data?.detail || 'Errore login' }
      }
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    },
    init() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      }
    }
  }
})
