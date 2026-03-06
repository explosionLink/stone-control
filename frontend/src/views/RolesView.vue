<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../api/crud'

const roles = ref<any[]>([])
const loading = ref(false)
const showModal = ref(false)
const currentRole = ref<any>({ name: '', description: '' })
const isEditing = ref(false)

const fetchRoles = async () => {
  loading.value = true
  try {
    const res = await api.roles.list()
    roles.value = res.data
  } catch (err) {
    console.error('Errore recupero ruoli:', err)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  currentRole.value = { name: '', description: '' }
  isEditing.value = false
  showModal.value = true
}

const openEditModal = (role: any) => {
  currentRole.value = { ...role }
  isEditing.value = true
  showModal.value = true
}

const saveRole = async () => {
  try {
    if (isEditing.value) {
      await api.roles.update(currentRole.value.id, currentRole.value)
    } else {
      await api.roles.create(currentRole.value)
    }
    showModal.value = false
    fetchRoles()
  } catch (err) {
    console.error('Errore salvataggio ruolo:', err)
  }
}

const deleteRole = async (id: string) => {
  if (confirm('Sei sicuro di voler eliminare questo ruolo?')) {
    try {
      await api.roles.delete(id)
      fetchRoles()
    } catch (err) {
      console.error('Errore eliminazione ruolo:', err)
    }
  }
}

onMounted(fetchRoles)
</script>

<template>
  <div class="roles-view">
    <div class="view-header">
      <h1>Gestione Ruoli</h1>
      <button class="btn primary" @click="openCreateModal">Nuovo Ruolo</button>
    </div>

    <div v-if="loading" class="loader">Caricamento...</div>

    <div v-else class="table-container">
      <table class="crud-table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>Descrizione</th>
            <th>Azioni</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="role in roles" :key="role.id">
            <td><strong>{{ role.name }}</strong></td>
            <td>{{ role.description }}</td>
            <td class="actions">
              <button class="btn small" @click="openEditModal(role)">Modifica</button>
              <button class="btn small danger" @click="deleteRole(role.id)">Elimina</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <h2>{{ isEditing ? 'Modifica Ruolo' : 'Nuovo Ruolo' }}</h2>
        <form @submit.prevent="saveRole">
          <div class="form-group">
            <label>Nome</label>
            <input v-model="currentRole.name" required />
          </div>
          <div class="form-group">
            <label>Descrizione</label>
            <textarea v-model="currentRole.description"></textarea>
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
.roles-view { padding: 2rem 0; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.actions { display: flex; gap: 0.5rem; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: var(--bg-card); padding: 2rem; border-radius: 12px; width: 100%; max-width: 400px; }
.form-group { margin-bottom: 1rem; display: flex; flex-direction: column; gap: 0.5rem; }
textarea { background: var(--bg-dark); border: 1px solid var(--border); color: white; padding: 0.5rem; border-radius: 4px; min-height: 80px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1.5rem; }
</style>
