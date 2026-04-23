<template>
  <div class="space-y-6">
    <!-- 关键指标卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div v-for="stat in stats" :key="stat.label" class="bg-slate-800 rounded-lg p-4 border border-slate-700">
        <div class="text-slate-400 text-sm mb-2">{{ stat.label }}</div>
        <div class="text-2xl font-bold text-white" :class="stat.colorClass">
          {{ stat.value }}
        </div>
      </div>
    </div>

    <!-- 月度销售趋势 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 class="text-xl font-semibold text-white mb-6">月度销售趋势</h3>
      <div class="h-[350px]">
        <v-chart class="h-full w-full" :option="monthlyOption" autoresize />
      </div>
    </div>

    <!-- 日销售趋势（最近30天） -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 class="text-xl font-semibold text-white mb-6">日销售趋势（最近30天）</h3>
      <div class="h-[300px]">
        <v-chart class="h-full w-full" :option="dailyOption" autoresize />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, BarChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  VisualMapComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';
import { dashboardStats } from '../data/mockData';

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  VisualMapComponent,
]);

// 使用从后端预计算的响应式数据
const monthlyData = computed(() => dashboardStats.monthlyData);
const dailyData = computed(() => dashboardStats.dailyData);

const stats = computed(() => {
  const kpi = dashboardStats.kpi;
  const growthRate = kpi.growthRate || 0;

  return [
    { label: '总销售额', value: `¥${(kpi.totalSales || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, colorClass: 'text-white' },
    { label: '订单总量', value: (kpi.totalOrders || 0).toLocaleString(), colorClass: 'text-white' },
    { label: '平均客单价', value: `¥${(kpi.avgPrice || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, colorClass: 'text-white' },
    { 
      label: '月度增长率', 
      value: `${growthRate >= 0 ? '+' : ''}${growthRate.toFixed(1)}%`, 
      colorClass: growthRate >= 0 ? 'text-green-400' : 'text-red-400' 
    },
  ];
});

const monthlyOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#1e293b',
    borderColor: '#334155',
    textStyle: { color: '#fff' },
    formatter: (params: any) => {
      let res = `<div style="font-weight:bold;margin-bottom:5px;border-bottom:1px solid #444;padding-bottom:3px;">${params[0].name}</div>`;
      params.forEach((item: any) => {
        const val = item.value;
        const formattedVal = item.seriesName === '销售额' ? val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : val.toLocaleString();
        res += `<div style="display:flex;justify-content:space-between;gap:20px;">
                  <span>${item.marker}${item.seriesName}</span>
                  <span style="font-weight:bold;">${item.seriesName === '销售额' ? '¥' : ''}${formattedVal}</span>
                </div>`;
      });
      return res;
    }
  },
  legend: {
    data: ['销售额', '订单数'],
    textStyle: { color: '#94a3b8' },
  },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    data: monthlyData.value.map(d => d.month),
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#94a3b8' },
  },
  yAxis: [
    {
      type: 'value',
      name: '销售额',
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#334155' } },
    },
    {
      type: 'value',
      name: '订单数',
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { show: false },
    },
  ],
  series: [
    {
      name: '销售额',
      type: 'line',
      smooth: true,
      data: monthlyData.value.map(d => d.sales),
      itemStyle: { color: '#3b82f6' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: 'rgba(59, 130, 246, 0.3)' }, { offset: 1, color: 'rgba(59, 130, 246, 0)' }]
        }
      },
    },
    {
      name: '订单数',
      type: 'bar',
      yAxisIndex: 1,
      data: monthlyData.value.map(d => d.orders),
      itemStyle: { color: '#10b981' },
    },
  ],
}));

const dailyOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#1e293b',
    borderColor: '#334155',
    textStyle: { color: '#fff' },
    formatter: (params: any) => {
      let res = `<div style="font-weight:bold;margin-bottom:5px;border-bottom:1px solid #444;padding-bottom:3px;">${params[0].name}</div>`;
      params.forEach((item: any) => {
        const val = item.value;
        const formattedVal = val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        res += `<div style="display:flex;justify-content:space-between;gap:20px;">
                  <span>${item.marker}${item.seriesName}</span>
                  <span style="font-weight:bold;">¥${formattedVal}</span>
                </div>`;
      });
      return res;
    }
  },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    data: dailyData.value.map(d => d.date),
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#94a3b8' },
  },
  yAxis: {
    type: 'value',
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#94a3b8' },
    splitLine: { lineStyle: { color: '#334155' } },
  },
  series: [
    {
      name: '销售额',
      type: 'line',
      smooth: true,
      data: dailyData.value.map(d => d.sales),
      itemStyle: { color: '#8b5cf6' },
      symbolSize: 6,
    },
  ],
}));
</script>
