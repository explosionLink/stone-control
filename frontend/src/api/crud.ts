import axios from 'axios'

const api = {
  auth: {
    me: () => axios.get('/api/v1/auth/me'),
    roles: () => axios.get('/api/v1/auth/me/roles'),
  },
  users: {
    list: () => axios.get('/api/v1/users/'),
    get: (id: string) => axios.get(`/api/v1/users/${id}`),
    create: (data: any) => axios.post('/api/v1/users/', data),
    update: (id: string, data: any) => axios.put(`/api/v1/users/${id}`, data),
    delete: (id: string) => axios.delete(`/api/v1/users/${id}`),
    roles: (id: string) => axios.get(`/api/v1/users/${id}/roles`),
    assignRole: (data: { user_id: string, role_id: string }) => axios.post('/api/v1/users/assign-role', data),
    unassignRole: (userId: string, roleId: string) => axios.delete(`/api/v1/users/${userId}/roles/${roleId}`),
  },
  roles: {
    list: () => axios.get('/api/v1/roles/'),
    get: (id: string) => axios.get(`/api/v1/roles/${id}`),
    create: (data: any) => axios.post('/api/v1/roles/', data),
    update: (id: string, data: any) => axios.put(`/api/v1/roles/${id}`, data),
    delete: (id: string) => axios.delete(`/api/v1/roles/${id}`),
  },
  clients: {
    list: () => axios.get('/api/v1/clients/'),
    get: (id: string) => axios.get(`/api/v1/clients/${id}`),
    create: (data: any) => axios.post('/api/v1/clients/', data),
    update: (id: string, data: any) => axios.patch(`/api/v1/clients/${id}`, data),
    delete: (id: string) => axios.delete(`/api/v1/clients/${id}`),
  },
  holeLibrary: {
    list: () => axios.get('/api/v1/hole-library/'),
    get: (id: string) => axios.get(`/api/v1/hole-library/${id}`),
    create: (data: any) => axios.post('/api/v1/hole-library/', data),
    update: (id: string, data: any) => axios.patch(`/api/v1/hole-library/${id}`, data),
    delete: (id: string) => axios.delete(`/api/v1/hole-library/${id}`),
  },
  orders: {
    list: () => axios.get('/api/v1/orders/'),
    get: (id: string) => axios.get(`/api/v1/orders/${id}`),
    import: (formData: FormData) => axios.post('/api/v1/orders/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    delete: (id: string) => axios.delete(`/api/v1/orders/${id}`),
  },
  polygons: {
    get: (id: string) => axios.get(`/api/v1/polygons/${id}`),
    update: (id: string, data: any) => axios.patch(`/api/v1/polygons/${id}`, data),
    delete: (id: string) => axios.delete(`/api/v1/polygons/${id}`),
  },
  holes: {
    create: (data: any) => axios.post('/api/v1/holes/', data),
    update: (id: string, data: any) => axios.patch(`/api/v1/holes/${id}`, data),
    delete: (id: string) => axios.delete(`/api/v1/holes/${id}`),
  }
}

export default api
