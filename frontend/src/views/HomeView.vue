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
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>Dashboard Operativa</h1>
      <div class="stats-row">
        <div class="stat-card">
          <span class="stat-label">Ordini Totali</span>
          <span class="stat-value">{{ orders.length }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">Ultimo Ordine</span>
          <span class="stat-value">{{ orders.length > 0 ? orders[0].code : '-' }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">Utente</span>
          <span class="stat-value user-name">{{ auth.user?.email?.split('@')[0] }}</span>
        </div>
      </div>
    </header>

    <div class="dashboard-content">
      <!-- Upload Section -->
      <section class="upload-container">
        <div
          class="drop-zone"
          :class="{ dragging: isDragging }"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
          @click="fileInput?.click()"
        >
          <input type="file" ref="fileInput" @change="handleUpload" accept=".pdf" style="display: none" />
          <div v-if="!uploading" class="drop-zone-content">
            <div class="icon-circle">📄</div>
            <p>Trascina il PDF dell'ordine qui</p>
            <span class="browse-link">o clicca per sfogliare i file</span>
          </div>
          <div v-else class="upload-loader">
            <div class="spinner"></div>
            <p>Elaborazione ordine in corso...</p>
          </div>
        </div>

        <div v-if="uploadStatus.message" class="status-toast" :class="uploadStatus.type">
          {{ uploadStatus.message }}
        </div>
      </section>

      <!-- Orders Section -->
      <section class="orders-section">
        <div class="section-header">
          <h2>Ordini Recenti</h2>
          <RouterLink to="/orders" class="view-all">Vedi tutti &rarr;</RouterLink>
        </div>

        <div v-if="orders.length > 0" class="orders-grid">
          <div v-for="order in orders.slice(0, 4)" :key="order.id" class="order-dashboard-card">
            <div class="order-info">
              <span class="order-code">{{ order.code }}</span>
              <span class="order-date">{{ new Date(order.created_at).toLocaleDateString() }}</span>
            </div>
            <div class="order-summary">
              <span class="poly-count">{{ order.polygons.length }} pezzi</span>
              <div class="poly-previews">
                <div v-for="poly in order.polygons.slice(0, 3)" :key="poly.id" class="mini-preview">
                  <img :src="'/api/v1/outputs/' + poly.preview_path" />
                </div>
                <div v-if="order.polygons.length > 3" class="more-count">+{{ order.polygons.length - 3 }}</div>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="!uploading" class="empty-dashboard">
          <p>Nessun ordine presente nel sistema.</p>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.dashboard-header {
  margin-bottom: 2.5rem;
}

.dashboard-header h1 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: white;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: var(--bg-card);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-label {
  color: var(--text-muted);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary);
}

.user-name {
  color: white;
  text-transform: capitalize;
}

/* Upload Section */
.upload-container {
  margin-bottom: 3rem;
}

.drop-zone {
  background: var(--bg-card);
  border: 2px dashed var(--border);
  border-radius: 16px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.drop-zone:hover, .drop-zone.dragging {
  border-color: var(--primary);
  background: rgba(66, 185, 131, 0.05);
  transform: translateY(-2px);
}

.icon-circle {
  width: 64px;
  height: 64px;
  background: var(--bg-dark);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin: 0 auto 1.5rem;
  border: 1px solid var(--border);
}

.drop-zone p {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.browse-link {
  color: var(--text-muted);
  font-size: 0.95rem;
}

.upload-loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(66, 185, 131, 0.1);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.status-toast {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
}

.status-toast.success { background: rgba(39, 174, 96, 0.1); color: #2ecc71; border: 1px solid rgba(39, 174, 96, 0.2); }
.status-toast.error { background: rgba(231, 76, 60, 0.1); color: #e74c3c; border: 1px solid rgba(231, 76, 60, 0.2); }

/* Orders Section */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.5rem;
}

.view-all {
  text-decoration: none;
  color: var(--primary);
  font-weight: 500;
  font-size: 0.95rem;
}

.orders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.order-dashboard-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.25rem;
  transition: transform 0.2s;
}

.order-dashboard-card:hover {
  transform: translateY(-4px);
  border-color: #444;
}

.order-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.25rem;
}

.order-code {
  font-weight: 700;
  font-size: 1.1rem;
  color: white;
}

.order-date {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.order-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.poly-count {
  font-size: 0.9rem;
  color: var(--text-muted);
}

.poly-previews {
  display: flex;
  align-items: center;
}

.mini-preview {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  background: white;
  margin-left: -8px;
  border: 2px solid var(--bg-card);
  overflow: hidden;
}

.mini-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.more-count {
  font-size: 0.75rem;
  margin-left: 0.5rem;
  color: var(--text-muted);
}

.empty-dashboard {
  text-align: center;
  padding: 3rem;
  background: var(--bg-card);
  border-radius: 12px;
  color: var(--text-muted);
}
</style>
