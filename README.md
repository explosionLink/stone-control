# Stone Control - Gestione Ordini Cucina (PDF to DXF)

Questo progetto è una piattaforma full-stack per la gestione di ordini tecnici di top cucina. Permette di importare file PDF, estrarre automaticamente dimensioni e geometrie (poligoni e fori) e generare file DXF pronti per il CAD/CAM (SolidWorks, ecc.).

## Struttura del Progetto
- `backend/`: FastAPI application, elaborazione PDF (pdfplumber, shapely, ezdxf).
- `frontend/`: Vue 3 application (Vite, Pinia, TypeScript).
- `SQL/`: Script SQL per l'inizializzazione manuale del database su Supabase.

---

## Prerequisiti
- **Python 3.12+**
- **Node.js 22+**
- **Account Supabase** (con un progetto attivo)

---

## Configurazione Backend

### 1. Installazione
Dalla radice del progetto:
```bash
# Crea un ambiente virtuale
python -m venv venv

# Attiva l'ambiente virtuale
# Su Windows:
venv\Scripts\activate
# Su Linux/macOS:
source venv/bin/activate

# Installa le dipendenze
pip install -r backend/requirements.txt
```

### 2. Variabili d'Ambiente (.env)
Crea un file `.env` nella cartella `backend/` con i seguenti dati (recuperabili dal pannello Supabase):
```env
SUPABASE_URL=tua_url_supabase
SUPABASE_ANON_KEY=tua_anon_key
SUPABASE_SERVICE_KEY=tua_service_key
DATABASE_URL=postgresql+asyncpg://postgres:tua_password@db.xxxx.supabase.co:5432/postgres
ENV=dev
```

### 3. Database e Migrazioni
Assicurati di essere nella cartella `backend/`:
```bash
cd backend

# Esegui le migrazioni per creare le tabelle
# Su Linux/macOS (bash):
export PYTHONPATH=$PYTHONPATH:$(pwd)
# Su Windows (PowerShell):
$env:PYTHONPATH += ";$PWD"
# Su Windows (CMD):
set PYTHONPATH=%PYTHONPATH%;%cd%

alembic upgrade head
```

### 4. Avvio Backend
Sempre dalla cartella `backend/`:
```bash
uvicorn app.main:app --reload --port 8000
```
L'API sarà disponibile su `http://localhost:8000`.

---

## Configurazione Frontend

### 1. Installazione
Dalla radice del progetto:
```bash
cd frontend
npm install
```

### 2. Avvio Frontend
```bash
npm run dev
```
L'applicazione sarà disponibile su `http://localhost:5173`. Il proxy è già configurato per inoltrare le chiamate `/api` al backend su porta 8000.

---

## Funzionalità PDF to DXF
- **Upload**: Carica un PDF tecnico nella sezione "Ordini".
- **Parsing**: Il sistema legge il testo (es. `1950 x 20 x 638`), identifica i contorni e i fori interni.
- **Output**: Verrà generata un'anteprima PNG e un file DXF nella cartella `backend/outputs/`.
- **Download**: Scarica il file DXF direttamente dalla dashboard.

---

## Note per lo Sviluppo
- **Vetur/VS Code**: Se ricevi errori relativi a `tsconfig.json`, assicurati di aprire VS Code direttamente nella cartella `frontend/` o aggiungi un file `tsconfig.json` nella radice se desideri gestire il progetto come monorepo.
- **Storage**: Attualmente i file sono salvati nel filesystem locale (`backend/imports` e `backend/outputs`). Per la produzione, si consiglia l'integrazione con Supabase Storage.
