<template>
  <div class="space-y-6 pb-10">
    <!-- 高级指标看板 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      <div v-for="stat in premiumStats" :key="stat.label"
           class="bg-slate-800/40 backdrop-blur-md p-5 rounded-2xl border border-slate-700/50 shadow-xl hover:border-blue-500/30 transition-all group relative min-h-[110px] flex flex-col justify-between overflow-hidden">
        <div class="flex justify-between items-start">
          <div class="p-2 rounded-xl bg-slate-900/50 group-hover:scale-110 transition-transform shrink-0">
            <component :is="stat.icon" class="w-5 h-5" :class="stat.color" />
          </div>
          <div class="text-right flex flex-col ml-2">
            <span class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">{{ stat.label }}</span>
            <span class="text-[10px] text-slate-500 font-medium truncate max-w-[100px]">{{ stat.subtitle }}</span>
          </div>
        </div>
        <div class="text-right mt-3">
          <div class="text-lg font-bold text-white tracking-tight leading-none truncate" :title="stat.value">
            {{ stat.value }}
          </div>
        </div>
        <div class="absolute -bottom-4 -right-4 w-12 h-12 rounded-full blur-2xl opacity-10" :class="stat.color.replace('text', 'bg')"></div>
      </div>
    </div>

    <!-- 主趋势分析区域 -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <!-- 月度销售趋势 (占2/3) -->
      <div class="xl:col-span-2 bg-slate-800 rounded-2xl p-6 border border-slate-700 shadow-lg">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-blue-500/10 rounded-lg">
              <CalendarDays class="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h3 class="text-lg font-bold text-white">月度业绩走势</h3>
              <p class="text-xs text-slate-500">对比全站月度销售额与订单量的增长轨迹</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <select v-model="monthlyYear" class="bg-slate-900 text-slate-300 text-xs px-4 py-2 rounded-xl border border-slate-700 outline-none focus:border-blue-500 cursor-pointer transition-all">
              <option value="all">全部年度</option>
              <option v-for="year in availableYears" :key="year" :value="year">{{ year }}年</option>
            </select>
          </div>
        </div>
        <div class="h-[380px]">
          <v-chart class="h-full w-full" :option="monthlyOption" autoresize />
        </div>
      </div>

      <!-- 周权重分布 (占1/3) -->
      <div class="bg-slate-800 rounded-2xl p-6 border border-slate-700 shadow-lg">
        <div class="flex items-center gap-3 mb-8">
          <div class="p-2 bg-emerald-500/10 rounded-lg">
            <BarChartIcon class="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h3 class="text-lg font-bold text-white">周期销售分布</h3>
            <p class="text-xs text-slate-500">识别周内每日的成交热度差异</p>
          </div>
        </div>
        <div class="h-[380px]">
          <v-chart class="h-full w-full" :option="dayOfWeekOption" autoresize />
        </div>
      </div>
    </div>

    <!-- 次级趋势分析区域 -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <!-- 日销售波动 (占2/3) -->
      <div class="xl:col-span-2 bg-slate-800 rounded-2xl p-6 border border-slate-700 shadow-lg">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-purple-500/10 rounded-lg">
              <TrendingUp class="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h3 class="text-lg font-bold text-white">日销售精密波动</h3>
              <p class="text-xs text-slate-500">穿透至每日颗粒度的业绩波动监控</p>
            </div>
          </div>
          <div class="flex items-center gap-2 p-1 bg-slate-900 rounded-xl border border-slate-700">
            <select v-model="dailyYear" @change="handleDailyYearChange" class="bg-transparent text-slate-400 text-[10px] px-3 py-1 outline-none border-r border-slate-700 cursor-pointer">
              <option value="all">全部</option>
              <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
            </select>
            <select v-model="dailyMonth" :disabled="dailyYear === 'all'" class="bg-transparent text-slate-400 text-[10px] px-3 py-1 outline-none cursor-pointer disabled:opacity-30">
              <option value="all">整月</option>
              <option v-for="month in availableMonthsForDaily" :key="month" :value="month">{{ month }}月</option>
            </select>
          </div>
        </div>
        <div class="h-[320px]">
          <v-chart class="h-full w-full" :option="dailyOption" autoresize />
        </div>
      </div>

      <!-- 时段成交热力 (占1/3) -->
      <div class="bg-slate-800 rounded-2xl p-6 border border-slate-700 shadow-lg">
        <div class="flex items-center gap-3 mb-8">
          <div class="p-2 bg-orange-500/10 rounded-lg">
            <Clock class="w-5 h-5 text-orange-400" />
          </div>
          <div>
            <h3 class="text-lg font-bold text-white">24小时成交热点</h3>
            <p class="text-xs text-slate-500">锁定全天的消费黄金时段</p>
          </div>
        </div>
        <div class="h-[320px]">
          <v-chart class="h-full w-full" :option="hourlyOption" autoresize />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, BarChart } from 'echarts/charts';
import {
  TooltipComponent,
  LegendComponent,
  GridComponent,
  VisualMapComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';
import {
  TrendingUp, CalendarDays, BarChart as BarChartIcon,
  Clock, DollarSign, ShoppingBag, Activity,
  Zap, Award, TrendingDown
} from 'lucide-vue-next';
import { dashboardStats } from '../data/mockData';

use([
  CanvasRenderer, LineChart, BarChart,
  TooltipComponent, LegendComponent, GridComponent, VisualMapComponent
]);

// 筛选状态
const monthlyYear = ref('all');
const dailyYear = ref('all');
const dailyMonth = ref('all');

// 数据源
const availableYears = computed(() => {
  const years = new Set<string>();
  dashboardStats.monthlyData.forEach(d => {
    const year = d.month.split('-')[0];
    if (year) years.add(year);
  });
  return Array.from(years).sort((a, b) => b.localeCompare(a));
});

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
  dailyMonth.value = 'all';
};

