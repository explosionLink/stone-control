# Frontend - Vue 3 Project

Progetto frontend sviluppato con **Vue 3**, **Vite**, **TypeScript**, **Pinia** e **Vue Router**.

## Requisiti

- **Node.js**: Versione 24 (specificata nel file `.nvmrc`)
- **Backend**: Assicurati che il backend sia attivo su `http://localhost:8000` per il corretto funzionamento del proxy.

## Setup del Progetto

Prima di iniziare, assicurati di essere nella cartella `frontend` e di usare Node 24:

```sh
cd frontend
nvm use # Se usi nvm, legge la versione da .nvmrc
npm install
```

## Comandi Disponibili

### Sviluppo

Avvia il server di sviluppo con hot-reload e configurazione proxy:

```sh
npm run dev
```

### Build per la Produzione

Esegue il controllo dei tipi e compila i file per la produzione nella cartella `dist`:

```sh
npm run build
```

### Testing

#### Unit Test (Vitest)
```sh
npm run test:unit
```

#### End-to-End Test (Playwright)
```sh
# Installa i browser necessari (solo la prima volta)
npx playwright install

# Esegue i test E2E
npm run test:e2e
```

### Qualità del Codice

#### Linting e Formattazione
```sh
# Esegue ESLint, Oxlint e Prettier per correggere i file
npm run lint
npm run format
```

#### Type-check
```sh
npm run type-check
```

## Configurazione Proxy

Il file `vite.config.ts` è configurato per inoltrare tutte le chiamate che iniziano con `/api` verso `http://localhost:8000`.
Esempio: Una chiamata a `axios.get('/api/users')` nel frontend verrà inoltrata a `http://localhost:8000/users`.

---

## Integrazione Axios

Axios è già installato. Puoi importarlo nei tuoi componenti o servizi:

```typescript
import axios from 'axios'

const fetchData = async () => {
  const response = await axios.get('/api/data')
  return response.data
}
```
