<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/crud'

const route = useRoute()
const orderId = route.params.id as string
const order = ref<any>(null)
const loading = ref(false)

const fetchOrder = async () => {
  loading.value = true
  try {
    const res = await api.orders.get(orderId)
    order.value = res.data
  } catch (err) {
    console.error('Errore recupero ordine:', err)
  } finally {
    loading.value = false
  }
}

const deleteOrder = async () => {
  if (confirm('Eliminare definitivamente questo ordine?')) {
    try {
      await api.orders.delete(orderId)
      window.location.href = '/orders'
    } catch (err) {
      console.error('Errore eliminazione ordine:', err)
    }
  }
}

const deletePolygon = async (polyId: string) => {
  if (confirm('Eliminare questo pezzo e tutte le sue lavorazioni?')) {
    try {
      await api.polygons.delete(polyId)
      fetchOrder()
    } catch (err) {
      console.error('Errore eliminazione pezzo:', err)
    }
  }
}

const updateHole = async (hole: any) => {
  try {
     // Esempio semplice: apri un prompt o un altro modal per i valori
     const newX = prompt("Nuova coordinata X", hole.x_mm.toString());
     if (newX !== null) {
       await api.holes.update(hole.id, { ...hole, x_mm: parseFloat(newX) });
       fetchOrder();
     }
  } catch (err) {
    console.error('Errore aggiornamento foro:', err);
  }
}

const deleteHole = async (holeId: string) => {
  if (confirm('Eliminare questo foro?')) {
    try {
      await api.holes.delete(holeId)
      fetchOrder()
    } catch (err) {
      console.error('Errore eliminazione foro:', err)
    }
  }
}

const showHoleModal = ref(false)
const currentPolygonId = ref('')
const newHole = ref({
  type: '',
  x_mm: 0,
  y_mm: 0,
  diameter_mm: null,
  width_mm: null,
  height_mm: null
})

const openAddHoleModal = (polyId: string) => {
  currentPolygonId.value = polyId
  newHole.value = { type: 'lavello', x_mm: 0, y_mm: 0, diameter_mm: null, width_mm: null, height_mm: null }
  showHoleModal.value = true
}

const addHole = async () => {
  try {
    await api.holes.create({ ...newHole.value, polygon_id: currentPolygonId.value })
    showHoleModal.value = false
    fetchOrder()
  } catch (err) {
    console.error('Errore aggiunta foro:', err)
  }
}

onMounted(fetchOrder)
</script>

<template>
  <div class="order-detail" v-if="order">
    <div class="view-header">
      <div class="header-left">
        <RouterLink to="/orders" class="back-link">&larr; Torna agli ordini</RouterLink>
        <h1>Dettaglio Ordine: {{ order.code }}</h1>
        <p class="subtitle">Creato il {{ new Date(order.created_at).toLocaleString() }}</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-danger" @click="deleteOrder">🗑️ Elimina Ordine</button>
        <p class="info-text">Per correggere l'ordine, puoi anche re-importare il PDF aggiornato.</p>
      </div>
    </div>

    <div class="polygons-list">
      <div v-for="poly in order.polygons" :key="poly.id" class="poly-card-detailed">
        <div class="poly-main">
          <div class="poly-header-flex">
            <h3>{{ poly.label }}</h3>
            <button class="btn btn-small btn-danger" @click="deletePolygon(poly.id)">🗑️ Elimina Pezzo</button>
          </div>
          <div class="poly-data">
            <div class="data-item"><strong>Dimensioni:</strong> {{ poly.width_mm }} x {{ poly.height_mm }} mm</div>
            <div class="data-item"><strong>Spessore:</strong> {{ poly.thickness_mm }} mm</div>
            <div class="data-item"><strong>Materiale:</strong> {{ poly.material }}</div>
            <div class="data-item"><strong>Specchiato:</strong> {{ poly.is_mirrored ? 'Sì' : 'No' }}</div>
          </div>

          <div class="previews-row">
             <img :src="'/api/v1/outputs/' + poly.preview_path" alt="PDF Preview" class="preview-img" />
             <img v-if="poly.technical_preview_path" :src="'/api/v1/outputs/' + poly.technical_preview_path" alt="Tech Preview" class="preview-img tech" />
          </div>
        </div>

        <div class="poly-holes">
          <h4>Fori / Lavorazioni ({{ poly.holes.length }})</h4>
          <table class="crud-table small">
            <thead>
              <tr>
                <th>Tipo</th>
                <th>X (mm)</th>
                <th>Y (mm)</th>
                <th>Dimensioni</th>
                <th>Azioni</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="hole in poly.holes" :key="hole.id">
                <td>{{ hole.type }}</td>
                <td>{{ hole.x_mm }}</td>
                <td>{{ hole.y_mm }}</td>
                <td>
                   <span v-if="hole.diameter_mm">Ø{{ hole.diameter_mm }}</span>
                   <span v-else>{{ hole.width_mm }}x{{ hole.height_mm }}</span>
                </td>
                <td class="actions">
                   <button class="btn btn-small btn-outline" @click="updateHole(hole)">✏️ Modifica</button>
                   <button class="btn btn-small btn-danger" @click="deleteHole(hole.id)">🗑️ Elimina</button>
                </td>
              </tr>
            </tbody>
          </table>
          <button class="btn small primary mt-1" @click="openAddHoleModal(poly.id)">Aggiungi Foro</button>
        </div>
      </div>
    </div>

    <!-- Hole Modal -->
    <div v-if="showHoleModal" class="modal-overlay">
      <div class="modal-content">
        <h2>Aggiungi Foro</h2>
        <form @submit.prevent="addHole">
          <div class="form-group">
            <label>Tipo</label>
            <input v-model="newHole.type" required />
          </div>
          <div class="form-group">
            <label>X (mm)</label>
            <input type="number" v-model="newHole.x_mm" required />
          </div>
          <div class="form-group">
            <label>Y (mm)</label>
            <input type="number" v-model="newHole.y_mm" required />
          </div>
          <div class="form-group">
            <label>Diametro (mm) - opzionale</label>
            <input type="number" v-model="newHole.diameter_mm" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn" @click="showHoleModal = false">Annulla</button>
            <button type="submit" class="btn primary">Aggiungi</button>
          </div>
        </form>
      </div>
    </div>
  </div>
  <div v-else-if="loading" class="loader">Caricamento ordine...</div>
</template>

<style scoped>
.order-detail { padding: 2rem 0; }
.view-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2rem; }
.poly-header-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.header-actions { display: flex; flex-direction: column; align-items: flex-end; gap: 0.5rem; }
.info-text { font-size: 0.8rem; color: var(--text-muted); font-style: italic; max-width: 300px; text-align: right; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: var(--bg-card); padding: 2rem; border-radius: 12px; width: 100%; max-width: 400px; }
.form-group { margin-bottom: 1rem; display: flex; flex-direction: column; gap: 0.5rem; }
.modal-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1.5rem; }
.back-link { display: block; margin-bottom: 1rem; color: var(--primary); text-decoration: none; font-weight: 600; }
.poly-card-detailed { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 2rem; margin-bottom: 2rem; display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
.previews-row { display: flex; gap: 1rem; margin-top: 1.5rem; }
.preview-img { width: 150px; height: 150px; object-fit: contain; background: white; border-radius: 8px; padding: 0.5rem; }
.preview-img.tech { background: #f0f0f0; border: 1px dashed #ccc; }
.mt-1 { margin-top: 1rem; }

@media (max-width: 1000px) {
  .poly-card-detailed { grid-template-columns: 1fr; }
}
</style>
