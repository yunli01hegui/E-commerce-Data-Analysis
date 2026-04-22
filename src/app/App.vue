<template>
  <div class="min-h-screen bg-slate-950 text-slate-50 font-sans antialiased">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { fetchOrderData } from './data/mockData';

onMounted(() => {
  fetchOrderData();
});
</script>

<style>
@import "../styles/tailwind.css";
@import "../styles/theme.css";
@import "../styles/fonts.css";
</style>
