<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  const res = await auth.login(email.value, password.value)
  if (res.success) {
    if (res.mfaRequired) {
      router.push({
        path: '/mfa-verify',
        query: {
          access_token: res.mfaData.access_token,
          factor_id: res.mfaData.factor_id,
          challenge_id: res.mfaData.challenge_id
        }
      })
    } else {
      router.push('/orders')
    }
  } else {
    error.value = res.detail
  }
  loading.value = false
}
</script>

<template>
  <div class="auth-view">
    <div class="auth-card">
      <div class="auth-header">
        <span class="auth-icon">🔐</span>
        <h1>Accedi a Stone Control</h1>
        <p>Inserisci le tue credenziali per continuare</p>
      </div>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label>Email</label>
          <div class="input-wrapper">
            <input v-model="email" type="email" required placeholder="tuo@email.com" />
          </div>
        </div>

        <div class="form-group">
          <label>Password</label>
          <div class="input-wrapper">
            <input v-model="password" type="password" required placeholder="••••••••" />
          </div>
        </div>

        <div v-if="error" class="error-msg">
          <span class="icon">⚠️</span> {{ error }}
        </div>

        <button type="submit" :disabled="loading" class="btn-submit">
          {{ loading ? 'Accesso in corso...' : 'Entra' }}
        </button>

        <div class="auth-footer">
          Non hai un account? <router-link to="/register">Registrati ora</router-link>
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
  max-width: 420px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 2.5rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-icon {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 1rem;
}

.auth-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
}

.auth-header p {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
}

.input-wrapper input {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--bg-dark);
  border: 1px solid var(--border);
  border-radius: 10px;
  color: white;
  font-size: 1rem;
  transition: all 0.2s;
}

.input-wrapper input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.error-msg {
  background: rgba(231, 76, 60, 0.1);
  color: #ff5252;
  padding: 0.75rem;
  border-radius: 10px;
  font-size: 0.85rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-submit {
  width: 100%;
  padding: 0.75rem;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-submit:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
}

.btn-submit:disabled {
  background: var(--border);
  color: var(--text-muted);
  cursor: not-allowed;
}

.auth-footer {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.9rem;
  color: var(--text-muted);
}

.auth-footer a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
}
</style>
