<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import api from '../api/crud';

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
  technical_preview_path: string | null;
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

const deleteOrder = async (orderId: string) => {
  if (confirm('Eliminare definitivamente questo ordine e tutti i suoi pezzi?')) {
    try {
      await api.orders.delete(orderId);
      fetchOrders();
    } catch (err) {
      console.error('Errore eliminazione ordine:', err);
    }
  }
};

const deletePolygon = async (polyId: string) => {
  if (confirm('Eliminare questo pezzo e tutte le sue lavorazioni?')) {
    try {
      await api.polygons.delete(polyId);
      fetchOrders();
    } catch (err) {
      console.error('Errore eliminazione pezzo:', err);
    }
  }
};

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
      <div class="header-left">
        <h1>Archivio Ordini</h1>
        <p class="subtitle">Consulta e scarica i file DXF per la produzione</p>
      </div>
      <div class="upload-action">
        <input type="file" ref="fileInput" @change="handleUpload" accept=".pdf" style="display: none" />
        <button class="btn btn-primary" @click="fileInput?.click()" :disabled="uploading">
          <span class="icon">{{ uploading ? '⏳' : '📥' }}</span>
          {{ uploading ? 'Elaborazione...' : 'Importa PDF' }}
        </button>
      </div>
    </header>

    <div class="orders-list">
      <div v-for="order in orders" :key="order.id" class="order-card">
        <div class="order-header">
          <div class="order-main-info">
            <div class="order-icon-bg">📦</div>
            <div class="order-title-group">
              <h3>Ordine: {{ order.code }}</h3>
              <span class="order-date">{{ new Date(order.created_at).toLocaleString('it-IT') }}</span>
            </div>
          </div>
          <div class="order-summary-badge">
            {{ order.polygons.length }} Pezzi rilevati
          </div>
          <button class="btn btn-danger btn-small" @click="deleteOrder(order.id)">🗑️ Elimina Ordine</button>
        </div>

        <div class="polygons-grid">
          <div v-for="poly in order.polygons" :key="poly.id" class="poly-card" :class="{ mirrored: poly.is_mirrored }">
            <div class="poly-header">
              <h4>{{ poly.label }}</h4>
              <div class="poly-header-actions">
                <span v-if="poly.is_mirrored" class="badge-mirrored">Specchiato</span>
                <button class="btn btn-small btn-danger" @click="deletePolygon(poly.id)" title="Elimina Pezzo">🗑️</button>
              </div>
            </div>

            <div class="poly-specs">
              <span class="spec-item">📐 {{ poly.width_mm }}x{{ poly.height_mm }} mm</span>
              <span class="spec-item">📏 Sp: {{ poly.thickness_mm }}mm</span>
              <span class="spec-item">💎 {{ poly.material }}</span>
            </div>

            <div class="previews-comparison">
              <div class="preview-box">
                <span class="preview-label">Originale PDF</span>
                <div class="preview-container">
                  <img :src="'/api/v1/outputs/' + poly.preview_path" alt="Preview PDF" />
                </div>
              </div>

              <div class="preview-box" v-if="poly.technical_preview_path">
                <span class="preview-label">Anteprima Tecnica (DXF)</span>
                <div class="preview-container tech">
                  <img :src="'/api/v1/outputs/' + poly.technical_preview_path" alt="Anteprima Tecnica" />
                </div>
              </div>
            </div>

            <div class="card-actions">
              <a :href="'/api/v1/outputs/' + poly.dxf_path" download class="btn-dxf">
                <span class="icon">💾</span> Scarica DXF
              </a>
            </div>

            <div class="lavorazioni-section">
              <div class="section-divider">
                <span>Lavorazioni ({{ poly.holes.length }})</span>
              </div>
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
              <div v-if="poly.holes.length === 0" class="empty-holes">Nessuna lavorazione interna.</div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="orders.length === 0" class="empty-orders bg-card">
        <div class="empty-icon">📭</div>
        <h2>Nessun ordine trovato</h2>
        <p>Inizia importando un file PDF con le specifiche tecniche.</p>
        <button class="btn btn-outline" @click="fileInput?.click()">Sfoglia i file</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.orders-view {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3.5rem;
}

