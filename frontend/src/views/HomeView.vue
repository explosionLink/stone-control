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
          <span class="stat-value">{{ orders.length > 0 && orders[0] ? orders[0].code : '-' }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">Utente</span>
          <span class="stat-value user-name">{{ auth.user?.email ? auth.user.email.split('@')[0] : 'Ospite' }}</span>
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
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

.dashboard-header {
  margin-bottom: 3rem;
}

.dashboard-header h1 {
  font-size: 2.25rem;
  font-weight: 800;
  margin-bottom: 2rem;
  color: white;
  letter-spacing: -0.5px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: var(--bg-card);
  padding: 1.75rem;
  border-radius: 16px;
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
  border-color: #444;
}

.stat-label {
  color: var(--text-muted);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary);
}

.user-name {
  color: white;
  text-transform: capitalize;
}

/* Upload Section */
.upload-container {
  margin-bottom: 4rem;
}

.drop-zone {
  background: var(--bg-card);
  border: 2px dashed var(--border);
  border-radius: 20px;
  padding: 4rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}

.drop-zone:hover, .drop-zone.dragging {
  border-color: var(--primary);
  background: rgba(66, 185, 131, 0.03);
  transform: scale(1.005);
}

.icon-circle {
  width: 80px;
  height: 80px;
  background: var(--bg-dark);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  margin: 0 auto 2rem;
  border: 1px solid var(--border);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.drop-zone p {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  color: white;
}

.browse-link {
  color: var(--text-muted);
  font-size: 1rem;
}

.upload-loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(66, 185, 131, 0.1);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.status-toast {
  margin-top: 1.5rem;
  padding: 1.25rem;
  border-radius: 12px;
  text-align: center;
  font-weight: 600;
  font-size: 1rem;
  animation: fadeIn 0.3s ease-in;
}

.status-toast.success { background: rgba(39, 174, 96, 0.1); color: #2ecc71; border: 1px solid rgba(39, 174, 96, 0.2); }
.status-toast.error { background: rgba(231, 76, 60, 0.1); color: #e74c3c; border: 1px solid rgba(231, 76, 60, 0.2); }

/* Orders Section */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.section-header h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
}

.view-all {
  text-decoration: none;
  color: var(--primary);
  font-weight: 600;
  font-size: 1rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  background: rgba(66, 185, 131, 0.05);
  transition: all 0.2s;
}

.view-all:hover {
  background: rgba(66, 185, 131, 0.1);
  transform: translateX(4px);
}

.orders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
}

.order-dashboard-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.75rem;
  transition: all 0.2s ease-out;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.order-dashboard-card:hover {
  transform: translateY(-6px);
  border-color: #555;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
}

.order-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.75rem;
}

.order-code {
  font-weight: 800;
  font-size: 1.25rem;
  color: white;
}

.order-date {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.order-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.poly-count {
  font-size: 1rem;
  color: var(--text-muted);
  font-weight: 500;
}

.poly-previews {
  display: flex;
  align-items: center;
}

.mini-preview {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  background: white;
  margin-left: -12px;
  border: 3px solid var(--bg-card);
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.mini-preview:first-child { margin-left: 0; }

.mini-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.more-count {
  font-size: 0.85rem;
  margin-left: 0.75rem;
  color: var(--text-muted);
  font-weight: 600;
}

.empty-dashboard {
  text-align: center;
  padding: 5rem;
  background: var(--bg-card);
  border-radius: 20px;
  color: var(--text-muted);
  border: 1px solid var(--border);
}
</style>
