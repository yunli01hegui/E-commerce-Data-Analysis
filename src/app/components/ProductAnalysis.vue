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
        <h3 class="text-xl font-semibold text-white">热销商品</h3>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        <div
          v-for="(product, index) in visibleProductRanking"
          :key="product.key"
          class="p-4 bg-slate-700/50 rounded-lg hover:bg-slate-700 transition-all duration-300"
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

      <!-- 操作按钮 -->
      <div class="flex flex-col items-center gap-4">
        <div v-if="visibleCount < productRanking.length" class="flex items-center justify-center gap-4">
          <button 
            @click="showMore"
            class="flex items-center gap-2 px-8 py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-all text-sm font-medium border border-slate-600 active:scale-95"
          >
            查看更多 (剩 {{ productRanking.length - visibleCount }})
          </button>
          <button 
            @click="showAll"
            class="flex items-center gap-2 px-8 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-all text-sm font-medium shadow-lg shadow-blue-900/20 active:scale-95"
          >
            显示全部商品
          </button>
        </div>
        
        <button 
          v-if="visibleCount > 9"
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

// 商品列表分页控制
const visibleCount = ref(9);
const visibleProductRanking = computed(() => productRanking.value.slice(0, visibleCount.value));

const showMore = () => {
  visibleCount.value += 9;
};

const showAll = () => {
  visibleCount.value = productRanking.value.length;
};

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
