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
  <div class="register-view">
    <div class="register-card">
      <h1>Registrazione Stone Control</h1>

      <div v-if="success" class="success-msg">
        Registrazione completata con successo! Verrai reindirizzato al login...
      </div>

      <form v-else @submit.prevent="handleRegister">
        <div class="form-group">
          <label>Nome</label>
          <input v-model="name" type="text" required placeholder="Inserisci il tuo nome" />
        </div>
        <div class="form-group">
          <label>Email</label>
          <input v-model="email" type="email" required placeholder="Inserisci la tua email" />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input v-model="password" type="password" required placeholder="Minimo 8 caratteri" minlength="8" />
        </div>
        <div class="form-group">
          <label>Conferma Password</label>
          <input v-model="confirm_password" type="password" required placeholder="Ripeti la password" minlength="8" />
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>

        <button type="submit" :disabled="loading">
          {{ loading ? 'Registrazione in corso...' : 'Registrati' }}
        </button>

        <div class="login-link">
          Hai già un account? <router-link to="/login">Accedi</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.register-view {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}
.register-card {
  width: 100%;
  max-width: 450px;
  padding: 2rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
}
.form-group input {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.error-msg {
  color: #e74c3c;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}
.success-msg {
  color: #27ae60;
  background: #eafaf1;
  padding: 1rem;
  border-radius: 4px;
  text-align: center;
}
button {
  width: 100%;
  padding: 0.75rem;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}
button:disabled {
  background: #a8d5c2;
}
.login-link {
  margin-top: 1rem;
  text-align: center;
  font-size: 0.9rem;
}
</style>
