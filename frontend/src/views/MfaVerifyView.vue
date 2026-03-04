<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter, useRoute } from 'vue-router'

const code = ref('')
const error = ref('')
const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

// Dati passati tramite state del router o query params
const accessToken = ref('')
const factorId = ref('')
const challengeId = ref('')

onMounted(() => {
  accessToken.value = (route.query.access_token as string) || ''
  factorId.value = (route.query.factor_id as string) || ''
  challengeId.value = (route.query.challenge_id as string) || ''

  if (!accessToken.value || !factorId.value || !challengeId.value) {
    error.value = 'Parametri di verifica mancanti. Torna al login.'
  }
})

const handleVerify = async () => {
  loading.value = true
  error.value = ''

  const res = await auth.verifyMfa({
    access_token: accessToken.value,
    factor_id: factorId.value,
    challenge_id: challengeId.value,
    code: code.value
  })

  if (res.success) {
    router.push('/orders')
  } else {
    error.value = res.detail
  }
  loading.value = false
}
</script>

<template>
  <div class="mfa-verify-view">
    <div class="mfa-card">
      <h1>Verifica MFA</h1>
      <p>Inserisci il codice di sicurezza generato dalla tua app di autenticazione.</p>

      <form @submit.prevent="handleVerify">
        <div class="form-group">
          <label>Codice OTP</label>
          <input
            v-model="code"
            type="text"
            required
            placeholder="000000"
            maxlength="6"
            pattern="\d{6}"
            autofocus
          />
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>

        <button type="submit" :disabled="loading || !code">
          {{ loading ? 'Verifica in corso...' : 'Verifica e Accedi' }}
        </button>

        <div class="back-link">
          <router-link to="/login">Torna al login</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.mfa-verify-view {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 60vh;
}
.mfa-card {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  text-align: center;
}
.mfa-card p {
  color: #666;
  margin-bottom: 1.5rem;
}
.form-group {
  margin-bottom: 1.5rem;
}
.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1.5rem;
  text-align: center;
  letter-spacing: 0.5rem;
}
.error-msg {
  color: #e74c3c;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}
button {
  width: 100%;
  padding: 0.75rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}
button:disabled {
  background: #bdc3c7;
}
.back-link {
  margin-top: 1rem;
}
</style>
