<template>
  <div class="space-y-6">
    <!-- 城市分级概览 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div v-for="stat in tierStats" :key="stat.tier" class="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <div class="flex items-center justify-between mb-4">
          <h4 class="text-white font-semibold text-lg">{{ stat.tier }}</h4>
          <div class="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm">
            {{ stat.cityCount }} 城市
          </div>
        </div>
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-slate-400 text-sm">总消费额</span>
            <span class="text-green-400 font-semibold">
              ¥{{ stat.totalAmount.toLocaleString() }}
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-slate-400 text-sm">订单数</span>
            <span class="text-white font-semibold">{{ stat.orderCount }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-slate-400 text-sm">平均客单价</span>
            <span class="text-blue-400 font-semibold">
              ¥{{ stat.avgAmount.toLocaleString(undefined, { maximumFractionDigits: 0 }) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 城市消费排行 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div class="flex items-center gap-2">
          <MapPin class="w-5 h-5 text-blue-400" />
          <h3 class="text-xl font-semibold text-white">城市消费排行</h3>
        </div>
        <div class="flex items-center bg-slate-700/50 p-1 rounded-lg border border-slate-700">
          <button 
            @click="rankingView = 'top10'"
            :class="[
              'px-4 py-1.5 rounded-md text-xs font-medium transition-all',
              rankingView === 'top10' ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20' : 'text-slate-400 hover:text-white'
            ]"
          >
            前10城市
          </button>
          <button 
            @click="rankingView = 'all'"
            :class="[
              'px-4 py-1.5 rounded-md text-xs font-medium transition-all',
              rankingView === 'all' ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20' : 'text-slate-400 hover:text-white'
            ]"
          >
            全部城市
          </button>
        </div>
      </div>
      <div :style="{ height: dynamicChartHeight }">
        <v-chart :key="rankingView" class="h-full w-full" :option="cityRankingOption" autoresize />
      </div>
    </div>

    <!-- 城市消费力矩阵 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 class="text-xl font-semibold text-white mb-6">城市消费力矩阵</h3>
      <p class="text-slate-400 text-sm mb-4">气泡大小代表总消费额，横轴为订单数，纵轴为平均客单价</p>
      <div class="h-[400px]">
        <v-chart class="h-full w-full" :option="cityMatrixOption" autoresize />
      </div>
    </div>

    <!-- 城市详细列表 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 class="text-xl font-semibold text-white mb-6">城市消费详情</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        <div v-for="(city, index) in visibleCityData" :key="city.city" class="bg-slate-700/50 rounded-lg p-4 hover:bg-slate-700 transition-all duration-300">
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center gap-2">
              <div :class="[
                'w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm',
                index === 0 ? 'bg-yellow-500 text-slate-900' :
                index === 1 ? 'bg-slate-400 text-slate-900' :
                index === 2 ? 'bg-orange-600 text-white' :
                'bg-slate-600 text-slate-300'
              ]">
                {{ index + 1 }}
              </div>
              <h4 class="text-white font-semibold text-lg">{{ city.city }}</h4>
            </div>
            <span class="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded">
              {{ city.topCategory }}
            </span>
          </div>
          <div class="space-y-2">
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">总消费额</span>
              <span class="text-green-400 font-semibold">
                ¥{{ city.totalAmount.toLocaleString(undefined, { maximumFractionDigits: 0 }) }}
              </span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">订单数</span>
              <span class="text-white">{{ city.orderCount }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">用户数</span>
              <span class="text-white">{{ city.userCount }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">平均客单价</span>
              <span class="text-blue-400 font-semibold">
                ¥{{ city.avgAmount.toLocaleString(undefined, { maximumFractionDigits: 0 }) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div v-if="visibleCount < cityData.length" class="flex items-center justify-center gap-4">
        <button 
          @click="showMore"
          class="flex items-center gap-2 px-8 py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-all text-sm font-medium border border-slate-600 active:scale-95"
        >
          查看更多 (剩 {{ cityData.length - visibleCount }})
        </button>
        <button 
          @click="showAll"
          class="flex items-center gap-2 px-8 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-all text-sm font-medium shadow-lg shadow-blue-900/20 active:scale-95"
        >
          显示全部城市
        </button>
      </div>
      <div v-else-if="cityData.length > 9" class="flex items-center justify-center">
        <button 
          @click="visibleCount = 9"
          class="px-8 py-2 text-slate-500 hover:text-slate-300 text-sm transition-colors border border-transparent hover:border-slate-700 rounded-lg"
        >
          收起列表
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, ScatterChart } from 'echarts/charts';
import {
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';
import { MapPin } from 'lucide-vue-next';
import { cityConsumption } from '../data/mockData';

use([
  CanvasRenderer,
  BarChart,
  ScatterChart,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

// 使用从后端预计算的响应式数据
const cityData = computed(() => cityConsumption.cityData);
const tierStats = computed(() => cityConsumption.tierStats);

// 城市列表分页控制
const visibleCount = ref(9);
const visibleCityData = computed(() => cityData.value.slice(0, visibleCount.value));

// 城市排行视图控制
const rankingView = ref<'top10' | 'all'>('top10');

const showMore = () => {
  visibleCount.value += 9;
};

const showAll = () => {
  visibleCount.value = cityData.value.length;
};

// 动态图表高度 (根据城市数量调整)
const dynamicChartHeight = computed(() => {
  const count = rankingView.value === 'top10' ? 10 : cityData.value.length;
  const height = Math.max(400, count * 40 + 50);
  return `${height}px`;
});

const cityRankingOption = computed(() => {
  const displayData = rankingView.value === 'top10' 
    ? cityData.value.slice(0, 10) 
    : cityData.value;
    
  // 反转是为了在 y 轴从上到下显示
  const sortedData = [...displayData].reverse();
  
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1e293b',
      borderColor: '#334155',
      textStyle: { color: '#fff' },
      formatter: (params: any) => {
        const item = sortedData[params[0].dataIndex];
        return `${item.city}<br/>总消费额: ¥${item.totalAmount.toLocaleString()}<br/>平均客单价: ¥${item.avgAmount.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
      }
    },
    grid: { left: '3%', right: '8%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'value',
      name: '总消费额',
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#334155' } },
    },
    yAxis: {
      type: 'category',
      name: '城市',
      data: sortedData.map(d => d.city),
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
    },
    series: [
      {
        name: '消费总额',
        type: 'bar',
        data: sortedData.map(d => d.totalAmount),
        itemStyle: { color: '#3b82f6', borderRadius: [0, 4, 4, 0] },
      },
    ],
  };
});

const cityMatrixOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    backgroundColor: '#1e293b',
    borderColor: '#334155',
    textStyle: { color: '#fff' },
    formatter: (params: any) => {
      return `${params.data[3]}<br/>订单数: ${params.data[0]}<br/>平均客单价: ¥${params.data[1].toLocaleString(undefined, { maximumFractionDigits: 0 })}<br/>总消费额: ¥${params.data[2].toLocaleString()}`;
    }
  },
  grid: { left: '3%', right: '8%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'value',
    name: '订单数',
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#94a3b8' },
    splitLine: { lineStyle: { color: '#334155' } },
  },
  yAxis: {
    type: 'value',
    name: '平均客单价',
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#94a3b8' },
    splitLine: { lineStyle: { color: '#334155' } },
  },
  series: [
    {
      name: '城市消费力',
      type: 'scatter',
      data: cityData.value.map(d => [d.orderCount, d.avgAmount, d.totalAmount, d.city]),
      symbolSize: (data: any) => Math.sqrt(data[2]) / 20,
      itemStyle: { color: '#8b5cf6', opacity: 0.6 },
    },
  ],
}));
</script>
