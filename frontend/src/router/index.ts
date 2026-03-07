import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/library',
      name: 'library',
      component: () => import('../views/HoleLibraryView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/orders',
      name: 'orders',
      component: () => import('../views/OrdersView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/orders/:id',
      name: 'order-detail',
      component: () => import('../views/OrderDetailView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/clients',
      name: 'clients',
      component: () => import('../views/ClientsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/users',
      name: 'users',
      component: () => import('../views/UsersView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/roles',
      name: 'roles',
      component: () => import('../views/RolesView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
    },
    {
      path: '/mfa-verify',
      name: 'mfa-verify',
      component: () => import('../views/MfaVerifyView.vue'),
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next('/login')
  }

  if (to.meta.requiresAdmin) {
    // Verifichiamo se l'utente ha il ruolo admin
    // Nota: in un'app reale dovremmo controllare i claims del token o chiamare un endpoint /me/roles
    // Per ora usiamo una logica basata sull'utente corrente nello store se disponibile
    const isAdmin = auth.user?.app_metadata?.roles?.includes('admin') ||
                    auth.user?.user_metadata?.role === 'admin';

    if (!isAdmin) {
      // Potremmo anche fare una chiamata API veloce per sicurezza se lo store non è certo
      try {
        const res = await axios.get('/api/v1/auth/me/roles');
        if (res.data.roles.includes('admin')) {
          return next();
        }
      } catch (e) {
        console.error("Errore verifica ruoli admin", e);
      }
      alert("Accesso negato: richiesti privilegi di amministratore.");
      return next('/');
    }
  }

  next()
})

export default router
