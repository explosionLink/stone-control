<script setup lang="ts">
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="app-layout">
    <header class="app-header">
      <div class="nav-container">
        <div class="brand">
          <RouterLink to="/" class="logo">
            <span class="logo-icon">💎</span>
            <span class="logo-text">Stone Control</span>
          </RouterLink>
        </div>
        <nav class="nav-links">
          <RouterLink to="/">Dashboard</RouterLink>
          <template v-if="auth.isAuthenticated">
            <RouterLink to="/orders">Ordini</RouterLink>
            <RouterLink to="/library">Libreria Fori</RouterLink>
            <div class="user-menu">
              <RouterLink to="/profile" class="profile-link">
                <span class="user-icon">👤</span>
                {{ auth.user?.email?.split('@')[0] }}
              </RouterLink>
              <button @click="handleLogout" class="btn-logout">Esci</button>
            </div>
          </template>
          <template v-else>
            <RouterLink to="/login">Accedi</RouterLink>
            <RouterLink to="/register" class="btn-register">Registrati</RouterLink>
          </template>
          <RouterLink to="/about">About</RouterLink>
        </nav>
      </div>
    </header>

    <main class="app-main">
      <div class="content-container">
        <RouterView />
      </div>
    </main>

    <footer class="app-footer">
      <p>&copy; 2024 Stone Control - Gestione Ordini Marmi e Graniti</p>
    </footer>
  </div>
</template>

<style>
/* Reset globale e stili base scuri */
:root {
  --bg-dark: #121212;
  --bg-card: #1e1e1e;
  --bg-nav: #181818;
  --primary: #42b983;
  --primary-hover: #3aa876;
  --text-main: #e0e0e0;
  --text-muted: #a0a0a0;
  --border: #333;
  --danger: #ff5252;
}

body {
  margin: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: var(--bg-dark);
  color: var(--text-main);
  -webkit-font-smoothing: antialiased;
}

* {
  box-sizing: border-box;
}
</style>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background-color: var(--bg-nav);
  border-bottom: 1px solid var(--border);
  padding: 0.75rem 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.nav-container {
  width: 100%;
  padding: 0 3%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand .logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: white;
}

.logo-icon {
  font-size: 1.5rem;
}

.logo-text {
  font-weight: 700;
  font-size: 1.25rem;
  letter-spacing: -0.5px;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.nav-links a {
  color: var(--text-muted);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  transition: color 0.2s;
}

.nav-links a:hover,
.nav-links a.router-link-active {
  color: var(--primary);
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-left: 1rem;
  border-left: 1px solid var(--border);
}

.profile-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-icon {
  font-size: 1.1rem;
}

.btn-logout {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-muted);
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.btn-logout:hover {
  border-color: var(--danger);
  color: var(--danger);
}

.btn-register {
  background-color: var(--primary);
  color: white !important;
  padding: 0.5rem 1rem;
  border-radius: 6px;
}

.btn-register:hover {
  background-color: var(--primary-hover);
}

.app-main {
  flex: 1;
  padding: 2rem 0;
}

.content-container {
  width: 100%;
  padding: 0 3%;
}

.app-footer {
  padding: 2rem;
  text-align: center;
  border-top: 1px solid var(--border);
  background-color: var(--bg-nav);
  color: var(--text-muted);
  font-size: 0.85rem;
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 1rem;
  }

  .nav-links {
    font-size: 0.85rem;
    gap: 1rem;
  }
}
</style>
