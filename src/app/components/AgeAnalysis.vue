<template>
  <div class="space-y-6">
    <!-- 年龄段概览卡片 -->
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
      <div v-for="stat in ageRangeStats" :key="stat.range" class="bg-slate-800 rounded-lg p-4 border border-slate-700">
        <div class="flex items-center gap-2 mb-3">
          <div 
            class="w-3 h-3 rounded-full"
            :style="{ backgroundColor: stat.color }"
          ></div>
          <h4 class="text-white font-semibold">{{ stat.range }}</h4>
        </div>
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-slate-400 text-sm">用户数</span>
            <span class="text-white font-semibold">{{ stat.count }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-slate-400 text-sm">消费额</span>
            <span class="text-green-400 font-semibold text-sm">
              ¥{{ stat.totalAmount.toLocaleString(undefined, { maximumFractionDigits: 0 }) }}
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-slate-400 text-sm">客单价</span>
            <span class="text-blue-400 font-semibold text-sm">
              ¥{{ stat.avgAmount.toLocaleString(undefined, { maximumFractionDigits: 0 }) }}
            </span>
          </div>
          <div class="pt-2 border-t border-slate-700">
            <span class="text-slate-400 text-xs">偏好: </span>
            <span class="text-purple-400 text-xs font-medium">{{ stat.topCategory }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 年龄段消费对比 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 class="text-xl font-semibold text-white mb-6">年龄段消费对比</h3>
      <div class="h-[300px]">
        <v-chart class="h-full w-full" :option="ageComparisonOption" autoresize />
      </div>
    </div>

    <!-- 年龄分布细节 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 class="text-xl font-semibold text-white mb-6">年龄分布详情</h3>
      <div class="h-[300px]">
        <v-chart class="h-full w-full" :option="ageDistributionOption" autoresize />
      </div>
    </div>

    <!-- 年龄段品类偏好 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 class="text-xl font-semibold text-white mb-6">年龄段品类消费分布</h3>
      <div class="h-[350px]">
        <v-chart class="h-full w-full" :option="ageCategoryOption" autoresize />
      </div>
    </div>

    <!-- 年龄段洞察 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div v-for="insight in insights" :key="insight.title" :class="[insight.bgClass, 'rounded-lg p-6 border', insight.borderClass]">
        <div class="flex items-center gap-3 mb-3">
          <component :is="insight.icon" :class="['w-6 h-6', insight.iconClass]" />
          <h4 class="text-white font-semibold">{{ insight.title }}</h4>
        </div>
        <p class="text-slate-300 text-sm">
          {{ insight.content }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, LineChart } from 'echarts/charts';
import {
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';
import { Users, TrendingUp, DollarSign } from 'lucide-vue-next';
import { ageAnalysis } from '../data/mockData';

use([
  CanvasRenderer,
  BarChart,
  LineChart,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

const ageRanges = [
  { label: '18岁以下', color: '#60a5fa' },
  { label: '18-25岁', color: '#3b82f6' },
  { label: '26-35岁', color: '#8b5cf6' },
  { label: '36-45岁', color: '#10b981' },
  { label: '46-55岁', color: '#f59e0b' },
  { label: '56-65岁', color: '#ef4444' },
  { label: '66岁以上', color: '#991b1b' },
];

const ageRangeStats = computed(() => {
  return (ageAnalysis.ageRangeStats || []).map((stat, i) => ({
    ...stat,
    color: ageRanges[i]?.color || '#94a3b8',
  }));
});

const ageComparisonOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#1e293b',
    borderColor: '#334155',
    textStyle: { color: '#fff' },
    formatter: (params: any) => {
      const rangeName = params[0].name;
      const stat = ageRangeStats.value.find(s => s.range === rangeName);
      const countStr = stat ? ` (${stat.count}人)` : '';
      let res = `<div style="font-weight:bold;margin-bottom:5px;border-bottom:1px solid #444;padding-bottom:3px;">${rangeName}${countStr}</div>`;
      params.forEach((item: any) => {
        const val = item.value;
        const formattedVal = item.seriesName === '客单价' ? val.toFixed(2) : val.toLocaleString();
        res += `<div style="display:flex;justify-content:space-between;gap:20px;">
                  <span>${item.marker}${item.seriesName}</span>
                  <span style="font-weight:bold;">${formattedVal}</span>
                </div>`;
      });
      return res;
    }
  },
  legend: { textStyle: { color: '#94a3b8' } },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    data: ageRangeStats.value.map(d => d.range),
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#94a3b8' },
  },
  yAxis: [
    {
      type: 'value',
      name: '总消费',
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#334155' } },
    },
    {
      type: 'value',
      name: '客单价',
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { show: false },
    },
  ],
  series: [
    {
      name: '总消费',
      type: 'bar',
      data: ageRangeStats.value.map((d, i) => ({
        value: d.totalAmount,
        itemStyle: { color: d.color, borderRadius: [4, 4, 0, 0] }
      })),
    },
    {
      name: '客单价',
      type: 'line',
      yAxisIndex: 1,
      data: ageRangeStats.value.map(d => d.avgAmount),
      itemStyle: { color: '#10b981' },
      smooth: true,
    },
  ],
}));

const ageDistributionOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#1e293b',
    borderColor: '#334155',
    textStyle: { color: '#fff' },
  },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    name: '年龄',
    data: ageAnalysis.ageDistribution.map(d => d.age),
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#94a3b8' },
  },
  yAxis: {
    type: 'value',
    name: '数量',
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#94a3b8' },
    splitLine: { lineStyle: { color: '#334155' } },
  },
  series: [
    {
      name: '用户数',
      type: 'line',
      smooth: true,
      data: ageAnalysis.ageDistribution.map(d => d.count),
      itemStyle: { color: '#3b82f6' },
      showSymbol: false,
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: 'rgba(59, 130, 246, 0.3)' }, { offset: 1, color: 'rgba(59, 130, 246, 0)' }]
        }
      },
    },
  ],
}));

const ageCategoryOption = computed(() => {
  const categories = ['电子产品', '服装', '美妆', '运动', '书籍', '玩具', '家居'];
  const data = ageAnalysis.categoryByAge || [];
  
  return {
    backgroundColor: 'transparent',
    tooltip: { 
      trigger: 'axis', 
      axisPointer: { type: 'shadow' },
      backgroundColor: '#1e293b',
      borderColor: '#334155',
      textStyle: { color: '#fff' },
      formatter: (params: any) => {
        let res = `<div style="font-weight:bold;margin-bottom:5px;border-bottom:1px solid #444;padding-bottom:3px;">${params[0].name}</div>`;
        params.forEach((item: any) => {
          if (item.value > 0) {
            res += `<div style="display:flex;justify-content:space-between;gap:20px;">
                      <span>${item.marker}${item.seriesName}</span>
                      <span style="font-weight:bold;">¥${item.value.toFixed(2)}</span>
                    </div>`;
          }
        });
        return res;
      }
    },
    legend: { textStyle: { color: '#94a3b8' }, bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: data.map(d => d.ageRange),
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#334155' } },
    },
    series: categories.map(cat => ({
      name: cat,
      type: 'bar',
      stack: 'total',
      emphasis: { focus: 'series' },
      data: data.map(d => d[cat] || 0)
    }))
  };
});

const insights = computed(() => {
  const data = ageAnalysis.insights || [];
  const iconMap: any = {
    core: { icon: Users, bg: 'bg-blue-500/10', border: 'border-blue-500/20', text: 'text-blue-400' },
    potential: { icon: TrendingUp, bg: 'bg-purple-500/10', border: 'border-purple-500/20', text: 'text-purple-400' },
    high_value: { icon: DollarSign, bg: 'bg-green-500/10', border: 'border-green-500/20', text: 'text-green-400' }
  };

  return data.map((item: any) => {
    const style = iconMap[item.type] || iconMap.core;
    return {
      title: item.title,
      content: item.content,
      icon: style.icon,
      bgClass: style.bg,
      borderClass: style.border,
      iconClass: style.text
    };
  });
});
</script>
