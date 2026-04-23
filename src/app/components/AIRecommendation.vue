<template>
  <div class="space-y-6">
    <!-- 标题 -->
    <div class="bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg p-6 border border-blue-500/20">
      <div class="flex items-center gap-3 mb-2">
        <Sparkles class="w-6 h-6 text-blue-400" />
        <h2 class="text-2xl font-bold text-white">AI 智能分析</h2>
      </div>
      <p class="text-slate-300">基于 DeepSeek 大模型的智能数据分析和推荐优化</p>
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

    <!-- 用户行为分析用户选择 -->
    <div v-if="activeReport === 'behavior'" class="bg-slate-800 rounded-lg p-6 border border-slate-700 animate-in fade-in slide-in-from-top-4 duration-300">
      <div class="flex flex-col lg:flex-row gap-6 items-end">
        <!-- 搜索部分 -->
        <div class="flex-1 w-full lg:max-w-xl">
          <label class="block text-slate-400 text-xs font-medium mb-1.5 px-1">精准搜索分析对象</label>
          <div class="flex items-center bg-slate-700 rounded-lg border border-slate-600 focus-within:border-purple-500 transition-all overflow-hidden">
            <select v-model="searchType" class="bg-slate-800 text-slate-300 text-sm px-3 py-2 border-r border-slate-600 outline-none cursor-pointer">
              <option value="id">用户ID</option>
              <option value="name">用户姓名</option>
            </select>
            <div class="relative flex-1">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input 
                v-model="searchKeyword" 
                type="text" 
                :placeholder="searchType === 'id' ? '输入完整ID...' : '输入姓名关键词...'" 
                class="w-full bg-transparent text-white text-sm pl-10 pr-4 py-2 outline-none"
                @keyup.enter="handleManualSearch"
              />
            </div>
            <button @click="handleManualSearch" class="px-6 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-bold transition-colors">
              查找
            </button>
          </div>
        </div>

        <div class="hidden lg:flex items-center justify-center py-2 h-10">
          <div class="w-px h-8 bg-slate-700"></div>
          <span class="px-3 text-slate-500 text-xs font-bold italic">OR</span>
          <div class="w-px h-8 bg-slate-700"></div>
        </div>

        <!-- 下拉列表 -->
        <div class="flex-1 w-full lg:max-w-xs">
          <label class="block text-slate-400 text-xs font-medium mb-1.5 px-1">从活跃用户列表挑选</label>
          <select
            v-model="selectedUserId"
            @change="onUserSelectChange"
            class="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2 text-sm focus:border-purple-500 outline-none transition-all cursor-pointer"
          >
            <option value="">-- 请选择用户 --</option>
            <option v-for="user in uniqueUsers" :key="user.id" :value="user.id">
              {{ user.id }} - {{ user.name }}
            </option>
          </select>
        </div>
      </div>

      <div class="mt-6 grid grid-cols-1 md:grid-cols-3 items-center gap-4">
        <div class="flex justify-start">
          <p v-if="searchStatus" :class="searchStatus.type === 'success' ? 'text-emerald-400' : 'text-rose-400'" class="text-xs px-1 font-medium animate-in fade-in duration-300">
            {{ searchStatus.msg }}
          </p>
        </div>
        <div class="flex justify-center">
          <button
            v-if="selectedUserId"
            @click="generateReport('behavior')"
            :disabled="loading"
            class="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white px-10 py-2.5 rounded-lg transition-all disabled:opacity-50 font-bold shadow-lg shadow-purple-900/20 active:scale-95 whitespace-nowrap"
          >
            {{ loading ? '报告生成中...' : '开始 AI 深度分析' }}
          </button>
        </div>
        <div class="hidden md:block"></div>
      </div>
    </div>

    <!-- 报告内容 -->
    <div v-if="activeReport" class="bg-slate-800 rounded-lg p-6 border border-slate-700">
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
            <h1 v-if="line.type === 'h1'" class="text-2xl font-bold text-white mt-6 mb-4">{{ line.content }}</h1>
            <h2 v-else-if="line.type === 'h2'" class="text-xl font-bold text-white mt-5 mb-3">{{ line.content }}</h2>
            <h3 v-else-if="line.type === 'h3'" class="text-lg font-semibold text-white mt-4 mb-2">{{ line.content }}</h3>
            <li v-else-if="line.type === 'li'" class="ml-4 mb-1">{{ line.content }}</li>
            <hr v-else-if="line.type === 'hr'" class="my-6 border-slate-600" />
            <p v-else-if="line.type === 'p'" class="mb-3">{{ line.content }}</p>
            <br v-else-if="line.type === 'br'" />
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Sparkles, FileText, User, Lightbulb, Loader2, Search } from 'lucide-vue-next';
import { callDeepSeekAPI } from '../utils/api';
import { 
  dashboardStats, productAnalysis, userList, fetchAllStats, isLoading as isStatsLoading 
} from '../data/mockData';

