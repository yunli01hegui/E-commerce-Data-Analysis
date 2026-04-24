<template>
  <div class="min-h-screen bg-slate-900">
    <!-- 顶部导航栏 -->
    <nav class="bg-slate-800 border-b border-slate-700">
      <div class="max-w-7xl mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-8">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                <BarChart3 class="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 class="text-xl font-bold text-white">电商数据分析平台</h1>
                <p class="text-xs text-slate-400">AI-Powered Analytics</p>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <router-link
                to="/"
                class="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors"
                exact-active-class="bg-blue-500 text-white"
                :class="$route.path === '/' ? '' : 'text-slate-300 hover:text-white hover:bg-slate-700'"
              >
                <BarChart3 class="w-4 h-4" />
                <span>数据大屏</span>
              </router-link>
              <router-link
                to="/ai"
                class="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors"
                active-class="bg-purple-500 text-white"
                :class="$route.path === '/ai' ? '' : 'text-slate-300 hover:text-white hover:bg-slate-700'"
              >
                <Sparkles class="w-4 h-4" />
                <span>AI 智能分析</span>
              </router-link>
              <router-link
                to="/data"
                class="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors"
                active-class="bg-emerald-500 text-white"
                :class="$route.path === '/data' ? '' : 'text-slate-300 hover:text-white hover:bg-slate-700'"
              >
                <Database class="w-4 h-4" />
                <span>数据中心</span>
              </router-link>
            </div>
          </div>

          <div class="flex items-center gap-4">
            <div class="text-right">
              <div class="text-sm text-slate-400">当前时间</div>
              <div class="text-white font-medium">
                {{ currentTime }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区域 -->
    <main class="max-w-7xl mx-auto px-6 py-8">
      <router-view :key="$route.fullPath" />
    </main>

    <!-- 页脚 -->
    <footer class="mt-12 border-t border-slate-800">
      <div class="max-w-7xl mx-auto px-6 py-6">
        <div class="flex items-center justify-between text-sm text-slate-400">
          <p>© 2026 电商数据分析平台. Powered by DeepSeek AI.</p>
          <div class="flex items-center gap-2">
            <Github class="w-4 h-4" />
            <span>数据可视化与智能分析解决方案</span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { BarChart3, Sparkles, Github, Database } from 'lucide-vue-next';

const currentTime = ref('');

const updateTime = () => {
  currentTime.value = new Date().toLocaleString('zh-CN', { 
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

let timer: number;
onMounted(() => {
  updateTime();
  timer = window.setInterval(updateTime, 1000);
});

onUnmounted(() => {
  clearInterval(timer);
});
</script>
