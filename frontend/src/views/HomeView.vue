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
const isDragging = ref(false);
const uploadStatus = ref<{ message: string; type: 'success' | 'error' | '' }>({ message: '', type: '' });

const fetchOrders = async () => {
  try {
    const response = await axios.get('/api/v1/orders/');
    orders.value = response.data;
  } catch (error: any) {
    console.error('Errore nel recupero ordini:', error);
  }
};

const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  uploading.value = true;
  uploadStatus.value = { message: 'Elaborazione del PDF in corso...', type: '' };

  try {
    await axios.post('/api/v1/orders/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    uploadStatus.value = { message: 'Importazione completata con successo!', type: 'success' };
    fetchOrders();
  } catch (error: any) {
    uploadStatus.value = {
      message: error.response?.data?.detail || 'Errore durante l\'importazione del PDF.',
      type: 'error'
    };
    console.error(error);
  } finally {
    uploading.value = false;
    setTimeout(() => {
      uploadStatus.value = { message: '', type: '' };
    }, 5000);
  }
};

const handleUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) await uploadFile(file);
};

const handleDrop = async (event: DragEvent) => {
  isDragging.value = false;
  const file = event.dataTransfer?.files[0];
  if (file && file.type === 'application/pdf') {
    await uploadFile(file);
  } else if (file) {
    uploadStatus.value = { message: 'Per favore, carica solo file PDF.', type: 'error' };
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
      <div
        class="upload-section"
        :class="{ dragging: isDragging }"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
      >
        <div class="upload-box" @click="fileInput?.click()">
          <input type="file" ref="fileInput" @change="handleUpload" accept=".pdf" style="display: none" />
          <div v-if="!uploading" class="upload-content">
            <span class="upload-icon">📄</span>
            <p>Trascina qui il PDF dell'ordine o <strong>clicca per sfogliare</strong></p>
          </div>
          <div v-else class="upload-progress">
            <div class="spinner"></div>
            <p>Elaborazione del PDF in corso...</p>
          </div>
        </div>
      </div>

      <div v-if="uploadStatus.message" class="status-alert" :class="uploadStatus.type">
        {{ uploadStatus.message }}
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
  margin-bottom: 3rem;
  border: 2px dashed #ccc;
  border-radius: 12px;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.upload-section.dragging {
  border-color: #42b983;
  background: #eafaf1;
  transform: scale(1.02);
}

.upload-box {
  padding: 3rem;
  text-align: center;
  cursor: pointer;
}

.upload-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
}

.upload-content p {
  font-size: 1.1rem;
  color: #666;
}

.upload-content strong {
  color: #42b983;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #42b983;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.status-alert {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  text-align: center;
}

.status-alert.success {
  background-color: #eafaf1;
  color: #27ae60;
  border: 1px solid #27ae60;
}

.status-alert.error {
  background-color: #fdf2f2;
  color: #e74c3c;
  border: 1px solid #e74c3c;
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
