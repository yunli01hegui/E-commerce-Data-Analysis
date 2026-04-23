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
  // 捕获所有未定义的路径并重定向到主页
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
