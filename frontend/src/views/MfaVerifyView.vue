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
  <div class="auth-view">
    <div class="auth-card mfa-verify">
      <div class="auth-header">
        <span class="auth-icon">🛡️</span>
        <h1>Verifica MFA</h1>
        <p>Inserisci il codice di sicurezza dall'app Authenticator</p>
      </div>

      <form @submit.prevent="handleVerify" class="auth-form">
        <div class="form-group otp-group">
          <label>Codice di Verifica</label>
          <div class="otp-input-container">
            <input
              v-model="code"
              type="text"
              required
              placeholder="000 000"
              maxlength="6"
              pattern="\d{6}"
              autofocus
            />
          </div>
        </div>

        <div v-if="error" class="error-msg">
          <span class="icon">⚠️</span> {{ error }}
        </div>

        <button type="submit" :disabled="loading || !code" class="btn-submit">
          {{ loading ? 'Verifica...' : 'Verifica e Accedi' }}
        </button>

        <div class="auth-footer">
          <router-link to="/login">Torna al login</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.auth-view {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 4rem 1rem;
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 2.5rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  text-align: center;
}

.auth-header { margin-bottom: 2rem; }
.auth-icon { font-size: 2.5rem; display: block; margin-bottom: 1rem; }
.auth-header h1 { font-size: 1.5rem; color: white; margin-bottom: 0.5rem; }
.auth-header p { color: var(--text-muted); font-size: 0.9rem; }

.otp-group label { display: block; margin-bottom: 1rem; color: var(--text-muted); font-size: 0.85rem; }

.otp-input-container input {
  width: 100%;
  padding: 1rem;
  background: var(--bg-dark);
  border: 2px solid var(--border);
  border-radius: 12px;
  color: white;
  font-size: 2rem;
  text-align: center;
  letter-spacing: 0.5rem;
  font-family: monospace;
  transition: border-color 0.2s;
}

.otp-input-container input:focus {
  outline: none;
  border-color: var(--primary);
}

.error-msg {
  background: rgba(231, 76, 60, 0.1);
  color: #ff5252;
  padding: 0.75rem;
  border-radius: 10px;
  font-size: 0.85rem;
  margin: 1.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: center;
}

.btn-submit {
  width: 100%;
  padding: 0.85rem;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-submit:hover { background: var(--primary-hover); }

.auth-footer { margin-top: 1.5rem; font-size: 0.9rem; }
.auth-footer a { color: var(--text-muted); text-decoration: none; }
.auth-footer a:hover { color: white; }
</style>
