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
            <RouterLink to="/clients">Clienti</RouterLink>
            <RouterLink to="/users">Utenti</RouterLink>
            <RouterLink to="/roles">Ruoli</RouterLink>
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
      <div class="footer-content">
        <p>&copy; 2024 Stone Control - Gestione Ordini Marmi e Graniti</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background-color: var(--bg-nav);
  border-bottom: 1px solid var(--border);
  padding: 0.85rem 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
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
  font-size: 1.35rem;
  letter-spacing: -0.5px;
}

.nav-links {
  display: flex;
  gap: 1.75rem;
  align-items: center;
}

.nav-links a {
  color: var(--text-muted);
  text-decoration: none;
  font-weight: 500;
  font-size: 1rem;
  transition: all 0.2s;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.nav-links a:hover,
.nav-links a.router-link-active {
  color: var(--primary);
  background-color: rgba(66, 185, 131, 0.05);
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-left: 1.25rem;
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
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-logout:hover {
  border-color: var(--danger);
  color: var(--danger);
  background-color: rgba(255, 82, 82, 0.05);
}

.btn-register {
  background-color: var(--primary);
  color: white !important;
  padding: 0.5rem 1rem !important;
  border-radius: 6px;
}

.btn-register:hover {
  background-color: var(--primary-hover);
  color: white !important;
}

.app-main {
  flex: 1;
  padding: 2.5rem 0;
  width: 100%;
}

.content-container {
  width: 100%;
  padding: 0 3%;
}

.app-footer {
  padding: 2.5rem 0;
  border-top: 1px solid var(--border);
  background-color: var(--bg-nav);
  color: var(--text-muted);
  font-size: 0.9rem;
}

.footer-content {
  width: 100%;
  padding: 0 3%;
  text-align: center;
}

@media (max-width: 900px) {
  .nav-container {
    flex-direction: column;
    gap: 1.25rem;
  }

  .nav-links {
    font-size: 0.9rem;
    gap: 1rem;
    flex-wrap: wrap;
    justify-content: center;
  }

  .user-menu {
    border-left: none;
    padding-left: 0;
    margin-top: 0.5rem;
  }
}
</style>
