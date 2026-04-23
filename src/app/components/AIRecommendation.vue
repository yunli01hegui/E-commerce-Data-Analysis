<template>
  <div class="space-y-6">
    <!-- 标题 -->
    <div class="bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg p-6 border border-blue-500/20">
      <div class="flex items-center gap-3 mb-2">
        <Sparkles class="w-6 h-6 text-blue-400" />
        <h2 class="text-2xl font-bold text-white">AI 智能分析</h2>
      </div>
      <p class="text-slate-300">基于 DeepSeek 大模型的全站数据深度洞察与智能分析</p>
    </div>

    <!-- 报告类型选择 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
      <button
        v-for="btn in reportButtons"
        :key="btn.type"
        @click="generateReport(btn.type as ReportType)"
        :disabled="loading"
        class="p-5 rounded-2xl border transition-all duration-500 disabled:opacity-50 disabled:cursor-not-allowed text-left relative overflow-hidden group backdrop-blur-xl"
        :class="[
          activeReport === btn.type
            ? `bg-gradient-to-br ${btn.activeGradient} ${btn.activeBorder} ${btn.glowShadow} scale-[1.02] -translate-y-1`
            : `bg-slate-800/40 border-slate-700/60 hover:bg-slate-700/60 hover:border-${btn.theme}-500/40`
        ]"
      >
        <div class="flex items-start justify-between mb-3">
          <div 
            class="p-2.5 rounded-lg transition-all duration-500"
            :class="activeReport === btn.type ? 'bg-white/20' : 'bg-slate-900/40 group-hover:bg-slate-900/60'"
          >
            <component 
              :is="btn.icon" 
              class="w-5 h-5 transition-all duration-500 group-hover:scale-110" 
              :class="activeReport === btn.type ? 'text-white' : btn.iconColor"
            />
          </div>
          <!-- 选中状态的小圆点 -->
          <div 
            v-if="activeReport === btn.type"
            class="w-1.5 h-1.5 rounded-full bg-white animate-pulse shadow-[0_0_8px_rgba(255,255,255,0.8)]"
          ></div>
        </div>

        <h3 
          class="text-lg font-bold mb-1.5 transition-colors"
          :class="activeReport === btn.type ? 'text-white' : 'text-slate-200'"
        >
          {{ btn.title }}
        </h3>
        <p class="text-xs leading-relaxed transition-colors" :class="activeReport === btn.type ? 'text-white/80' : 'text-slate-400'">
          {{ btn.description }}
        </p>
      </button>
    </div>

    <!-- 报告内容 -->
    <div v-if="activeReport" class="bg-slate-800/50 rounded-2xl p-8 border border-slate-700/50 relative backdrop-blur-md">
      <!-- 报告操作与时间展示 -->
      <div v-if="!loading" class="absolute top-4 right-6 flex items-center gap-3">
        <div v-if="reportTime" class="flex items-center gap-1.5 text-slate-500 text-xs font-mono bg-slate-900/50 px-3 py-1 rounded-full border border-slate-700/50">
          <Clock class="w-3.5 h-3.5" />
          报告生成于: {{ reportTime }}
        </div>
        
        <button 
          @click="generateReport(activeReport, true)"
          class="flex items-center gap-1.5 px-3 py-1 bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 text-xs font-bold rounded-full border border-blue-500/30 transition-all active:scale-95"
          title="忽略缓存，重新生成此模块报告"
        >
          <RotateCw class="w-3.5 h-3.5" />
          更新报告
        </button>
      </div>

      <div class="flex items-center justify-between mb-4">
        <h3 class="text-xl font-semibold text-white">
          {{ reportButtons.find(btn => btn.type === activeReport)?.title }}
        </h3>
        <div v-if="loading" class="flex items-center gap-2 text-blue-400">
          <Loader2 class="w-5 h-5 animate-spin" />
          <span>AI 生成中...</span>
        </div>
      </div>
      
      <div class="prose prose-invert prose-slate max-w-none">
        <div v-if="loading && !reportContent" class="flex flex-col items-center justify-center py-20 gap-4">
          <div class="relative">
            <Loader2 class="w-10 h-10 text-blue-400 animate-spin" />
            <div class="absolute inset-0 blur-lg bg-blue-400/20 animate-pulse"></div>
          </div>
          <span class="text-blue-400 font-medium tracking-widest animate-pulse">DeepSeek 深度分析中...</span>
        </div>
        <div v-if="reportContent" class="text-slate-300 whitespace-pre-wrap leading-relaxed">
          <template v-for="(line, index) in parsedContent" :key="index">
            <!-- 标题渲染 -->
            <h1 v-if="line.type === 'h1'" class="text-2xl font-bold text-white mt-6 mb-4" v-html="line.content"></h1>
            <h2 v-else-if="line.type === 'h2'" class="text-xl font-bold text-white mt-5 mb-3" v-html="line.content"></h2>
            <h3 v-else-if="line.type === 'h3'" class="text-lg font-semibold text-white mt-4 mb-2" v-html="line.content"></h3>
            
            <!-- 列表渲染 -->
            <li v-else-if="line.type === 'li'" class="ml-4 mb-1" v-html="line.content"></li>
            
            <!-- 分割线渲染 -->
            <hr v-else-if="line.type === 'hr'" class="my-6 border-slate-600" />
            
            <!-- 表格渲染 -->
            <div v-else-if="line.type === 'table'" class="my-6 overflow-x-auto rounded-lg border border-slate-700 bg-slate-900/50 shadow-inner">
              <table class="w-full text-sm text-left border-collapse">
                <thead>
                  <tr class="bg-slate-800/80">
                    <th v-for="(header, i) in line.headers" :key="i" class="px-4 py-3 font-bold text-slate-200 border-b border-slate-700" v-html="header"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, ri) in line.rows" :key="ri" class="border-b border-slate-800 hover:bg-slate-800/40 transition-colors">
                    <td v-for="(cell, ci) in row" :key="ci" class="px-4 py-3 text-slate-300" v-html="cell"></td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- 普通段落渲染 -->
            <p v-else-if="line.type === 'p'" class="mb-3" v-html="line.content"></p>
            
            <!-- 换行渲染 -->
            <br v-else-if="line.type === 'br'" />
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Sparkles, FileText, User, Lightbulb, Loader2, Clock, RotateCw } from 'lucide-vue-next';
import { callDeepSeekAPI } from '../utils/api';
import { fetchAllStats } from '../data/mockData';

