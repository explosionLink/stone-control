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
    router.push('/orders')
  } else {
    error.value = res.detail
  }
  loading.value = false
}
</script>

<template>
  <div class="login-view">
    <div class="login-card">
      <h1>Accesso Stone Control</h1>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Email</label>
          <input v-model="email" type="email" required placeholder="Inserisci la tua email" />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input v-model="password" type="password" required placeholder="Inserisci la tua password" />
        </div>
        <div v-if="error" class="error-msg">{{ error }}</div>
        <button type="submit" :disabled="loading">
          {{ loading ? 'Accesso in corso...' : 'Accedi' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-view {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 60vh;
}
.login-card {
  width: 100%;
  max-width: 400px;
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
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.error-msg {
  color: #e74c3c;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}
button {
  width: 100%;
  padding: 0.75rem;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:disabled {
  background: #a8d5c2;
}
</style>
