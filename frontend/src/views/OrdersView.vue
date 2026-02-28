<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

const orders = ref([]);
const fileInput = ref(null);
const uploading = ref(false);

const fetchOrders = async () => {
  try {
    const response = await axios.get('/api/v1/orders/');
    orders.value = response.data;
  } catch (error) {
    console.error('Errore nel recupero ordini:', error);
  }
};

const handleUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  uploading.value = true;
  try {
    await axios.post('/api/v1/orders/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    fetchOrders();
  } catch (error) {
    alert('Errore durante l\'importazione del PDF');
    console.error(error);
  } finally {
    uploading.value = false;
  }
};

onMounted(fetchOrders);
</script>

<template>
  <div class="orders-container">
    <h1>Gestione Ordini Cucina</h1>

    <div class="upload-section">
      <input type="file" ref="fileInput" @change="handleUpload" accept=".pdf" style="display: none" />
      <button @click="$refs.fileInput.click()" :disabled="uploading">
        {{ uploading ? 'Elaborazione in corso...' : 'Importa PDF Ordine' }}
      </button>
    </div>

    <div class="orders-list">
      <div v-for="order in orders" :key="order.id" class="order-card">
        <h3>Ordine: {{ order.code }}</h3>
        <p>Data: {{ new Date(order.created_at).toLocaleString() }}</p>

        <div class="polygons-grid">
          <div v-for="poly in order.polygons" :key="poly.id" class="poly-card">
            <h4>{{ poly.label }} ({{ poly.width_mm }}x{{ poly.height_mm }} mm)</h4>
            <div class="preview-container">
              <img :src="'/api/v1/outputs/' + poly.preview_path" alt="Preview" />
            </div>
            <div class="actions">
              <a :href="'/api/v1/outputs/' + poly.dxf_path" download>Scarica DXF</a>
            </div>
            <ul class="holes-list">
              <li v-for="hole in poly.holes" :key="hole.id">
                Foro: {{ hole.width_mm }}x{{ hole.height_mm }} mm (X: {{ hole.x_mm.toFixed(1) }}, Y: {{ hole.y_mm.toFixed(1) }})
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.orders-container {
  padding: 2rem;
}
.upload-section {
  margin-bottom: 2rem;
}
.order-card {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 2rem;
  background: #f9f9f9;
}
.polygons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}
.poly-card {
  border: 1px solid #eee;
  padding: 1rem;
  background: white;
}
.preview-container img {
  max-width: 100%;
  height: auto;
  border: 1px solid #ddd;
}
.actions {
  margin: 1rem 0;
}
.actions a {
  background: #42b983;
  color: white;
  padding: 0.5rem 1rem;
  text-decoration: none;
  border-radius: 4px;
}
.holes-list {
  font-size: 0.8rem;
  color: #666;
}
</style>