type ReportType = 'analysis' | 'behavior' | 'recommendation';

const activeReport = ref<ReportType | null>(null);
const loading = ref(false);
const reportContent = ref('');
const reportTime = ref('');

onMounted(() => {
  fetchAllStats();
});

const generateReport = async (type: ReportType, force: boolean = false) => {
  // 如果点击的是新模块，或者强制更新，则清空旧内容显示加载状态
  if (activeReport.value !== type || force) {
    reportContent.value = '';
    reportTime.value = '';
  }
  
  activeReport.value = type;
  loading.value = true;
  
  try {
    // 逻辑已迁移至后端，直接传入类型即可获取专业报告和生成时间
    const result = await callDeepSeekAPI(type, force);
    reportContent.value = result.report;
    reportTime.value = result.updated_at || '';
  } catch (error) {
    console.error('AI Report Generation Error:', error);
    reportContent.value = '生成报告失败，请检查 API 配置或网络连接。';
  } finally {
    loading.value = false;
  }
};

const parsedContent = computed(() => {
  if (!reportContent.value) return [];

  const parseInline = (text: string) => {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-bold">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-slate-700 px-1 rounded text-blue-300">$1</code>');
  };

  const lines = reportContent.value.split('\n');
  const result: any[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    // 表格识别逻辑
    if (trimmed.startsWith('|')) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        tableLines.push(lines[i].trim());
        i++;
      }
      
      if (tableLines.length >= 2) {
        // 解析表头
        const headers = tableLines[0]
          .split('|')
          .filter((_, idx, arr) => idx > 0 && idx < arr.length - 1)
          .map(c => parseInline(c.trim()));
        
        // 解析数据行（跳过表头和分割线）
        const rows = tableLines.slice(2)
          .map(rowLine => 
            rowLine.split('|')
            .filter((_, idx, arr) => idx > 0 && idx < arr.length - 1)
            .map(c => parseInline(c.trim()))
          );
        
        result.push({ type: 'table', headers, rows });
      }
      continue;
    }

    // 标题
    if (trimmed.startsWith('# ')) {
      result.push({ type: 'h1', content: parseInline(trimmed.slice(2)) });
    } else if (trimmed.startsWith('## ')) {
      result.push({ type: 'h2', content: parseInline(trimmed.slice(3)) });
    } else if (trimmed.startsWith('### ')) {
      result.push({ type: 'h3', content: parseInline(trimmed.slice(4)) });
    } 
    // 列表
    else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      result.push({ type: 'li', content: parseInline(trimmed.slice(2)) });
    } 
    // 有序列表
    else if (/^\d+\.\s/.test(trimmed)) {
      result.push({ type: 'li', content: parseInline(trimmed.replace(/^\d+\.\s/, '')) });
    }
    // 分割线
    else if (trimmed.startsWith('---')) {
      result.push({ type: 'hr' });
    } 
    // 段落
    else if (trimmed) {
      result.push({ type: 'p', content: parseInline(trimmed) });
    } 
    // 换行
    else {
      result.push({ type: 'br' });
    }
    i++;
  }
  
  return result;
});

const reportButtons = [
  { 
    type: 'analysis', 
    icon: FileText, 
    title: '数据分析报告', 
    description: '自动生成全站核心销售指标及趋势洞察',
    theme: 'blue',
    activeGradient: 'from-blue-600/60 to-blue-400/30',
    activeBorder: 'border-blue-300/50',
    iconColor: 'text-blue-400',
    glowShadow: 'shadow-[0_0_20px_rgba(59,130,246,0.3)]'
  },
  { 
    type: 'behavior', 
    icon: User, 
    title: '用户行为分析', 
    description: '深度挖掘用户画像偏好及消费行为心理',
    theme: 'purple',
    activeGradient: 'from-purple-600/60 to-purple-400/30',
    activeBorder: 'border-purple-300/50',
    iconColor: 'text-purple-400',
    glowShadow: 'shadow-[0_0_20px_rgba(168,85,247,0.3)]'
  },
  { 
    type: 'recommendation', 
    icon: Lightbulb, 
    title: '推荐优化建议', 
    description: '基于算法架构演进及转化的技术方案建议',
    theme: 'emerald',
    activeGradient: 'from-emerald-600/60 to-emerald-400/30',
    activeBorder: 'border-emerald-300/50',
    iconColor: 'text-emerald-400',
    glowShadow: 'shadow-[0_0_20px_rgba(16,185,129,0.3)]'
  },
];
</script>

<style scoped>
:deep(strong) {
  color: white;
  font-weight: 700;
}
:deep(code) {
  font-family: monospace;
}
</style>
