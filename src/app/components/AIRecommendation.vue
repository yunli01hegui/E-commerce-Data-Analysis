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
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <button
        v-for="btn in reportButtons"
        :key="btn.type"
        @click="generateReport(btn.type as ReportType)"
        :disabled="loading"
        :class="[btn.color, 'p-6 rounded-lg border border-slate-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-left']"
      >
        <component :is="btn.icon" class="w-8 h-8 mb-3" />
        <h3 class="text-lg font-semibold mb-2">{{ btn.title }}</h3>
        <p class="text-sm text-slate-400">{{ btn.description }}</p>
      </button>
    </div>

    <!-- 报告内容 -->
    <div v-if="activeReport" class="bg-slate-800 rounded-lg p-6 border border-slate-700 relative">
      <!-- 报告生成时间展示 -->
      <div v-if="reportTime && !loading" class="absolute top-4 right-6 flex items-center gap-1.5 text-slate-500 text-xs font-mono bg-slate-900/50 px-3 py-1 rounded-full border border-slate-700/50">
        <Clock class="w-3.5 h-3.5" />
        报告生成于: {{ reportTime }}
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
        <div v-if="loading && !reportContent" class="flex items-center justify-center py-12">
          <Loader2 class="w-8 h-8 text-blue-400 animate-spin" />
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
import { Sparkles, FileText, User, Lightbulb, Loader2, Clock } from 'lucide-vue-next';
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

const generateReport = async (type: ReportType) => {
  activeReport.value = type;
  loading.value = true;
  reportContent.value = '';
  reportTime.value = '';

  try {
    // 逻辑已迁移至后端，直接传入类型即可获取专业报告和生成时间
    const result = await callDeepSeekAPI(type);
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
  { type: 'analysis', icon: FileText, title: '数据分析报告', description: '自动生成全面的数据分析报告', color: 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30' },
  { type: 'behavior', icon: User, title: '用户行为分析', description: '深度分析用户消费行为特征', color: 'bg-purple-500/20 text-purple-400 hover:bg-purple-500/30' },
  { type: 'recommendation', icon: Lightbulb, title: '推荐优化建议', description: '智能推荐系统优化方案', color: 'bg-green-500/20 text-green-400 hover:bg-green-500/30' },
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
