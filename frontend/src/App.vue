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
  <header class="app-header">
    <nav>
      <RouterLink to="/">Home</RouterLink>
      <template v-if="auth.isAuthenticated">
        <RouterLink to="/orders">Ordini</RouterLink>
        <RouterLink to="/library">Libreria Fori</RouterLink>
        <RouterLink to="/profile">Profilo</RouterLink>
        <a href="#" @click.prevent="handleLogout">Logout</a>
      </template>
      <template v-else>
        <RouterLink to="/login">Accedi</RouterLink>
        <RouterLink to="/register">Registrati</RouterLink>
      </template>
      <RouterLink to="/about">About</RouterLink>
    </nav>
  </header>

  <main class="app-main">
    <RouterView />
  </main>
</template>

<style scoped>
.app-header {
  padding: 1rem 2rem;
  background-color: #2c3e50;
  color: white;
}

nav {
  display: flex;
  gap: 1rem;
  align-items: center;
}

nav a {
  color: #ecf0f1;
  text-decoration: none;
  font-weight: 500;
}

nav a.router-link-exact-active {
  color: #42b983;
}

.app-main {
  padding: 1rem;
}
</style>
