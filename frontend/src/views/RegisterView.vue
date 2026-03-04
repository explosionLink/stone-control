<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const name = ref('')
const email = ref('')
const password = ref('')
const confirm_password = ref('')
const error = ref('')
const success = ref(false)
const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()

const handleRegister = async () => {
  if (password.value !== confirm_password.value) {
    error.value = 'Le password non corrispondono'
    return
  }

  loading.value = true
  error.value = ''

  const payload = {
    name: name.value,
    email: email.value,
    password: password.value,
    confirm_password: confirm_password.value
  }

  const res = await auth.register(payload)
  if (res.success) {
    success.value = true
    setTimeout(() => {
      router.push('/login')
    }, 3000)
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
        <span class="auth-icon">🚀</span>
        <h1>Inizia con Stone Control</h1>
        <p>Crea il tuo account gratuito</p>
      </div>

      <div v-if="success" class="success-msg">
        <span class="icon">✅</span> Registrazione completata! Reindirizzamento...
      </div>

      <form v-else @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label>Nome Completo</label>
          <div class="input-wrapper">
            <input v-model="name" type="text" required placeholder="Nome Cognome" />
          </div>
        </div>

        <div class="form-group">
          <label>Email</label>
          <div class="input-wrapper">
            <input v-model="email" type="email" required placeholder="tuo@email.com" />
          </div>
        </div>

        <div class="form-group">
          <label>Password (min 8 car.)</label>
          <div class="input-wrapper">
            <input v-model="password" type="password" required minlength="8" placeholder="••••••••" />
          </div>
        </div>

        <div class="form-group">
          <label>Conferma Password</label>
          <div class="input-wrapper">
            <input v-model="confirm_password" type="password" required minlength="8" placeholder="••••••••" />
          </div>
        </div>

        <div v-if="error" class="error-msg">
          <span class="icon">⚠️</span> {{ error }}
        </div>

        <button type="submit" :disabled="loading" class="btn-submit">
          {{ loading ? 'Creazione account...' : 'Crea Account' }}
        </button>

        <div class="auth-footer">
          Hai già un account? <router-link to="/login">Accedi</router-link>
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
  max-width: 440px;
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
  margin-bottom: 1.25rem;
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
  padding: 0.7rem 1rem;
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

.success-msg {
  background: rgba(39, 174, 96, 0.1);
  color: var(--primary);
  padding: 1.5rem;
  border-radius: 10px;
  text-align: center;
  font-weight: 600;
}

.btn-submit {
  width: 100%;
  padding: 0.8rem;
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
