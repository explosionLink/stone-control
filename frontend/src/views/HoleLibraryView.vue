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

const createHole = async () => {
  if (!newHole.value.code || !newHole.value.name) {
    alert('Codice e Nome sono obbligatori');
    return;
  }
  try {
    await axios.post('/api/v1/hole-library/', newHole.value);
    newHole.value = { code: '', name: '', diameter_mm: null, depth_mm: null };
    fetchHoles();
  } catch (error) {
    console.error('Errore nella creazione foro:', error);
  }
};

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

    <div class="add-hole-form bg-card">
      <h3 class="form-title">Aggiungi Nuovo Tipo Foro</h3>
      <div class="form-row">
        <div class="input-group">
          <label>Codice</label>
          <input v-model="newHole.code" placeholder="es. BUSSOLA_12" />
        </div>
        <div class="input-group">
          <label>Nome</label>
          <input v-model="newHole.name" placeholder="es. Bussola Ø12" />
        </div>
        <div class="input-group mini">
          <label>Ø mm</label>
          <input type="number" v-model="newHole.diameter_mm" placeholder="0" />
        </div>
        <div class="input-group mini">
          <label>Profondità</label>
          <input type="number" v-model="newHole.depth_mm" placeholder="0" />
        </div>
        <button @click="createHole" class="btn btn-primary btn-add">
          <span class="icon">➕</span> Aggiungi
        </button>
      </div>
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
              <button @click="deleteHole(hole.id)" class="btn-delete" title="Elimina">
                🗑️
              </button>
            </td>
          </tr>
          <tr v-if="holes.length === 0">
            <td colspan="5" class="empty-table">Nessuna configurazione trovata.</td>
          </tr>
        </tbody>
      </table>
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
  width: 100px;
}

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
