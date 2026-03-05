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
    <header class="profile-header">
      <h1>Profilo Utente</h1>
    </header>

    <div class="profile-content">
      <section class="info-card">
        <div class="card-header">
          <span class="icon">👤</span>
          <h3>Informazioni Account</h3>
        </div>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">Email</span>
            <span class="value">{{ auth.user?.email }}</span>
          </div>
          <div class="info-item">
            <span class="label">ID Utente</span>
            <span class="value code">{{ auth.user?.id }}</span>
          </div>
        </div>
      </section>

      <section class="security-card">
        <div class="card-header">
          <span class="icon">🛡️</span>
          <h3>Sicurezza (MFA)</h3>
        </div>

        <div class="mfa-status-container">
          <div v-if="loading && !enrolling" class="mfa-loading">
            <div class="spinner-small"></div> Verificando stato...
          </div>

          <div v-if="mfaFactors.length > 0" class="mfa-active">
            <div class="status-badge active">Attivo</div>
            <p>L'autenticazione a due fattori è attiva.</p>
            <ul class="factors-list">
              <li v-for="factor in mfaFactors" :key="factor.id">
                <div class="factor-info">
                  <span class="factor-name">{{ factor.friendly_name || 'Authenticator App' }}</span>
                  <span class="factor-type">{{ factor.factor_type }}</span>
                </div>
                <button @click="removeMfa(factor.id)" class="btn-remove">Disattiva</button>
              </li>
            </ul>
          </div>

          <div v-else-if="!enrolling" class="mfa-inactive">
            <div class="status-badge inactive">Non Attivo</div>
            <p>Aggiungi un ulteriore livello di sicurezza al tuo account.</p>
            <button @click="startMfaEnroll" class="btn-enable">Configura MFA</button>
          </div>

          <!-- Enrollment Flow -->
          <div v-if="enrolling && enrollData" class="enrollment-flow">
            <h4>Configura Authenticator</h4>
            <ol class="steps-list">
              <li>Installa un'app come Google Authenticator o Authy.</li>
              <li>Scansiona il codice QR qui sotto:</li>
            </ol>

            <div class="qr-box" v-html="enrollData.qr_code"></div>

            <p class="manual-code">O usa il codice: <code>{{ enrollData.secret }}</code></p>

            <div class="verify-form">
              <label>Inserisci il codice a 6 cifre per confermare:</label>
              <input v-model="verificationCode" type="text" placeholder="000 000" maxlength="6" />
              <div class="flow-actions">
                <button @click="confirmEnrollment" :disabled="loading" class="btn-confirm">Attiva Ora</button>
                <button @click="enrolling = false" class="btn-cancel">Annulla</button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="error" class="error-msg-inline">{{ error }}</div>
        <div v-if="success" class="success-msg-inline">{{ success }}</div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.profile-view {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.profile-header {
  margin-bottom: 2.5rem;
}

.profile-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
}

.profile-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

.info-card, .security-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 2rem;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.card-header .icon { font-size: 1.5rem; }
.card-header h3 { margin: 0; font-size: 1.1rem; color: white; }

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.label {
  font-size: 0.8rem;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.5px;
}

.value {
  font-size: 1.1rem;
  font-weight: 600;
  color: white;
}

.value.code {
  font-family: monospace;
  font-size: 0.9rem;
  background: var(--bg-dark);
  padding: 4px 8px;
  border-radius: 4px;
  color: var(--primary);
}

/* MFA Styles */
.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 1rem;
}

.status-badge.active { background: rgba(39, 174, 96, 0.1); color: #2ecc71; border: 1px solid rgba(39, 174, 96, 0.2); }
.status-badge.inactive { background: rgba(255, 255, 255, 0.05); color: var(--text-muted); border: 1px solid var(--border); }

.mfa-active p, .mfa-inactive p {
  color: var(--text-muted);
  margin-bottom: 1.5rem;
}

.factors-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.factors-list li {
  background: var(--bg-dark);
  padding: 1rem;
  border-radius: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.factor-name { display: block; font-weight: 600; color: white; }
.factor-type { font-size: 0.75rem; color: var(--text-muted); }

.btn-remove {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--danger);
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-remove:hover { background: rgba(255, 82, 82, 0.1); border-color: var(--danger); }

.btn-enable {
  background: var(--primary);
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.qr-box {
  background: white;
  padding: 1rem;
  border-radius: 12px;
  display: inline-block;
  margin: 1.5rem 0;
}

.manual-code code {
  background: var(--bg-dark);
  padding: 4px 8px;
  border-radius: 4px;
  color: var(--primary);
  font-size: 1rem;
}

.verify-form {
  margin-top: 2rem;
  background: var(--bg-dark);
  padding: 1.5rem;
  border-radius: 12px;
}

.verify-form input {
  display: block;
  width: 100%;
  max-width: 200px;
  margin: 1rem 0;
  padding: 0.75rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: white;
  text-align: center;
  font-size: 1.25rem;
  letter-spacing: 2px;
  border-radius: 8px;
}

.flow-actions {
  display: flex;
  gap: 1rem;
}

.btn-confirm { background: var(--primary); color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 6px; cursor: pointer; }
.btn-cancel { background: transparent; color: var(--text-muted); border: 1px solid var(--border); padding: 0.6rem 1.2rem; border-radius: 6px; cursor: pointer; }

.error-msg-inline { color: var(--danger); margin-top: 1rem; font-size: 0.9rem; }
.success-msg-inline { color: var(--primary); margin-top: 1rem; font-size: 0.9rem; font-weight: 600; }

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--primary);
  border-radius: 50%;
  display: inline-block;
  animation: spin 0.8s linear infinite;
  vertical-align: middle;
  margin-right: 0.5rem;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
