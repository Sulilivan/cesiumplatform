import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../components/CesiumViewer.vue'), // 确保指向你的组件
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../views/AdminView.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  console.log(`Routing to ${to.path}, Auth Required: ${requiresAuth}, Token: ${!!token}`);
  
  // 检查该路由是否需要登录权限
  if (requiresAuth) {
    if (!token) {
      console.log('No token found, redirecting to login');
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } else {
    // 如果已经登录且访问登录页，跳转到首页
    if (to.path === '/login' && token) {
      next('/');
    } else {
      next()
    }
  }
})

export default router