// 仪表盘核心指标 (对接后端新 KPI)
const premiumStats = computed(() => {
  const k = dashboardStats.kpi || {};
  return [
    { label: '累计销售总额', subtitle: '全域经营规模', value: k.totalSales || '¥0', icon: DollarSign, color: 'text-emerald-400' },
    { label: '订单总规模', subtitle: '全站累计成单', value: k.totalOrders || '0', icon: ShoppingBag, color: 'text-blue-400' },
    { label: '平均客单价', subtitle: '单笔消费水平', value: k.avgPrice || '¥0', icon: Activity, color: 'text-purple-400' },
    { label: '单日销售峰值', subtitle: '历史成交极值', value: k.peakDaySales || '¥0', icon: Award, color: 'text-orange-400' },
    { label: '日均成单效率', subtitle: '平均单日订单', value: k.avgDailyOrders || '0 单', icon: Zap, color: 'text-cyan-400' },
    { label: '业绩增长率', subtitle: '对比上期表现', value: `${k.growthRate || 0}%`, icon: TrendingUp, color: 'text-rose-400' },
  ];
});

// 图表配置 - 月度趋势
const monthlyOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(15, 23, 42, 0.9)',
    borderColor: '#334155',
    textStyle: { color: '#fff' }
  },
  legend: { data: ['销售额', '订单量'], textStyle: { color: '#94a3b8' }, right: 0 },
  grid: { left: '2%', right: '2%', bottom: '2%', containLabel: true },
  xAxis: {
    type: 'category',
    data: (monthlyYear.value === 'all' ? dashboardStats.monthlyData : dashboardStats.monthlyData.filter(d => d.month.startsWith(monthlyYear.value))).map(d => d.month),
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#64748b', fontSize: 10 }
  },
  yAxis: [
    { type: 'value', name: '销售额', splitLine: { lineStyle: { color: '#334155', type: 'dashed' } }, axisLabel: { color: '#64748b' } },
    { type: 'value', name: '订单量', splitLine: { show: false }, axisLabel: { color: '#64748b' } }
  ],
  series: [
    {
      name: '销售额', type: 'line', smooth: true,
      data: (monthlyYear.value === 'all' ? dashboardStats.monthlyData : dashboardStats.monthlyData.filter(d => d.month.startsWith(monthlyYear.value))).map(d => d.sales),
      itemStyle: { color: '#3b82f6' },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(59, 130, 246, 0.2)' }, { offset: 1, color: 'rgba(59, 130, 246, 0)' }] } }
    },
    {
      name: '订单量', type: 'bar', barWidth: '30%', yAxisIndex: 1,
      data: (monthlyYear.value === 'all' ? dashboardStats.monthlyData : dashboardStats.monthlyData.filter(d => d.month.startsWith(monthlyYear.value))).map(d => d.orders),
      itemStyle: { color: '#10b981', borderRadius: [4, 4, 0, 0] }
    }
  ]
}));

// 图表配置 - 周分布
const dayOfWeekOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: '3%', right: '3%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#334155', type: 'dashed' } },
    axisLabel: { show: false }
  },
  yAxis: {
    type: 'category',
    data: (dashboardStats as any).dayOfWeekData?.map((d: any) => d.name) || [],
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#fff', fontWeight: 'bold' }
  },
  series: [{
    name: '销售额', type: 'bar', barWidth: '50%',
    data: (dashboardStats as any).dayOfWeekData?.map((d: any) => d.sales) || [],
    itemStyle: {
      color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#10b981' }, { offset: 1, color: '#34d399' }] },
      borderRadius: [0, 4, 4, 0]
    }
  }]
}));

// 图表配置 - 日趋势
const dailyOption = computed(() => {
  let data = dashboardStats.dailyData;
  if (dailyYear.value !== 'all') {
    data = data.filter(d => d.date.startsWith(dailyYear.value));
    if (dailyMonth.value !== 'all') {
      const prefix = `${dailyYear.value}-${dailyMonth.value}`;
      data = data.filter(d => d.date.startsWith(prefix));
    }
  }
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '2%', right: '2%', bottom: '2%', containLabel: true },
    xAxis: {
      type: 'category', data: data.map(d => d.date.split('-').slice(1).join('/')),
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#64748b', rotate: data.length > 15 ? 45 : 0 }
    },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#334155' } }, axisLabel: { color: '#64748b' } },
    series: [{
      name: '单日销售额', type: 'line', smooth: true,
      data: data.map(d => d.sales),
      itemStyle: { color: '#8b5cf6' },
      symbol: 'circle', symbolSize: 4
    }]
  };
});

// 图表配置 - 24时段热力
const hourlyOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: { trigger: 'axis' },
  grid: { left: '3%', right: '3%', bottom: '5%', top: '10%', containLabel: true },
  xAxis: {
    type: 'category',
    data: (dashboardStats as any).hourlyData?.map((d: any) => `${d.hour}:00`) || [],
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#64748b', fontSize: 9 }
  },
  yAxis: { type: 'value', splitLine: { show: false }, axisLabel: { show: false } },
  series: [{
    name: '订单量', type: 'bar',
    data: (dashboardStats as any).hourlyData?.map((d: any) => d.orders) || [],
    itemStyle: {
      color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#f59e0b' }, { offset: 1, color: '#d97706' }] },
      borderRadius: [4, 4, 0, 0]
    }
  }]
}));
</script>
