<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

const mfaFactors = ref<any[]>([])
const loading = ref(false)
const enrolling = ref(false)
const enrollData = ref<any>(null)
const verificationCode = ref('')
const error = ref('')
const success = ref('')

const fetchMfaStatus = async () => {
  loading.value = true
  const res = await auth.listMfaFactors()
  if (res.success) {
    mfaFactors.value = res.factors
  }
  loading.value = false
}

const startMfaEnroll = async () => {
  enrolling.value = true
  error.value = ''
  const res = await auth.enrollMfa()
  if (res.success) {
    enrollData.value = res.data
  } else {
    error.value = res.detail
    enrolling.value = false
  }
}

const confirmEnrollment = async () => {
  if (!verificationCode.value) return
  loading.value = true
  error.value = ''

  const res = await auth.verifyMfa({
    access_token: auth.token!,
    factor_id: enrollData.value.factor_id,
    challenge_id: enrollData.value.challenge_id,
    code: verificationCode.value
  })

  if (res.success) {
    success.value = 'MFA attivata con successo!'
    enrollData.value = null
    enrolling.value = false
    verificationCode.value = ''
    await fetchMfaStatus()
  } else {
    error.value = res.detail
  }
  loading.value = false
}

const removeMfa = async (factorId: string) => {
  if (!confirm('Sei sicuro di voler disattivare l\'MFA?')) return
  loading.value = true
  const res = await auth.deleteMfaFactor(factorId)
  if (res.success) {
    success.value = 'MFA rimossa correttamente.'
    await fetchMfaStatus()
  } else {
    error.value = res.detail
  }
  loading.value = false
}

onMounted(fetchMfaStatus)
</script>

<template>
  <div class="profile-view">
    <div class="profile-container">
      <h1>Il Tuo Profilo</h1>

      <section class="user-info">
        <h3>Informazioni Account</h3>
        <p><strong>Email:</strong> {{ auth.user?.email }}</p>
        <p><strong>ID:</strong> {{ auth.user?.id }}</p>
      </section>

      <section class="mfa-section">
        <h3>Sicurezza: Multi-Factor Authentication (MFA)</h3>

        <div v-if="loading && !enrolling" class="loading">Caricamento stato sicurezza...</div>

        <div v-if="mfaFactors.length > 0">
          <p class="status-active">L'MFA è attiva sul tuo account.</p>
          <ul class="factors-list">
            <li v-for="factor in mfaFactors" :key="factor.id">
              {{ factor.friendly_name || 'App Authenticator' }} ({{ factor.factor_type }})
              <button @click="removeMfa(factor.id)" class="btn-danger">Rimuovi</button>
            </li>
          </ul>
        </div>

        <div v-else-if="!enrolling">
          <p class="status-inactive">L'MFA non è attualmente attiva.</p>
          <button @click="startMfaEnroll" class="btn-primary">Attiva MFA</button>
        </div>

        <!-- Flusso di attivazione -->
        <div v-if="enrolling && enrollData" class="enroll-container">
          <h4>Configura Authenticator</h4>
          <p>Scansiona il codice QR con un'app come Google Authenticator o Authy.</p>

          <div class="qr-container" v-html="enrollData.qr_code"></div>

          <p class="secret-text">O inserisci il codice manualmente: <code>{{ enrollData.secret }}</code></p>

          <div class="verify-step">
            <label>Inserisci il codice di verifica a 6 cifre:</label>
            <input v-model="verificationCode" type="text" placeholder="000000" maxlength="6" />
            <div class="actions">
              <button @click="confirmEnrollment" :disabled="loading" class="btn-success">Conferma e Attiva</button>
              <button @click="enrolling = false" class="btn-secondary">Annulla</button>
            </div>
          </div>
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>
        <div v-if="success" class="success-msg">{{ success }}</div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.profile-view {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}
.profile-container {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #eee;
}
h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}
.status-active {
  color: #27ae60;
  font-weight: bold;
}
.status-inactive {
  color: #7f8c8d;
  margin-bottom: 1rem;
}
.factors-list {
  list-style: none;
  padding: 0;
}
.factors-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}
.qr-container {
  display: flex;
  justify-content: center;
  margin: 1.5rem 0;
  background: white;
  padding: 1rem;
  border: 1px solid #ddd;
}
.secret-text {
  font-size: 0.9rem;
  text-align: center;
  margin-bottom: 1.5rem;
}
.verify-step {
  background: #f0f7ff;
  padding: 1.5rem;
  border-radius: 8px;
}
.verify-step input {
  display: block;
  width: 100%;
  padding: 0.75rem;
  margin: 0.5rem 0 1rem;
  font-size: 1.2rem;
  text-align: center;
}
.actions {
  display: flex;
  gap: 1rem;
}
.btn-primary { background: #3498db; color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 4px; cursor: pointer; }
.btn-success { background: #2ecc71; color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 4px; cursor: pointer; flex: 1; }
.btn-danger { background: #e74c3c; color: white; border: none; padding: 0.4rem 0.8rem; border-radius: 4px; cursor: pointer; }
.btn-secondary { background: #95a5a6; color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 4px; cursor: pointer; }

.error-msg { color: #e74c3c; margin-top: 1rem; }
.success-msg { color: #27ae60; margin-top: 1rem; font-weight: bold; }
</style>
