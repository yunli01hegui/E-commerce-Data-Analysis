import { createRouter, createWebHistory } from 'vue-router'
import Layout from './pages/Layout.vue'
import Dashboard from './pages/Dashboard.vue'
import AIPage from './pages/AIPage.vue'
import DataCenter from './pages/DataCenter.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    children: [
      {
        path: '',
        name: 'dashboard',
        component: Dashboard,
      },
      {
        path: 'ai',
        name: 'ai',
        component: AIPage,
      },
      {
        path: 'data',
        name: 'data',
        component: DataCenter,
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
