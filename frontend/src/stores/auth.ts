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
    async login(email: string, password: string) {
      try {
        const res = await axios.post('/api/v1/auth/login', { email, password })
        if (res.data.status === 'mfa_required') {
          return { success: true, mfaRequired: true, mfaData: res.data }
        }
        if (res.data.access_token) {
          this.token = res.data.access_token
          this.user = res.data.user
          localStorage.setItem('token', this.token!)
          axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
          return { success: true }
        }
        return { success: false, detail: 'Risposta inattesa dal server' }
      } catch (err: any) {
        return { success: false, detail: err.response?.data?.detail || 'Errore login' }
      }
    },
    async register(payload: any) {
      try {
        const res = await axios.post('/api/v1/auth/register', payload)
        return { success: true, data: res.data }
      } catch (err: any) {
        return { success: false, detail: err.response?.data?.detail || 'Errore registrazione' }
      }
    },
    async verifyMfa(payload: { access_token: string, factor_id: string, challenge_id: string, code: string }) {
      try {
        const res = await axios.post('/api/v1/auth/mfa/verify', payload)
        if (res.data.access_token) {
          this.token = res.data.access_token
          this.user = res.data.user
          localStorage.setItem('token', this.token!)
          axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
          return { success: true }
        }
        return { success: false, detail: 'Errore durante la verifica MFA' }
      } catch (err: any) {
        return { success: false, detail: err.response?.data?.detail || 'Codice non valido' }
      }
    },
    async enrollMfa(friendlyName: string = 'App Authenticator') {
      try {
        const res = await axios.post('/api/v1/auth/mfa/enroll-totp', { friendly_name: friendlyName })
        return { success: true, data: res.data }
      } catch (err: any) {
        return { success: false, detail: err.response?.data?.detail || 'Errore attivazione MFA' }
      }
    },
    async listMfaFactors() {
      try {
        const res = await axios.get('/api/v1/auth/mfa/factors')
        return { success: true, factors: res.data.factors }
      } catch (err: any) {
        return { success: false, detail: err.response?.data?.detail || 'Errore recupero fattori MFA' }
      }
    },
    async deleteMfaFactor(factorId: string) {
      try {
        await axios.delete(`/api/v1/auth/mfa/factors/${factorId}`)
        return { success: true }
      } catch (err: any) {
        return { success: false, detail: err.response?.data?.detail || 'Errore eliminazione fattore MFA' }
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
