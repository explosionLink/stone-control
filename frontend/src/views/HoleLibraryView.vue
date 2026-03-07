<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

interface HoleDefinition {
  id: string;
  code: string;
  name: string;
  diameter_mm: number | null;
  depth_mm: number | null;
}

const holes = ref<HoleDefinition[]>([]);
const showModal = ref(false)
const isEditing = ref(false)
const currentHole = ref<any>({ code: '', name: '', diameter_mm: null, depth_mm: null });

const newHole = ref({
  code: '',
  name: '',
  diameter_mm: null,
  depth_mm: null
});

const fetchHoles = async () => {
  try {
    const response = await axios.get('/api/v1/hole-library/');
    holes.value = response.data;
  } catch (error) {
    console.error('Errore nel recupero libreria fori:', error);
  }
};

const openCreateModal = () => {
  currentHole.value = { code: '', name: '', diameter_mm: null, depth_mm: null }
  isEditing.value = false
  showModal.value = true
}

const openEditModal = (hole: any) => {
  currentHole.value = { ...hole }
  isEditing.value = true
  showModal.value = true
}

const saveHole = async () => {
  if (!currentHole.value.code || !currentHole.value.name) {
    alert('Codice e Nome sono obbligatori');
    return;
  }
  try {
    if (isEditing.value) {
      await axios.patch(`/api/v1/hole-library/${currentHole.value.id}`, currentHole.value);
    } else {
      await axios.post('/api/v1/hole-library/', currentHole.value);
    }
    showModal.value = false
    fetchHoles();
  } catch (error) {
    console.error('Errore nel salvataggio foro:', error);
  }
}

const deleteHole = async (id: string) => {
  if (!confirm('Sei sicuro di voler eliminare questa configurazione?')) return;
  try {
    await axios.delete(`/api/v1/hole-library/${id}`);
    fetchHoles();
  } catch (error) {
    console.error('Errore nella cancellazione foro:', error);
  }
};

onMounted(fetchHoles);
</script>

<template>
  <div class="library-container">
    <header class="view-header">
      <h1>Libreria Fori e Lavorazioni</h1>
      <p class="view-subtitle">Gestisci i tipi di foratura standard riconosciuti dal sistema</p>
    </header>

    <div class="view-actions">
       <button @click="openCreateModal" class="btn btn-primary">
          <span class="icon">➕</span> Aggiungi Nuovo Tipo Foro
       </button>
    </div>

    <div class="table-container bg-card">
      <table class="holes-table">
        <thead>
          <tr>
            <th>Codice</th>
            <th>Nome</th>
            <th>Diametro (mm)</th>
            <th>Profondità (mm)</th>
            <th class="actions-col">Azioni</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="hole in holes" :key="hole.id">
            <td class="code-cell">{{ hole.code }}</td>
            <td class="name-cell">{{ hole.name }}</td>
            <td>{{ hole.diameter_mm !== null ? hole.diameter_mm + ' mm' : '-' }}</td>
            <td>{{ hole.depth_mm !== null ? hole.depth_mm + ' mm' : '-' }}</td>
            <td class="actions-col">
              <div class="actions-flex">
                <button @click="openEditModal(hole)" class="btn btn-small btn-outline" title="Modifica">
                  ✏️ Modifica
                </button>
                <button @click="deleteHole(hole.id)" class="btn btn-small btn-danger" title="Elimina">
                  🗑️ Elimina
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="holes.length === 0">
            <td colspan="5" class="empty-table">Nessuna configurazione trovata.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Hole Library Modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <h2>{{ isEditing ? 'Modifica Tipo Foro' : 'Nuovo Tipo Foro' }}</h2>
        <form @submit.prevent="saveHole">
          <div class="form-group">
            <label>Codice</label>
            <input v-model="currentHole.code" required />
          </div>
          <div class="form-group">
            <label>Nome</label>
            <input v-model="currentHole.name" required />
          </div>
          <div class="form-group">
            <label>Diametro (mm)</label>
            <input type="number" v-model="currentHole.diameter_mm" step="0.1" />
          </div>
          <div class="form-group">
            <label>Profondità (mm)</label>
            <input type="number" v-model="currentHole.depth_mm" step="0.1" />
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
.library-container {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

.view-header {
  margin-bottom: 2.5rem;
}

.view-header h1 {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  color: white;
}

.view-subtitle {
  color: var(--text-muted);
  font-size: 1.1rem;
}

.add-hole-form {
  margin-bottom: 3rem;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

.form-title {
  margin-bottom: 1.5rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
}

.form-row {
  display: flex;
  gap: 1.25rem;
  align-items: flex-end;
  flex-wrap: wrap;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 2;
  min-width: 180px;
}

.input-group.mini {
  flex: 1;
  min-width: 100px;
}

.input-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.input-group input {
  background: var(--bg-dark);
  border: 1px solid var(--border);
  color: white;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s;
}

.input-group input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(66, 185, 131, 0.1);
}

.btn-add {
  height: 48px;
  padding: 0 1.5rem;
  font-weight: 600;
}

.table-container {
  padding: 0;
  overflow: hidden;
  border-radius: 16px;
}

.holes-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.holes-table th {
  background-color: rgba(255, 255, 255, 0.02);
  padding: 1.25rem 1.5rem;
  font-size: 0.9rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border);
}

.holes-table td {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border);
  font-size: 1rem;
}

.holes-table tr:last-child td {
  border-bottom: none;
}

.holes-table tr:hover {
  background-color: rgba(255, 255, 255, 0.01);
}

.code-cell {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  color: var(--primary);
}

.name-cell {
  font-weight: 500;
  color: white;
}

.actions-col {
  text-align: right;
  width: 200px;
}

.actions-flex {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.view-actions {
  margin-bottom: 2rem;
}

.btn-edit {
  background: rgba(255, 255, 255, 0.05);
  color: white;
  border: 1px solid var(--border);
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit:hover {
  border-color: var(--primary);
  background: rgba(66, 185, 131, 0.1);
}

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: var(--bg-card); padding: 2rem; border-radius: 12px; width: 100%; max-width: 400px; text-align: left; }
.form-group { margin-bottom: 1rem; display: flex; flex-direction: column; gap: 0.5rem; }
.form-group label { font-size: 0.85rem; color: var(--text-muted); font-weight: 600; }
.form-group input { background: var(--bg-dark); border: 1px solid var(--border); color: white; padding: 0.6rem; border-radius: 6px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1.5rem; }

.btn-delete {
  background: rgba(255, 82, 82, 0.1);
  color: var(--danger);
  border: 1px solid rgba(255, 82, 82, 0.2);
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  transition: all 0.2s;
  cursor: pointer;
  margin-left: auto;
}

.btn-delete:hover {
  background: var(--danger);
  color: white;
  transform: scale(1.1);
}

.empty-table {
  text-align: center;
  padding: 4rem !important;
  color: var(--text-muted);
  font-style: italic;
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    align-items: stretch;
  }
  .input-group {
    width: 100%;
  }
}
</style>
