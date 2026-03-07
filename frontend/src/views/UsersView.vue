<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../api/crud'

const users = ref<any[]>([])
const loading = ref(false)
const showModal = ref(false)
const currentUser = ref<any>({ email: '', password: '', role: 'authenticated' })
const isEditing = ref(false)

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await api.users.list()
    users.value = res.data
  } catch (err) {
    console.error('Errore recupero utenti:', err)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  currentUser.value = { email: '', password: '', role: 'authenticated' }
  isEditing.value = false
  showModal.value = true
}

const openEditModal = (user: any) => {
  currentUser.value = { ...user }
  isEditing.value = true
  showModal.value = true
}

const saveUser = async () => {
  try {
    if (isEditing.value) {
      await api.users.update(currentUser.value.id, currentUser.value)
    } else {
      await api.users.create(currentUser.value)
    }
    showModal.value = false
    fetchUsers()
  } catch (err) {
    console.error('Errore salvataggio utente:', err)
  }
}

const deleteUser = async (id: string) => {
  if (confirm('Eliminare questo utente?')) {
    try {
      await api.users.delete(id)
      fetchUsers()
    } catch (err) {
      console.error('Errore eliminazione utente:', err)
    }
  }
}

onMounted(fetchUsers)
</script>

<template>
  <div class="users-view">
    <div class="view-header">
      <h1>Gestione Utenti</h1>
      <button class="btn primary" @click="openCreateModal">Nuovo Utente</button>
    </div>

    <div v-if="loading" class="loader">Caricamento...</div>

    <div v-else class="table-container">
      <table class="crud-table">
        <thead>
          <tr>
            <th>Email</th>
            <th>Ruolo Supabase</th>
            <th>Ultimo Accesso</th>
            <th>Azioni</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.email }}</td>
            <td>{{ user.role }}</td>
            <td>{{ user.last_sign_in_at ? new Date(user.last_sign_in_at).toLocaleString() : 'Mai' }}</td>
            <td class="actions">
              <button class="btn btn-small btn-outline" @click="openEditModal(user)">✏️ Modifica</button>
              <button class="btn btn-small btn-danger" @click="deleteUser(user.id)">🗑️ Elimina</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- User Modal -->
  <div v-if="showModal" class="modal-overlay">
    <div class="modal-content">
      <h2>{{ isEditing ? 'Modifica Utente' : 'Nuovo Utente' }}</h2>
      <form @submit.prevent="saveUser">
        <div class="form-group">
          <label>Email</label>
          <input v-model="currentUser.email" required type="email" :disabled="isEditing" />
        </div>
        <div class="form-group" v-if="!isEditing">
          <label>Password</label>
          <input v-model="currentUser.password" required type="password" />
        </div>
        <div class="form-group">
          <label>Ruolo Supabase</label>
          <select v-model="currentUser.role">
            <option value="authenticated">Authenticated</option>
            <option value="anon">Anon</option>
          </select>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn" @click="showModal = false">Annulla</button>
          <button type="submit" class="btn primary">Salva</button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.users-view { padding: 2rem 0; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.actions { display: flex; gap: 0.5rem; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: var(--bg-card); padding: 2rem; border-radius: 12px; width: 100%; max-width: 400px; }
.form-group { margin-bottom: 1rem; display: flex; flex-direction: column; gap: 0.5rem; }
select { background: var(--bg-dark); border: 1px solid var(--border); color: white; padding: 0.5rem; border-radius: 4px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1.5rem; }
</style>