.header-left h1 {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  color: white;
  letter-spacing: -0.5px;
}

.subtitle {
  color: var(--text-muted);
  font-size: 1.1rem;
}

.btn-primary {
  padding: 0.85rem 1.75rem;
  font-size: 1rem;
  font-weight: 700;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.2);
}

.order-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 2.5rem;
  margin-bottom: 4rem;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
  transition: all 0.3s;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}

.order-main-info {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.order-icon-bg {
  width: 48px;
  height: 48px;
  background: var(--bg-dark);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  border: 1px solid var(--border);
}

.order-title-group h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
}

.order-date {
  font-size: 0.9rem;
  color: var(--text-muted);
  font-weight: 500;
}

.order-summary-badge {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-main);
  padding: 0.5rem 1.25rem;
  border-radius: 100px;
  font-size: 0.9rem;
  font-weight: 600;
  border: 1px solid var(--border);
}

.polygons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 2.5rem;
}

.poly-card {
  background: var(--bg-dark);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  transition: all 0.2s;
}

.poly-card:hover {
  border-color: #555;
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.poly-card.mirrored {
  border-top: 5px solid var(--primary);
}

.poly-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.poly-header h4 {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 700;
  color: white;
}

.poly-header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.badge-mirrored {
  background: rgba(66, 185, 131, 0.1);
  color: var(--primary);
  padding: 4px 12px;
  border-radius: 100px;
  font-size: 0.8rem;
  font-weight: 700;
  border: 1px solid rgba(66, 185, 131, 0.2);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.poly-specs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.75rem;
}

.spec-item {
  background: rgba(255, 255, 255, 0.03);
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-muted);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.previews-comparison {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.preview-box {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.preview-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.preview-container {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: inset 0 2px 8px rgba(0,0,0,0.1);
  border: 1px solid rgba(0,0,0,0.05);
}

.preview-container.tech {
  background: #f8f9fa;
  border: 1px dashed #ccc;
}

.preview-container img {
  max-width: 100%;
  max-height: 100%;
  display: block;
  object-fit: contain;
}

.card-actions {
  margin-bottom: 2rem;
}

.btn-dxf {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  background: #2a2a2a;
  color: white;
  text-decoration: none;
  padding: 0.85rem;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 700;
  transition: all 0.2s;
  border: 1px solid #333;
}

.btn-dxf:hover {
  background: #333;
  border-color: var(--primary);
  color: var(--primary);
}

.section-divider {
  display: flex;
  align-items: center;
  margin-bottom: 1.25rem;
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.section-divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--border);
  margin-left: 1rem;
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
  padding: 0.75rem 0;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.holes-list li:first-child { border-top: none; }

.hole-info {
  display: flex;
  flex-direction: column;
}

.hole-type {
  font-size: 0.95rem;
  font-weight: 700;
  color: #efefef;
}

.hole-dims {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 500;
}

.coords {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: var(--primary);
  opacity: 0.9;
  background: rgba(66, 185, 131, 0.05);
  padding: 2px 8px;
  border-radius: 4px;
}

.empty-holes {
  text-align: center;
  color: var(--text-muted);
  font-size: 0.9rem;
  font-style: italic;
  padding: 1rem 0;
}

.empty-orders {
  text-align: center;
  padding: 6rem 2rem;
  border-radius: 32px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
}

.empty-orders h2 {
  font-size: 2rem;
  color: white;
  margin-bottom: 1rem;
}

.empty-orders p {
  color: var(--text-muted);
  margin-bottom: 2rem;
  font-size: 1.1rem;
}

@media (max-width: 900px) {
  .polygons-grid {
    grid-template-columns: 1fr;
  }
}
</style>
