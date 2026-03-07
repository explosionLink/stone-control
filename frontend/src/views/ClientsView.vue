<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../api/crud'

const clients = ref<any[]>([])
const loading = ref(false)
const showModal = ref(false)
const currentClient = ref<any>({ name: '', code: '' })
const isEditing = ref(false)

const fetchClients = async () => {
  loading.value = true
  try {
    const res = await api.clients.list()
    clients.value = res.data
  } catch (err) {
    console.error('Errore recupero clienti:', err)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  currentClient.value = { name: '', code: '' }
  isEditing.value = false
  showModal.value = true
}

const openEditModal = (client: any) => {
  currentClient.value = { ...client }
  isEditing.value = true
  showModal.value = true
}

const saveClient = async () => {
  try {
    if (isEditing.value) {
      await api.clients.update(currentClient.value.id, currentClient.value)
    } else {
      await api.clients.create(currentClient.value)
    }
    showModal.value = false
    fetchClients()
  } catch (err) {
    console.error('Errore salvataggio cliente:', err)
  }
}

const deleteClient = async (id: string) => {
  if (confirm('Sei sicuro di voler eliminare questo cliente?')) {
    try {
      await api.clients.delete(id)
      fetchClients()
    } catch (err) {
      console.error('Errore eliminazione cliente:', err)
    }
  }
}

onMounted(fetchClients)
</script>

<template>
  <div class="clients-view">
    <div class="view-header">
      <h1>Gestione Clienti</h1>
      <button class="btn primary" @click="openCreateModal">Nuovo Cliente</button>
    </div>

    <div v-if="loading" class="loader">Caricamento...</div>

    <div v-else class="table-container">
      <table class="crud-table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>Codice</th>
            <th>Azioni</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="client in clients" :key="client.id">
            <td><strong>{{ client.name }}</strong></td>
            <td><code>{{ client.code }}</code></td>
            <td class="actions">
              <button class="btn btn-small btn-outline" @click="openEditModal(client)">✏️ Modifica</button>
              <button class="btn btn-small btn-danger" @click="deleteClient(client.id)">🗑️ Elimina</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal semplice -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <h2>{{ isEditing ? 'Modifica Cliente' : 'Nuovo Cliente' }}</h2>
        <form @submit.prevent="saveClient">
          <div class="form-group">
            <label>Nome</label>
            <input v-model="currentClient.name" required />
          </div>
          <div class="form-group">
            <label>Codice</label>
            <input v-model="currentClient.code" required />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn" @click="showModal = false">Annulla</button>
            <button type="submit" class="btn primary">Salva</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.clients-view {
  padding: 2rem 0;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.actions {
  display: flex;
  gap: 0.5rem;
}
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: var(--bg-card);
  padding: 2rem;
  border-radius: 12px;
  width: 100%;
  max-width: 400px;
}
.form-group {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}
</style>
