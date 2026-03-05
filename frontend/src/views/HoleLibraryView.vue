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
  try {
    await axios.post('/api/v1/hole-library/', newHole.value);
    newHole.value = { code: '', name: '', diameter_mm: null, depth_mm: null };
    fetchHoles();
  } catch (error) {
    console.error('Errore nella creazione foro:', error);
  }
};

const deleteHole = async (id: string) => {
  if (!confirm('Sei sicuro?')) return;
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
    <h1>Libreria Fori e Lavorazioni</h1>

    <div class="add-hole-form">
      <h3>Aggiungi Nuovo Tipo Foro</h3>
      <div class="form-row">
        <input v-model="newHole.code" placeholder="Codice (es. BUSSOLA_12)" />
        <input v-model="newHole.name" placeholder="Nome (es. Bussola Ø12)" />
        <input type="number" v-model="newHole.diameter_mm" placeholder="Ø mm" />
        <input type="number" v-model="newHole.depth_mm" placeholder="Profondità mm" />
        <button @click="createHole">Aggiungi</button>
      </div>
    </div>

    <table class="holes-table">
      <thead>
        <tr>
          <th>Codice</th>
          <th>Nome</th>
          <th>Diametro (mm)</th>
          <th>Profondità (mm)</th>
          <th>Azioni</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="hole in holes" :key="hole.id">
          <td>{{ hole.code }}</td>
          <td>{{ hole.name }}</td>
          <td>{{ hole.diameter_mm || '-' }}</td>
          <td>{{ hole.depth_mm || '-' }}</td>
          <td>
            <button @click="deleteHole(hole.id)" class="btn-delete">Elimina</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.library-container {
  padding: 2rem;
}
.add-hole-form {
  background: #f4f4f4;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}
.form-row {
  display: flex;
  gap: 0.5rem;
}
.form-row input {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.holes-table {
  width: 100%;
  border-collapse: collapse;
}
.holes-table th, .holes-table td {
  border: 1px solid #ddd;
  padding: 0.8rem;
  text-align: left;
}
.holes-table th {
  background-color: #f2f2f2;
}
.btn-delete {
  background-color: #ff4d4d;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
}
</style>
