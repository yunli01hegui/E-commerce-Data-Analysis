<template>
  <div class="space-y-6">
    <!-- 品类销售占比 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 class="text-xl font-semibold text-white mb-6">品类销售占比</h3>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="h-[300px]">
          <v-chart class="h-full w-full" :option="categoryOption" autoresize />
        </div>
        <div class="space-y-3">
          <div v-for="(item, index) in categoryData" :key="item.name" class="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
            <div class="flex items-center gap-3">
              <div
                class="w-4 h-4 rounded-full"
                :style="{ backgroundColor: colors[index % colors.length] }"
              ></div>
              <div>
                <div class="text-white font-medium">{{ item.name }}</div>
                <div class="text-slate-400 text-sm">{{ item.count }} 笔订单</div>
              </div>
            </div>
            <div class="text-white font-semibold">¥{{ item.value.toLocaleString() }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 热销商品排行 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div class="flex items-center gap-2 mb-6">
        <Package class="w-5 h-5 text-blue-400" />
        <h3 class="text-xl font-semibold text-white">热销商品 TOP 15</h3>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="(product, index) in productRanking"
          :key="product.key"
          class="p-4 bg-slate-700/50 rounded-lg hover:bg-slate-700 transition-colors"
        >
          <div class="flex items-start justify-between mb-3">
            <div :class="[
              'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm',
              index === 0 ? 'bg-yellow-500 text-slate-900' :
              index === 1 ? 'bg-slate-400 text-slate-900' :
              index === 2 ? 'bg-orange-600 text-white' :
              'bg-slate-600 text-slate-300'
            ]">
              {{ index + 1 }}
            </div>
            <span class="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded">
              {{ product.category }}
            </span>
          </div>
          <div class="mb-3">
            <h4 class="text-white font-medium mb-1 line-clamp-1">{{ product.name }}</h4>
            <div class="flex items-center gap-2 text-sm text-slate-400">
              <span>销量: {{ product.sales }}</span>
              <span>•</span>
              <span>{{ product.orders }} 订单</span>
            </div>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-green-400 font-semibold">¥{{ product.revenue.toLocaleString() }}</span>
            <TrendingUp class="w-4 h-4 text-green-400" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart } from 'echarts/charts';
import {
  TooltipComponent,
  LegendComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';
import { TrendingUp, Package } from 'lucide-vue-next';
import { productAnalysis } from '../data/mockData';

use([
  CanvasRenderer,
  PieChart,
  TooltipComponent,
  LegendComponent,
]);

const categoryData = computed(() => productAnalysis.categoryData);
const productRanking = computed(() => productAnalysis.productRanking);

const colors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899'];

const categoryOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    backgroundColor: '#1e293b',
    borderColor: '#334155',
    textStyle: { color: '#fff' },
    formatter: (params: any) => `${params.name}: ¥${params.value.toLocaleString()} (${params.percent}%)`
  },
  series: [
    {
      name: '品类占比',
      type: 'pie',
      radius: '70%',
      center: ['50%', '50%'],
      data: categoryData.value.map((d, i) => ({
        name: d.name,
        value: d.value,
        itemStyle: { color: colors[i % colors.length] }
      })),
      label: {
        show: true,
        formatter: '{b}: {d}%',
        color: '#94a3b8'
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
}));
</script>
