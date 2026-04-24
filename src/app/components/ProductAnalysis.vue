<template>
  <div class="space-y-6">
    <!-- 销售决策核心看板 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      <div v-for="stat in productStats" :key="stat.label" class="bg-slate-800/40 backdrop-blur-md p-5 rounded-2xl border border-slate-700/50 shadow-xl hover:border-blue-500/30 transition-all group relative min-h-[120px] flex flex-col justify-between overflow-hidden">
        <!-- 顶部行：左图标，右标题 -->
        <div class="flex justify-between items-start">
          <div class="p-2.5 rounded-xl bg-slate-900/50 group-hover:scale-110 transition-transform shrink-0">
            <component :is="stat.icon" class="w-5 h-5" :class="stat.color" />
          </div>
          <div class="text-right flex flex-col ml-2">
            <span class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">{{ stat.label }}</span>
            <span class="text-[10px] text-slate-500 font-medium truncate max-w-[120px]">{{ stat.subtitle }}</span>
          </div>
        </div>
        
        <!-- 底部行：核心数据（超长省略） -->
        <div class="text-right mt-4">
          <div 
            class="text-xl font-bold text-white tracking-tight leading-none truncate"
            :title="stat.value"
          >
            {{ stat.value }}
          </div>
        </div>

        <!-- 装饰背景效果 -->
        <div class="absolute -bottom-4 -right-4 w-12 h-12 rounded-full blur-2xl opacity-10 transition-opacity group-hover:opacity-30" :class="stat.color.replace('text', 'bg')"></div>
      </div>
    </div>

    <!-- 全品类深度数据透视 -->
    <div class="bg-slate-800 rounded-xl border border-slate-700 shadow-lg overflow-hidden">
      <div class="px-6 py-5 border-b border-slate-700 flex items-center justify-between bg-slate-800/50">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-blue-500/10 rounded-lg">
            <BarChartIcon class="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h3 class="text-lg font-bold text-white">全品类深度数据透视</h3>
            <p class="text-sm text-slate-400">实时追踪各业务类目的经营健康度与贡献占比</p>
          </div>
        </div>
        <div class="px-4 py-1.5 bg-slate-900 rounded-full border border-slate-700">
          <span class="text-xs text-slate-300 font-bold uppercase tracking-widest">共 {{ categoryEfficiency.length }} 个类目</span>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-900/50 text-white text-xs font-bold uppercase tracking-wider">
              <th class="px-6 py-5">品类名称</th>
              <th class="px-6 py-5">销售总额</th>
              <th class="px-6 py-5">销售件数</th>
              <th class="px-6 py-5">平均单价</th>
              <th class="px-6 py-5">平均件数/单</th>
              <th class="px-6 py-5 text-right">收入占比贡献</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-700/50">
            <tr v-for="item in categoryEfficiency" :key="item.category" class="hover:bg-slate-700/30 transition-colors group">
              <td class="px-6 py-5">
                <div class="flex items-center gap-3">
                  <div class="w-1.5 h-6 bg-blue-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <span class="text-white font-bold text-sm">{{ item.category }}</span>
                </div>
              </td>
              <td class="px-6 py-5">
                <div class="text-white font-mono font-medium text-sm">¥{{ item.revenue.toLocaleString() }}</div>
              </td>
              <td class="px-6 py-5">
                <div class="text-slate-300 text-sm">{{ item.volume.toLocaleString() }} <span class="text-xs text-slate-500">件</span></div>
              </td>
              <td class="px-6 py-5">
                <div class="text-emerald-400 font-mono text-sm">¥{{ item.avg_unit_price }}</div>
              </td>
              <td class="px-6 py-5">
                <div class="text-blue-400 text-sm">{{ item.upt }} <span class="text-xs text-slate-500">件</span></div>
              </td>
              <td class="px-6 py-5">
                <div class="flex flex-col items-end gap-2">
                  <span class="text-white font-bold text-sm">{{ item.rev_ratio }}%</span>
                  <div class="w-28 bg-slate-700 h-1.5 rounded-full overflow-hidden">
                    <div class="bg-gradient-to-r from-blue-600 to-blue-400 h-full rounded-full" :style="{ width: item.rev_ratio + '%' }"></div>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 品类销售占比 (左) -->
      <div class="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">
        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center gap-2">
            <PieChartIcon class="w-5 h-5 text-blue-400" />
            <h3 class="text-lg font-semibold text-white">品类结构分析</h3>
          </div>
          <span class="text-xs text-slate-400 uppercase tracking-widest">全维度数据洞察</span>
        </div>
        <div class="h-[350px]">
          <v-chart class="h-full w-full" :option="categoryOption" autoresize />
        </div>
      </div>

      <!-- 价格区间分布 (右) -->
      <div class="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">
        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center gap-2">
            <BarChart3 class="w-5 h-5 text-emerald-400" />
            <h3 class="text-lg font-semibold text-white">价格区间表现</h3>
          </div>
          <span class="text-sm text-slate-400">主销区间: <span class="text-emerald-400 font-bold ml-1">{{ (productAnalysis as any).stats?.main_price_range || '计算中...' }}</span></span>
        </div>
        <div class="h-[350px]">
          <v-chart class="h-full w-full" :option="priceRangeOption" autoresize />
        </div>
      </div>
    </div>

    <!-- 全量品类产出效能深度分析 -->
    <div class="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-purple-500/10 rounded-lg">
            <Target class="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h3 class="text-lg font-bold text-white">全品类经营效能矩阵</h3>
            <p class="text-sm text-purple-400 font-bold mb-1">
              效能指数 = 收入贡献率 / 销量占比。
            </p>
            <p class="text-xs text-slate-400 leading-relaxed max-w-2xl">
              指数 > 1 表示该类目以较少销量贡献了较高收入（高价值/高毛利）；
            </p>
            <p class="text-xs text-slate-400 leading-relaxed max-w-2xl">
              指数 < 1 表示该类目销量大但收入产出相对较低（引流/爆款/低单价）。
            </p>
          </div>
        </div>
        <div class="flex items-center gap-6 p-2 bg-slate-900/50 rounded-xl border border-slate-700/50">
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 bg-purple-500 rounded-full shadow-[0_0_8px_rgba(168,85,247,0.5)]"></div>
            <span class="text-xs font-bold text-slate-400 uppercase">收入贡献</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 bg-blue-500 rounded-full shadow-[0_0_8px_rgba(59,130,246,0.5)]"></div>
            <span class="text-xs font-bold text-slate-400 uppercase">销量占比</span>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        <div v-for="item in categoryEfficiency" :key="item.category" 
             class="group relative bg-slate-900/40 backdrop-blur-sm rounded-2xl p-6 border border-slate-800 hover:border-purple-500/40 hover:bg-slate-800/60 transition-all duration-300">
          
          <!-- 头部信息 -->
          <div class="flex justify-between items-start mb-6">
            <div>
              <div class="text-white font-black text-xl tracking-tight group-hover:text-purple-400 transition-colors">{{ item.category }}</div>
              <div class="flex items-center gap-2 mt-1">
                <span class="text-xs px-2 py-0.5 bg-slate-800 text-slate-400 rounded-full border border-slate-700">
                  {{ item.unique_buyers }} 位核心买家
                </span>
              </div>
            </div>
            <div :class="[
              'px-3 py-1 rounded-lg text-xs font-black shadow-lg',
              (item.rev_ratio / (item.vol_ratio || 1)) > 1.2 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
              (item.rev_ratio / (item.vol_ratio || 1)) > 0.8 ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
              'bg-rose-500/10 text-rose-400 border border-rose-500/20'
            ]">
              效能指数: {{ (item.rev_ratio / (item.vol_ratio || 1)).toFixed(2) }}
            </div>
          </div>

          <!-- 核心指标 Grid -->
          <div class="grid grid-cols-2 gap-4 mb-6">
            <div class="p-3 bg-slate-800/30 rounded-xl border border-slate-700/30">
              <div class="text-xs text-slate-400 uppercase font-bold mb-1">平均件单价</div>
              <div class="text-base font-black text-white">¥{{ item.avg_unit_price }}</div>
            </div>
            <div class="p-3 bg-slate-800/30 rounded-xl border border-slate-700/30">
              <div class="text-xs text-slate-400 uppercase font-bold mb-1">单笔件数</div>
              <div class="text-base font-black text-white">{{ item.upt }} 件</div>
            </div>
          </div>

          <!-- 进度条分析 -->
          <div class="space-y-5">
            <div>
              <div class="flex justify-between text-xs mb-2 font-bold uppercase tracking-wider">
                <span class="text-slate-400">收入贡献率</span>
                <span class="text-purple-400">{{ item.rev_ratio }}%</span>
              </div>
              <div class="w-full bg-slate-800 h-2.5 rounded-full p-0.5 border border-slate-700/50">
                <div class="bg-gradient-to-r from-purple-600 to-purple-400 h-full rounded-full shadow-[0_0_10px_rgba(168,85,247,0.3)] transition-all duration-1000" 
                     :style="{ width: item.rev_ratio + '%' }"></div>
              </div>
            </div>
            <div>
              <div class="flex justify-between text-xs mb-2 font-bold uppercase tracking-wider">
                <span class="text-slate-400">销量占比</span>
                <span class="text-blue-400">{{ item.vol_ratio }}%</span>
              </div>
              <div class="w-full bg-slate-800 h-2.5 rounded-full p-0.5 border border-slate-700/50">
                <div class="bg-gradient-to-r from-blue-600 to-blue-400 h-full rounded-full shadow-[0_0_10px_rgba(59,130,246,0.3)] transition-all duration-1000" 
                     :style="{ width: item.vol_ratio + '%' }"></div>
              </div>
            </div>
          </div>

          <!-- 底部详情数据 -->
          <div class="mt-6 pt-4 border-t border-slate-800 flex justify-between items-center text-xs">
            <div class="text-slate-400">累计销售额 <span class="text-white font-mono font-bold ml-1">¥{{ item.revenue.toLocaleString() }}</span></div>
            <div class="text-slate-400">订单数 <span class="text-white font-mono font-bold ml-1">{{ item.order_count }}</span></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart, BarChart } from 'echarts/charts';
