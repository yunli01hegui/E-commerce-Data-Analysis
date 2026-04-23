<template>
  <div class="space-y-6">
    <!-- RFM指标说明 -->
    <div class="bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg p-6 border border-blue-500/20">
      <h3 class="text-xl font-semibold text-white mb-4">RFM 模型分析</h3>
      <p class="text-slate-300 mb-4">
        RFM模型是衡量客户价值和创造利润能力的重要工具，通过三个维度评估客户：
      </p>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-for="desc in rfmDescriptions" :key="desc.title" class="bg-slate-800/50 rounded-lg p-4">
          <div class="flex items-center gap-2 mb-2">
            <component :is="desc.icon" :class="['w-5 h-5', desc.iconClass]" />
            <span class="text-white font-semibold">{{ desc.title }}</span>
          </div>
          <p class="text-slate-400 text-sm">{{ desc.content }}</p>
        </div>
      </div>
    </div>

    <!-- 客户分群概览 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div class="flex items-center gap-2 mb-6">
        <Users class="w-5 h-5 text-blue-400" />
        <h3 class="text-xl font-semibold text-white">客户分群概览</h3>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="seg in segmentArray" :key="seg.segment" class="bg-slate-700/50 rounded-lg p-4 border-l-4" :style="{ borderLeftColor: seg.color }">
          <div class="flex items-center justify-between mb-2">
            <h4 class="text-white font-semibold">{{ seg.segment }}</h4>
            <div 
              class="w-3 h-3 rounded-full"
              :style="{ backgroundColor: seg.color }"
            ></div>
          </div>
          <p class="text-slate-400 text-xs mb-3">{{ seg.desc }}</p>
          <div class="space-y-2">
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">RFM得分</span>
              <span class="text-white font-bold">{{ seg.avgRFM || '0.0' }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">客户数</span>
              <span class="text-white font-semibold">{{ seg.count }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">总消费</span>
              <span class="text-green-400 font-semibold">
                ¥{{ seg.totalAmount.toLocaleString(undefined, { maximumFractionDigits: 0 }) }}
              </span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">人均消费</span>
              <span class="text-blue-400 font-semibold">
                ¥{{ (seg.totalAmount / seg.count).toLocaleString(undefined, { maximumFractionDigits: 0 }) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- RFM二维矩阵：频率 vs 消费金额 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 class="text-xl font-semibold text-white mb-6">客户价值分布矩阵</h3>
      <p class="text-slate-400 text-sm mb-4">横轴：购买频率 | 纵轴：消费金额 | 颜色：客户分群</p>
      <div class="h-[450px]">
        <v-chart class="h-full w-full" :option="rfmMatrixOption" autoresize />
      </div>
    </div>

    <!-- RFM 客户价值看板 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700 shadow-xl">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div class="flex items-center gap-2">
          <Award class="w-5 h-5 text-yellow-400" />
          <h3 class="text-xl font-semibold text-white">RFM 客户价值看板</h3>
        </div>
        
        <!-- 搜索控制 -->
        <div class="flex items-center bg-slate-700 rounded-lg overflow-hidden border border-slate-600 focus-within:border-blue-500 transition-all">
          <div class="px-3 py-2 text-slate-400 border-r border-slate-600">
            <Search class="w-4 h-4" />
          </div>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索用户名或ID..." 
            class="bg-transparent text-white text-sm px-4 py-2 outline-none w-48 md:w-64"
          />
          <button v-if="searchQuery" @click="searchQuery = ''" class="px-3 py-2 text-slate-400 hover:text-white transition-colors">
            <X class="w-4 h-4" />
          </button>
        </div>
      </div>

      <div class="overflow-x-auto rounded-lg border border-slate-700/50">
        <table class="w-full">
          <thead>
            <tr class="bg-slate-700/30 text-slate-300 text-xs font-semibold uppercase tracking-wider">
              <th class="text-left py-4 px-4">排名</th>
              <th class="text-left py-4 px-4">客户ID</th>
              <th class="text-left py-4 px-4">客户名称</th>
              <th class="text-left py-4 px-4">客户分群</th>
              <th class="text-center py-4 px-4">R评分</th>
              <th class="text-center py-4 px-4">F评分</th>
              <th class="text-center py-4 px-4">M评分</th>
              <th class="text-right py-4 px-4">消费总额</th>
              <th class="text-right py-4 px-4">购买次数</th>
              <th class="text-right py-4 px-4">距今天数</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-700/50">
            <tr v-if="paginatedRFM.length === 0" class="hover:bg-slate-700/20 transition-colors">
              <td colspan="10" class="py-12 text-center text-slate-500">未找到匹配的客户数据</td>
            </tr>
            <tr v-for="(user, idx) in paginatedRFM" :key="user.userId" class="hover:bg-slate-700/40 transition-all duration-200 group">
              <td class="py-4 px-4">
                <div :class="[
                  'w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-transform group-hover:scale-110',
                  (startIndex + idx) === 0 ? 'bg-yellow-500 text-slate-900 shadow-lg shadow-yellow-900/20' :
                  (startIndex + idx) === 1 ? 'bg-slate-300 text-slate-900' :
                  (startIndex + idx) === 2 ? 'bg-orange-600 text-white' :
                  'bg-slate-700 text-slate-400 border border-slate-600'
                ]">
                  {{ startIndex + idx + 1 }}
                </div>
              </td>
              <td class="py-4 px-4 text-slate-300 font-mono text-sm">{{ user.userId }}</td>
              <td class="py-4 px-4 text-white font-medium">{{ user.userName }}</td>
              <td class="py-4 px-4">
                <span 
                  class="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider"
                  :style="{ backgroundColor: `${user.segmentColor}20`, color: user.segmentColor, border: `1px solid ${user.segmentColor}40` }"
                >
                  {{ user.segment }}
                </span>
              </td>
              <td class="py-4 px-4 text-center">
                <div class="text-blue-400 font-bold bg-blue-400/10 rounded py-1">{{ user.R }}</div>
              </td>
              <td class="py-4 px-4 text-center">
                <div class="text-purple-400 font-bold bg-purple-400/10 rounded py-1">{{ user.F }}</div>
              </td>
              <td class="py-4 px-4 text-center">
                <div class="text-green-400 font-bold bg-green-400/10 rounded py-1">{{ user.M }}</div>
              </td>
              <td class="py-4 px-4 text-right text-green-400 font-bold">
                ¥{{ user.monetary.toLocaleString() }}
              </td>
              <td class="py-4 px-4 text-right text-white font-semibold">{{ user.frequency }}</td>
              <td class="py-4 px-4 text-right text-slate-400">{{ user.recency }}天</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页控制栏 (复刻数据中心风格) -->
      <div class="mt-6 pt-6 border-t border-slate-700 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div class="text-sm text-slate-400">
          显示 <span class="text-white font-medium">{{ filteredRFM.length > 0 ? startIndex + 1 : 0 }}</span> 到 <span class="text-white font-medium">{{ endIndex }}</span> 条，共 <span class="text-white font-medium">{{ filteredRFM.length }}</span> 条记录
        </div>
        
        <div class="flex items-center gap-2">
          <button 
            @click="prevPage" 
            :disabled="currentPage === 1"
            class="p-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg disabled:opacity-30 disabled:cursor-not-allowed transition-all border border-slate-600"
          >
            <ChevronLeft class="w-5 h-5" />
          </button>
          
          <div class="hidden sm:flex items-center gap-1">
            <button 
              v-for="p in visiblePages" 
              :key="p" 
              @click="goToPage(p)"
              class="w-10 h-10 rounded-lg text-sm font-bold transition-all"
              :class="currentPage === p ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20' : 'text-slate-400 hover:bg-slate-700 hover:text-white border border-transparent hover:border-slate-600'"
            >
              {{ p }}
            </button>
          </div>

          <button 
            @click="nextPage" 
            :disabled="currentPage === totalPages"
            class="p-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg disabled:opacity-30 disabled:cursor-not-allowed transition-all border border-slate-600"
          >
            <ChevronRight class="w-5 h-5" />
          </button>
        </div>

        <!-- 跳转控制 -->
        <div class="flex items-center gap-2 border-l border-slate-700 pl-4">
          <span class="text-xs text-slate-500">跳转至</span>
          <div class="flex items-center bg-slate-700 rounded-lg overflow-hidden border border-slate-600 focus-within:border-blue-500 transition-all">
            <input 
              v-model="jumpPageNum" 
              type="number" 
              class="bg-transparent text-white text-xs px-2 py-1.5 outline-none w-12 text-center [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
              @keyup.enter="handleJumpPage"
            />
            <button @click="handleJumpPage" class="px-2 py-1.5 bg-blue-600 hover:bg-blue-500 text-white transition-colors">
              <ArrowRight class="w-3.5 h-3.5" />
            </button>
          </div>
          <span class="text-xs text-slate-500">页</span>
        </div>
      </div>
    </div>

    <!-- 客户策略 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div class="flex items-center gap-2 mb-6">
        <Sparkles class="w-5 h-5 text-purple-400" />
        <h3 class="text-xl font-semibold text-white">针对性客户策略</h3>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="strategy in activeStrategies" :key="strategy.segment" class="bg-slate-700/30 rounded-xl p-5 border border-slate-600 hover:border-blue-500/50 transition-all">
          <div class="flex items-center gap-3 mb-4">
            <div 
              class="w-4 h-4 rounded-full"
              :style="{ backgroundColor: strategy.color }"
            ></div>
            <h4 class="text-white font-bold text-lg">{{ strategy.segment }}策略</h4>
          </div>
          <div class="space-y-3">
            <div v-for="(item, idx) in strategy.items" :key="idx" class="flex gap-3">
              <span class="flex-shrink-0 w-5 h-5 rounded-full bg-slate-600 text-blue-400 text-xs flex items-center justify-center font-bold">
                {{ idx + 1 }}
              </span>
              <p class="text-slate-300 text-sm leading-relaxed">{{ item }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { ScatterChart } from 'echarts/charts';
import {
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';
import { 
  Users, Clock, ShoppingCart, DollarSign, Award, Sparkles, 
  Search, X, ChevronLeft, ChevronRight, ArrowRight 
} from 'lucide-vue-next';
import { rfmAnalysis } from '../data/mockData';

use([
  CanvasRenderer,
  ScatterChart,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

// 1. 状态管理
const searchQuery = ref('');
const currentPage = ref(1);
const pageSize = 10;
const jumpPageNum = ref<number | string>('');

// 2. 数据处理
const rfmSegmented = computed(() => rfmAnalysis.rfmSegmented);
const segmentStats = computed(() => rfmAnalysis.segmentStats);

// 过滤逻辑
const filteredRFM = computed(() => {
  const query = searchQuery.value.toLowerCase().trim();
  if (!query) return rfmSegmented.value;
  
  return rfmSegmented.value.filter((user: any) => 
    user.userName.toLowerCase().includes(query) || 
    String(user.userId).toLowerCase().includes(query)
  );
});

// 分页逻辑
const paginatedRFM = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return filteredRFM.value.slice(start, start + pageSize);
});

// 计算分页元数据
const totalPages = computed(() => Math.ceil(filteredRFM.value.length / pageSize));
const startIndex = computed(() => (currentPage.value - 1) * pageSize);
const endIndex = computed(() => Math.min(startIndex.value + pageSize, filteredRFM.value.length));

const visiblePages = computed(() => {
  const range = [];
  const start = Math.max(1, currentPage.value - 2);
  const end = Math.min(totalPages.value, start + 4);
  for (let i = start; i <= end; i++) range.push(i);
  return range;
});

// 3. 交互方法
const prevPage = () => { if (currentPage.value > 1) currentPage.value--; };
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++; };
const goToPage = (p: number) => { currentPage.value = p; };
const handleJumpPage = () => {
  const p = Number(jumpPageNum.value);
  if (p >= 1 && p <= totalPages.value) {
    currentPage.value = p;
  }
};

// 搜索时重置页码
watch(searchQuery, () => {
  currentPage.value = 1;
});

const segmentArray = computed(() => {
  return Object.values(segmentStats.value).sort((a: any, b: any) => (b.avgRFM || 0) - (a.avgRFM || 0));
});

const rfmDescriptions = [
  { title: 'Recency (最近一次购买)', content: '客户最近一次购买距今的时间，越近越好', icon: Clock, iconClass: 'text-blue-400' },
  { title: 'Frequency (购买频率)', content: '客户在一定时期内的购买次数，越多越好', icon: ShoppingCart, iconClass: 'text-purple-400' },
  { title: 'Monetary (消费金额)', content: '客户在一定时期内的消费总额，越高越好', icon: DollarSign, iconClass: 'text-green-400' },
];

const strategyMap: Record<string, string[]> = {
  '重要价值客户': [
    '维持其高频消费，推送高客单价新品',
    '邀请加入 VIP 社群，提供专属管家服务',
    '定期进行专属回访，确保其对品牌的极高忠诚度'
  ],
  '重要发展客户': [
    '分析其近期购买品类，精准推送关联商品组合',
    '提供大额优惠券激励复购，提升购买频次',
    '将其纳入会员培养体系，关注其成长轨迹'
  ],
  '重要保持客户': [
    '提供重聚礼包，通过老客召回活动激活',
    '分析流失前购买习惯，推送其最感兴趣的内容',
    '加强品牌情感连接，提醒其积分即将过期'
  ],
  '重要挽留客户': [
    '重点回访，通过电话或短信进行深度关怀',
    '赠送高面额礼券，通过大力度促销吸引回归',
    '深入调研流失原因，改善服务细节'
  ],
  '一般价值客户': [
    '重点进行交叉销售，通过组合购买提升消费额',
    '引导其关注官方社交账号，增强品牌心智',
    '定期推送新品资讯和大众化活动'
  ],
  '一般发展客户': [
    '推荐平台热门爆款，降低其试错成本',
    '引导参与签到、抽奖等互动，提高访问频率',
    '推送其曾经浏览但未下单的商品折扣'
  ],
  '一般保持客户': [
    '推送低门槛激活券，测试其回归意愿',
    '保持周期性的品牌曝光，不进行强力打扰',
    '推荐相似品类的替代款，挖掘潜在需求'
  ],
  '一般挽留客户': [
    '进行低成本唤醒，如节假日祝福和限时活动',
    '利用极低价格的清仓活动吸引二次尝试',
    '保持基础曝光，等待需求自然恢复'
  ],
  '潜力客户': [
    '推荐热门新品，引导尝试更多品类',
    '设置会员升级阶梯奖励，激发成长动力',
    '加强互动沟通，建立初步品牌认知'
  ]
};

const activeStrategies = computed(() => {
  return segmentArray.value.map(seg => ({
    segment: seg.segment,
    color: seg.color,
    items: strategyMap[seg.segment] || ['持续关注客户需求，提供标准服务', '定期推送平台资讯', '保持基础沟通渠道']
  }));
});

const rfmMatrixOption = computed(() => {
  const maxFreq = rfmAnalysis.scatterData.length > 0 
    ? Math.max(...rfmAnalysis.scatterData.map((d: any) => d.x)) 
    : 10;

  return {
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: '#1e293b',
      borderColor: '#334155',
      textStyle: { color: '#fff' },
      formatter: (params: any) => {
        return `${params.data[3]} (${params.data[4]})<br/>频次: ${params.data[0]}<br/>金额: ¥${params.data[1].toLocaleString()}`;
      }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'value',
      name: '购买频率',
      max: maxFreq + 1,
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#334155' } },
    },
    yAxis: {
      type: 'value',
      name: '消费金额',
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#334155' } },
    },
    series: [
      {
        name: '客户价值',
        type: 'scatter',
        data: rfmAnalysis.scatterData.map((d: any) => [d.x, d.y, d.z, d.name, d.segment, d.segmentColor]),
        symbolSize: (data: any) => Math.sqrt(data[1]) / 5,
        itemStyle: {
          color: (params: any) => params.data[5],
          opacity: 0.7
        },
      },
    ],
  };
});
</script>