type ReportType = 'analysis' | 'behavior' | 'recommendation';

const activeReport = ref<ReportType | null>(null);
const loading = ref(false);
const reportContent = ref('');
const selectedUserId = ref('');
const searchType = ref<'id' | 'name'>('name');
const searchKeyword = ref('');
const searchStatus = ref<{ type: 'success' | 'error', msg: string } | null>(null);

onMounted(() => {
  fetchAllStats();
});

const uniqueUsers = computed(() => (userList || []).slice(0, 100));

const onUserSelectChange = () => {
  if (selectedUserId.value) {
    searchKeyword.value = '';
    searchStatus.value = null;
  }
};

const handleManualSearch = async () => {
  const kw = searchKeyword.value.trim();
  if (!kw) return;
  searchStatus.value = { type: 'success', msg: '正在检索数据库...' };
  try {
    const res = await fetch(`http://localhost:5000/api/users/search?keyword=${encodeURIComponent(kw)}&type=${searchType.value}`);
    const found = await res.json();
    if (found) {
      selectedUserId.value = found.id;
      searchStatus.value = { type: 'success', msg: `已选中: ${found.name}` };
    } else {
      searchStatus.value = { type: 'error', msg: '未找到匹配用户' };
    }
  } catch (err) {
    searchStatus.value = { type: 'error', msg: '搜索失败' };
  }
};

const generateReport = async (type: ReportType) => {
  activeReport.value = type;
  loading.value = true;
  reportContent.value = '';

  try {
    let prompt = '';

    if (type === 'analysis') {
      const { totalSales, totalOrders, avgPrice } = dashboardStats.kpi;
      const topCategories = productAnalysis.categoryData
        .slice(0, 3)
        .map(cat => `${cat.name} (¥${cat.value.toLocaleString()})`)
        .join(', ');

      prompt = `作为电商数据分析师，请基于以下真实数据生成一份详细的数据分析报告：

数据概况：
- 总交易额: ¥${totalSales?.toLocaleString()}
- 订单总量: ${totalOrders}笔
- 平均客单价: ¥${avgPrice?.toLocaleString()}
- 热销品类: ${topCategories}

请从总体概况、用户画像、商品销售分析和优化建议四个维度进行深度分析。用markdown格式输出。`;

    } else if (type === 'behavior') {
      if (!selectedUserId.value) return;
      // Behavior analysis still benefits from a dedicated endpoint or filtered data
      prompt = `作为电商数据分析师，请分析用户 ${selectedUserId.value} 的消费行为。请从消费特征、价格敏感度、用户价值进行分析。`;

    } else {
      prompt = `作为电商推荐系统专家，提供智能推荐系统的优化建议（包含协同过滤、内容推荐等策略）。用markdown格式输出。`;
    }

    const result = await callDeepSeekAPI(prompt);
    reportContent.value = result;
  } catch (error) {
    console.error('AI Report Generation Error:', error);
    reportContent.value = '生成报告失败，请检查 API 配置或网络连接。';
  } finally {
    loading.value = false;
  }
};

const parsedContent = computed(() => {
  return reportContent.value.split('\n').map(line => {
    if (line.startsWith('# ')) return { type: 'h1', content: line.slice(2) };
    if (line.startsWith('## ')) return { type: 'h2', content: line.slice(3) };
    if (line.startsWith('### ')) return { type: 'h3', content: line.slice(4) };
    if (line.startsWith('- ')) return { type: 'li', content: line.slice(2) };
    if (line.startsWith('---')) return { type: 'hr' };
    if (line.trim()) return { type: 'p', content: line };
    return { type: 'br' };
  });
});

const reportButtons = [
  { type: 'analysis', icon: FileText, title: '数据分析报告', description: '自动生成全面的数据分析报告', color: 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30' },
  { type: 'behavior', icon: User, title: '用户行为分析', description: '深度分析用户消费行为特征', color: 'bg-purple-500/20 text-purple-400 hover:bg-purple-500/30' },
  { type: 'recommendation', icon: Lightbulb, title: '推荐优化建议', description: '智能推荐系统优化方案', color: 'bg-green-500/20 text-green-400 hover:bg-green-500/30' },
];
</script>