import {
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';
import { 
  TrendingUp, Package, BarChart3, PieChart as PieChartIcon, 
  Layers, ChevronDown, DollarSign, ShoppingBag, Target, Box,
  Zap, Activity, BarChart as BarChartIcon
} from 'lucide-vue-next';
import { productAnalysis } from '../data/mockData';

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  TooltipComponent,
  LegendComponent,
  GridComponent
]);

const productStats = computed(() => {
  const s = (productAnalysis as any).stats || {};
  return [
    { 
      label: '全站销售总额', subtitle: '业务规模概览', value: s.sales_amount || '¥0', 
      icon: DollarSign, color: 'text-emerald-400'
    },
    { 
      label: '单笔均件价', subtitle: '订单消费质量', value: s.avg_order_value || '¥0', 
      icon: Activity, color: 'text-blue-400'
    },
    { 
      label: '在售商品品种', subtitle: 'SKU丰富度', value: s.sku_count || '0', 
      icon: Box, color: 'text-purple-400'
    },
    { 
      label: '每日销售动能', subtitle: '日均销售件数', value: s.daily_velocity || '0', 
      icon: Zap, color: 'text-orange-400'
    },
    { 
      label: '支柱类目营收比', subtitle: '前三大类目销售额占比', value: s.top_concentration || '0%', 
      icon: Target, color: 'text-rose-400'
    },
    { 
      label: '订单累计总量', subtitle: '全站交易规模', value: s.order_total || '0', 
      icon: ShoppingBag, color: 'text-cyan-400'
    },
  ];
});

