<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();

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
  } catch (error: any) {
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
    alert('Errore durante l\'importazione del PDF.');
    console.error(error);
  } finally {
    uploading.value = false;
  }
};

onMounted(fetchOrders);
</script>

<template>
  <div class="home-container">
    <section class="hero">
      <h1>Benvenuto nel Sistema Gestione Ordini</h1>
    </section>

    <div class="main-content">
      <div class="upload-section">
        <input type="file" ref="fileInput" @change="handleUpload" accept=".pdf" style="display: none" />
        <button class="btn-primary" @click="fileInput?.click()" :disabled="uploading">
          {{ uploading ? 'Elaborazione in corso...' : 'Importa Nuovo PDF Ordine' }}
        </button>
      </div>

      <div v-if="orders.length > 0" class="orders-list">
        <h2>Ordini Recenti</h2>
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
      <div v-else-if="auth.isAuthenticated && !uploading" class="empty-state">
        <p>Non ci sono ordini caricati. Carica il tuo primo PDF!</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.hero {
  text-align: center;
  margin-bottom: 3rem;
}

.hero h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.upload-section {
  display: flex;
  justify-content: center;
  margin-bottom: 3rem;
}

.btn-primary {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 1rem 2rem;
  font-size: 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #3aa876;
}

.btn-primary:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.order-card {
  border: 1px solid #ddd;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  background: #fdfdfd;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #eee;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
}

.polygons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.poly-card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 1rem;
  background: white;
}

.poly-card.mirrored {
  border-left: 5px solid #3498db;
}

.preview-container {
  margin: 1rem 0;
  border: 1px solid #eee;
  border-radius: 4px;
  overflow: hidden;
}

.preview-container img {
  width: 100%;
  display: block;
}

.btn-dxf {
  display: inline-block;
  background: #3498db;
  color: white;
  padding: 0.5rem 1rem;
  text-decoration: none;
  border-radius: 4px;
  font-size: 0.9rem;
}

.holes-list {
  list-style: none;
  padding: 0;
  font-size: 0.85rem;
}

.hole-type {
  font-weight: bold;
  margin-right: 0.5rem;
}

.coords {
  color: #7f8c8d;
  margin-left: 0.5rem;
}

.empty-state {
  text-align: center;
  color: #7f8c8d;
  margin-top: 4rem;
}

.badge {
  background: #3498db;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
}
</style>
