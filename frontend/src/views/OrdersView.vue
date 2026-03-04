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
  } catch (error: any) {
    console.error('Errore nel recupero ordini:', error);
    if (error.response?.status === 401) {
      alert('Sessione scaduta o non valida. Effettua nuovamente il login.');
    }
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
  <div class="orders-view">
    <header class="view-header">
      <h1>Archivio Ordini</h1>
      <div class="upload-action">
        <input type="file" ref="fileInput" @change="handleUpload" accept=".pdf" style="display: none" />
        <button class="btn-primary" @click="fileInput?.click()" :disabled="uploading">
          {{ uploading ? 'Elaborazione...' : '+ Importa PDF' }}
        </button>
      </div>
    </header>

    <div class="orders-list">
      <div v-for="order in orders" :key="order.id" class="order-card">
        <div class="order-header">
          <div class="order-main-info">
            <span class="order-icon">📦</span>
            <h3>Ordine: {{ order.code }}</h3>
          </div>
          <span class="order-date">{{ new Date(order.created_at).toLocaleString() }}</span>
        </div>

        <div class="polygons-grid">
          <div v-for="poly in order.polygons" :key="poly.id" class="poly-card" :class="{ mirrored: poly.is_mirrored }">
            <div class="poly-header">
              <h4>{{ poly.label }}</h4>
              <span v-if="poly.is_mirrored" class="badge">Specchiato</span>
            </div>

            <div class="poly-specs">
              <span class="spec-item">📐 {{ poly.width_mm }} x {{ poly.height_mm }} mm</span>
              <span class="spec-item">📏 Sp: {{ poly.thickness_mm }}mm</span>
              <span class="spec-item">💎 {{ poly.material }}</span>
            </div>

            <div class="preview-container">
              <img :src="'/api/v1/outputs/' + poly.preview_path" alt="Preview" />
            </div>

            <div class="card-actions">
              <a :href="'/api/v1/outputs/' + poly.dxf_path" download class="btn-dxf">
                <span class="icon">💾</span> Scarica DXF
              </a>
            </div>

            <div class="lavorazioni-section">
              <h5>Lavorazioni ({{ poly.holes.length }})</h5>
              <ul class="holes-list">
                <li v-for="hole in poly.holes" :key="hole.id">
                  <div class="hole-info">
                    <span class="hole-type">{{ hole.type }}</span>
                    <span class="hole-dims">
                      <template v-if="hole.diameter_mm">Ø{{ hole.diameter_mm }} p.{{ hole.depth_mm }}</template>
                      <template v-else>{{ hole.width_mm.toFixed(0) }}x{{ hole.height_mm.toFixed(0) }}</template>
                    </span>
                  </div>
                  <span class="coords">X:{{ hole.x_mm.toFixed(1) }} Y:{{ hole.y_mm.toFixed(1) }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.orders-view {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2.5rem;
}

.view-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
}

.btn-primary {
  background-color: var(--primary);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
}

.order-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 3rem;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.order-main-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.order-icon { font-size: 1.25rem; }

.order-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: white;
}

.order-date {
  font-size: 0.9rem;
  color: var(--text-muted);
}

.polygons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 2rem;
}

.poly-card {
  background: var(--bg-dark);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
}

.poly-card.mirrored {
  border-top: 4px solid var(--primary);
}

.poly-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.poly-header h4 {
  margin: 0;
  font-size: 1.1rem;
  color: white;
}

.badge {
  background: rgba(66, 185, 131, 0.1);
  color: var(--primary);
  padding: 2px 8px;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid rgba(66, 185, 131, 0.2);
}

.poly-specs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.spec-item {
  background: rgba(255, 255, 255, 0.03);
  padding: 4px 8px;
  border-radius: 4px;
}

.preview-container {
  background: white;
  border-radius: 8px;
  padding: 0.75rem;
  margin-bottom: 1.25rem;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-container img {
  max-width: 100%;
  max-height: 250px;
  display: block;
}

.card-actions {
  margin-bottom: 1.5rem;
}

.btn-dxf {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: #333;
  color: white;
  text-decoration: none;
  padding: 0.6rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-dxf:hover {
  background: #444;
}

.lavorazioni-section h5 {
  margin: 0 0 0.75rem;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
}

.holes-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.holes-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.hole-info {
  display: flex;
  flex-direction: column;
}

.hole-type {
  font-size: 0.85rem;
  font-weight: 600;
  color: #ddd;
}

.hole-dims {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.coords {
  font-family: monospace;
  font-size: 0.75rem;
  color: var(--primary);
  opacity: 0.8;
}
</style>