const categoryData = computed(() => productAnalysis.categoryData);

// 品类效能
const categoryEfficiency = computed(() => (productAnalysis as any).categoryEfficiency || []);

// 真实价格区间数据
const priceRangeData = computed(() => (productAnalysis as any).priceRangeData || []);

const colors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899'];

// 图表配置 - 品类占比
const categoryOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(15, 23, 42, 0.95)',
    borderColor: '#334155',
    borderWidth: 1,
    padding: [12, 16],
    textStyle: { color: '#fff', fontSize: 12 },
    formatter: (params: any) => {
      const data = params.data;
      return `
        <div style="min-width: 140px">
          <div style="font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #334155; padding-bottom: 4px; color: ${params.color}">
            ${params.name}
          </div>
          <div style="display: flex; justify-between; margin-bottom: 4px">
            <span style="color: #94a3b8">销售总额：</span>
            <span style="font-weight: bold; margin-left: auto">¥${data.value.toLocaleString()}</span>
          </div>
          <div style="display: flex; justify-between; margin-bottom: 4px">
            <span style="color: #94a3b8">订单总量：</span>
            <span style="font-weight: bold; margin-left: auto">${data.count} 笔</span>
          </div>
          <div style="display: flex; justify-between; margin-top: 8px; padding-top: 4px; border-top: 1px dashed #334155">
            <span style="color: #94a3b8">销售总额占比：</span>
            <span style="font-weight: bold; margin-left: auto">${params.percent}%</span>
          </div>
        </div>
      `;
    }
  },
  series: [
    {
      name: '品类占比',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#1e293b',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '16',
          fontWeight: 'bold',
          color: '#fff',
          formatter: '{b} 销售占比 {d}%'
        }
      },
      labelLine: {
        show: false
      },
      data: categoryData.value.map((d, i) => ({
        name: d.name,
        value: d.value,
        count: d.count, // 传递订单数数据
        itemStyle: { color: colors[i % colors.length] }
      }))
    }
  ]
}));

// 图表配置 - 价格区间
const priceRangeOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#1e293b',
    borderColor: '#334155',
    textStyle: { color: '#fff' },
    axisPointer: { type: 'shadow' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: priceRangeData.value.map(d => d.range),
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#94a3b8' }
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#334155', type: 'dashed' } },
    axisLabel: { color: '#94a3b8' }
  },
  series: [
    {
      data: priceRangeData.value.map(d => d.count),
      type: 'bar',
      barWidth: '40%',
      itemStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#10b981' },
            { offset: 1, color: '#059669' }
          ]
        },
        borderRadius: [4, 4, 0, 0]
      }
    }
  ]
}));
</script>
