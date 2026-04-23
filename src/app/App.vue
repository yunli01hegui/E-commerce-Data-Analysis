<template>
  <div class="min-h-screen bg-slate-950 text-slate-50 font-sans antialiased">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { fetchOrderData } from './data/mockData';

const router = useRouter();

onMounted(() => {
  fetchOrderData();
  // 强制每次加载应用（包括刷新）都回到数据大屏
  router.push('/');
});
</script>

<style>
@import "../styles/tailwind.css";
@import "../styles/theme.css";
@import "../styles/fonts.css";
</style>
