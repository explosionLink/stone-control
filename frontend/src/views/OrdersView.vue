<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

interface Hole {
  id: string;
  type: string;
  x_mm: number;
  y_mm: number;
  width_mm: number;
  height_mm: number;
  diameter_mm: number | null;
  depth_mm: number | null;
}

interface Polygon {
  id: string;
  label: string;
  width_mm: number;
  height_mm: number;
  material: string;
  thickness_mm: number;
  is_mirrored: boolean;
  preview_path: string;
  dxf_path: string;
  holes: Hole[];
}

interface Order {
  id: string;
  code: string;
  created_at: string;
  polygons: Polygon[];
}

const orders = ref<Order[]>([]);
const fileInput = ref<HTMLInputElement | null>(null);
const uploading = ref(false);

const fetchOrders = async () => {
  try {
    const response = await axios.get('/api/v1/orders/');
    orders.value = response.data;
  } catch (error) {
    console.error('Errore nel recupero ordini:', error);
  }
};

const handleUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
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
      <button @click="fileInput?.click()" :disabled="uploading">
        {{ uploading ? 'Elaborazione in corso...' : 'Importa PDF Ordine' }}
      </button>
    </div>

    <div class="orders-list">
      <div v-for="order in orders" :key="order.id" class="order-card">
        <div class="order-header">
          <h3>Ordine: {{ order.code }}</h3>
          <span class="order-date">{{ new Date(order.created_at).toLocaleString() }}</span>
        </div>

        <div class="polygons-grid">
          <div v-for="poly in order.polygons" :key="poly.id" class="poly-card" :class="{ mirrored: poly.is_mirrored }">
            <div class="poly-header">
              <h4>{{ poly.label }}</h4>
              <span v-if="poly.is_mirrored" class="badge">Specchiato</span>
            </div>
            <p class="specs">{{ poly.width_mm }}x{{ poly.height_mm }} mm | Sp: {{ poly.thickness_mm }}mm | {{ poly.material }}</p>

            <div class="preview-container">
              <img :src="'/api/v1/outputs/' + poly.preview_path" alt="Preview" />
            </div>

            <div class="actions">
              <a :href="'/api/v1/outputs/' + poly.dxf_path" download class="btn-dxf">Scarica DXF</a>
            </div>

            <h5>Lavorazioni:</h5>
            <ul class="holes-list">
              <li v-for="hole in poly.holes" :key="hole.id">
                <span class="hole-type">{{ hole.type }}:</span>
                <span v-if="hole.diameter_mm">Ø{{ hole.diameter_mm }} prof. {{ hole.depth_mm }}</span>
                <span v-else>{{ hole.width_mm.toFixed(0) }}x{{ hole.height_mm.toFixed(0) }}</span>
                <span class="coords">(X:{{ hole.x_mm.toFixed(1) }}, Y:{{ hole.y_mm.toFixed(1) }})</span>
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
.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #eee;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
}
.order-date {
  color: #888;
  font-size: 0.9rem;
}
.poly-card {
  border: 1px solid #eee;
  padding: 1rem;
  background: white;
  transition: transform 0.2s;
}
.poly-card.mirrored {
  border-left: 5px solid #3498db;
}
.poly-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.badge {
  background: #3498db;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.7rem;
}
.specs {
  font-size: 0.85rem;
  color: #555;
  margin-bottom: 1rem;
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
