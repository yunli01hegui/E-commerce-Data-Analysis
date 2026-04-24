<template>
  <div class="space-y-6">
    <!-- 关键指标卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div v-for="stat in stats" :key="stat.label" class="bg-slate-800 rounded-lg p-4 border border-slate-700 min-w-0">
        <div class="text-slate-400 text-sm mb-2 truncate" :title="stat.label">{{ stat.label }}</div>
        <div 
          class="text-2xl font-bold text-white truncate" 
          :class="stat.colorClass"
          :title="stat.value"
        >
          {{ stat.value }}
        </div>
      </div>
    </div>

    <!-- 月度销售趋势 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <h3 class="text-xl font-semibold text-white">月度销售趋势</h3>
        <div class="flex items-center gap-2">
          <button 
            @click="monthlyYear = 'all'"
            :class="[
              'px-3 py-1.5 rounded-lg text-xs font-medium transition-all',
              monthlyYear === 'all' ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            ]"
          >
            全部数据
          </button>
          <div class="h-4 w-px bg-slate-700 mx-1"></div>
          <select 
            v-model="monthlyYear"
            class="bg-slate-900 text-slate-300 text-xs px-3 py-1.5 rounded-lg border border-slate-700 outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="all" disabled>选择年份</option>
            <option v-for="year in availableYears" :key="year" :value="year">{{ year }}年</option>
          </select>
        </div>
      </div>
      <div class="h-[350px]">
        <v-chart class="h-full w-full" :option="monthlyOption" autoresize />
      </div>
    </div>

    <!-- 日销售趋势 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <h3 class="text-xl font-semibold text-white">日销售趋势</h3>
        <div class="flex flex-wrap items-center gap-2">
          <button 
            @click="resetDailyFilter"
            :class="[
              'px-3 py-1.5 rounded-lg text-xs font-medium transition-all',
              dailyYear === 'all' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/20' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            ]"
          >
            全部数据
          </button>
          <div class="h-4 w-px bg-slate-700 mx-1"></div>
          <div class="flex items-center bg-slate-900 rounded-lg border border-slate-700 overflow-hidden">
            <select 
              v-model="dailyYear"
              @change="handleDailyYearChange"
              class="bg-transparent text-slate-300 text-xs px-3 py-1.5 outline-none border-r border-slate-700 cursor-pointer"
            >
              <option value="all" disabled>年份</option>
              <option v-for="year in availableYears" :key="year" :value="year">{{ year }}年</option>
            </select>
            <select 
              v-model="dailyMonth"
              :disabled="dailyYear === 'all'"
              class="bg-transparent text-slate-300 text-xs px-3 py-1.5 outline-none cursor-pointer disabled:opacity-50"
            >
              <option value="all" disabled>月份</option>
              <option v-for="month in availableMonthsForDaily" :key="month" :value="month">{{ month }}月</option>
            </select>
          </div>
        </div>
      </div>
      <div class="h-[300px]">
        <v-chart class="h-full w-full" :option="dailyOption" autoresize />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
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

// 筛选状态
const monthlyYear = ref('all');
const dailyYear = ref('all');
const dailyMonth = ref('all');

// 获取数据库中所有存在的年份
const availableYears = computed(() => {
  const years = new Set<string>();
  dashboardStats.monthlyData.forEach(d => {
    const year = d.month.split('-')[0];
    if (year) years.add(year);
  });
  return Array.from(years).sort((a, b) => b.localeCompare(a));
});

// 获取选中年份对应的月份列表 (用于日趋势筛选)
const availableMonthsForDaily = computed(() => {
  if (dailyYear.value === 'all') return [];
  const months = new Set<string>();
  dashboardStats.dailyData.forEach(d => {
    if (d.date.startsWith(dailyYear.value)) {
      const month = d.date.split('-')[1];
      if (month) months.add(month);
    }
  });
  return Array.from(months).sort((a, b) => a.localeCompare(b));
});

const handleDailyYearChange = () => {
  // 当年份改变时，如果当前选中的月份不在新年度内，则重置月份为第一个可用月份或 'all'
  const months = availableMonthsForDaily.value;
  if (months.length > 0) {
    dailyMonth.value = months[0];
  } else {
    dailyMonth.value = 'all';
  }
};

const resetDailyFilter = () => {
  dailyYear.value = 'all';
  dailyMonth.value = 'all';
};

// 过滤后的数据
const filteredMonthlyData = computed(() => {
  if (monthlyYear.value === 'all') return dashboardStats.monthlyData;
  return dashboardStats.monthlyData.filter(d => d.month.startsWith(monthlyYear.value));
});

const filteredDailyData = computed(() => {
  if (dailyYear.value === 'all') return dashboardStats.dailyData;
  let filtered = dashboardStats.dailyData.filter(d => d.date.startsWith(dailyYear.value));
  if (dailyMonth.value !== 'all') {
    const prefix = `${dailyYear.value}-${dailyMonth.value}`;
    filtered = filtered.filter(d => d.date.startsWith(prefix));
  }
  return filtered;
});

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
    right: 10
  },
  grid: { left: '3%', right: '6%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    name: '时间',
    data: filteredMonthlyData.value.map(d => d.month),
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
      data: filteredMonthlyData.value.map(d => d.sales),
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
      data: filteredMonthlyData.value.map(d => d.orders),
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
  grid: { left: '3%', right: '6%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    name: '时间',
    data: filteredDailyData.value.map(d => d.date),
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#94a3b8' },
  },
  yAxis: {
    type: 'value',
    name: '销售额',
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#94a3b8' },
    splitLine: { lineStyle: { color: '#334155' } },
  },
  series: [
    {
      name: '销售额',
      type: 'line',
      smooth: true,
      data: filteredDailyData.value.map(d => d.sales),
      itemStyle: { color: '#8b5cf6' },
      symbolSize: 6,
    },
  ],
}));
</script>
