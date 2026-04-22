<template>
  <div class="space-y-6">
    <!-- 概览卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div v-for="gender in ['男', '女']" :key="gender" class="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div :class="[
              'w-12 h-12 rounded-full flex items-center justify-center',
              gender === '男' ? 'bg-blue-500/20' : 'bg-pink-500/20'
            ]">
              <Users :class="['w-6 h-6', gender === '男' ? 'text-blue-400' : 'text-pink-400']" />
            </div>
            <h3 class="text-xl font-semibold text-white">{{ gender }}性用户</h3>
          </div>
          <div :class="[
            'px-3 py-1 rounded-full text-sm font-medium',
            gender === '男' ? 'bg-blue-500/20 text-blue-400' : 'bg-pink-500/20 text-pink-400'
          ]">
            {{ genderStats[gender]?.orderCount || 0 }} 人
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-slate-700/50 rounded-lg p-4">
            <div class="text-slate-400 text-sm mb-1">总消费</div>
            <div class="text-white text-xl font-bold">¥{{ (genderStats[gender]?.totalAmount || 0).toLocaleString() }}</div>
          </div>
          <div class="bg-slate-700/50 rounded-lg p-4">
            <div class="text-slate-400 text-sm mb-1">平均客单价</div>
            <div class="text-white text-xl font-bold">¥{{ (genderStats[gender]?.totalAmount / genderStats[gender]?.orderCount || 0).toLocaleString(undefined, { maximumFractionDigits: 0 }) }}</div>
          </div>
          <div class="bg-slate-700/50 rounded-lg p-4">
            <div class="text-slate-400 text-sm mb-1">订单数</div>
            <div class="text-white text-xl font-bold">{{ genderStats[gender]?.orderCount || 0 }}</div>
          </div>
          <div class="bg-slate-700/50 rounded-lg p-4">
            <div class="text-slate-400 text-sm mb-1">购买件数</div>
            <div class="text-white text-xl font-bold">{{ genderStats[gender]?.totalQuantity || 0 }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 性别分布与性别消费对比 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 性别分布 -->
      <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 class="text-xl font-semibold text-white mb-6">性别分布</h3>
        <div class="h-[250px]">
          <v-chart class="h-full w-full" :option="genderOption" autoresize />
        </div>
        <div class="flex flex-col justify-center space-y-2 mt-4">
          <div v-for="(item, index) in genderData" :key="item.name" class="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
            <div class="flex items-center gap-3">
              <div
                class="w-3 h-3 rounded-full"
                :style="{ backgroundColor: genderColors[index] }"
              ></div>
              <span class="text-white text-sm">{{ item.name === '男' ? '男性用户' : '女性用户' }}</span>
            </div>
            <div class="text-right">
              <span class="text-white font-semibold text-sm">{{ item.value }}人</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 性别对比分析 -->
      <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 class="text-xl font-semibold text-white mb-6">性别消费对比</h3>
        <div class="h-[330px]">
          <v-chart class="h-full w-full" :option="comparisonOption" autoresize />
        </div>
      </div>
    </div>

    <!-- 年龄分布 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 class="text-xl font-semibold text-white mb-6">年龄分布</h3>
      <div class="h-[300px]">
        <v-chart class="h-full w-full" :option="ageOption" autoresize />
      </div>
    </div>

    <!-- 品类偏好雷达图 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 class="text-xl font-semibold text-white mb-6">品类消费偏好（占比%）</h3>
      <div class="h-[400px]">
        <v-chart class="h-full w-full" :option="radarOption" autoresize />
      </div>
    </div>

    <!-- 地域分布对比 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div v-for="gender in ['男', '女']" :key="gender" class="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 class="text-xl font-semibold text-white mb-4">{{ gender }}性用户 TOP5 城市</h3>
        <div class="space-y-3">
          <div v-for="(item, index) in getTopCities(gender)" :key="item.city" class="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
            <div class="flex items-center gap-3">
              <div :class="[
                'w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm',
                index === 0 ? 'bg-yellow-500 text-slate-900' :
                index === 1 ? 'bg-slate-400 text-slate-900' :
                index === 2 ? 'bg-orange-600 text-white' :
                'bg-slate-600 text-slate-300'
              ]">
                {{ index + 1 }}
              </div>
              <span class="text-white font-medium">{{ item.city }}</span>
            </div>
            <span :class="['font-semibold', gender === '男' ? 'text-blue-400' : 'text-pink-400']">
              {{ item.count }} 订单
            </span>
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
import { BarChart, RadarChart, PieChart } from 'echarts/charts';
import {
  TooltipComponent,
  LegendComponent,
  GridComponent,
  PolarComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';
import { Users } from 'lucide-vue-next';
import { genderAnalysis, userDistribution } from '../data/mockData';

use([
  CanvasRenderer,
  BarChart,
  RadarChart,
  PieChart,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  PolarComponent,
]);

// 使用从后端预计算的响应式数据
const genderStats = computed(() => genderAnalysis.genderStats);
const comparisonData = computed(() => genderAnalysis.comparisonData);

const genderData = computed(() => userDistribution.genderData);
const ageData = computed(() => userDistribution.ageData);

const genderColors = ['#3b82f6', '#ec4899'];

const genderOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    backgroundColor: '#1e293b',
    borderColor: '#334155',
    textStyle: { color: '#fff' },
  },
  series: [
    {
      name: '性别分布',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#1e293b',
        borderWidth: 2
      },
      label: {
        show: true,
        formatter: '{b}: {d}%',
        color: '#94a3b8'
      },
      data: genderData.value.map((d, i) => ({
        value: d.value,
        name: d.name === '男' ? '男性' : '女性',
        itemStyle: { color: genderColors[i] }
      })),
    },
  ],
}));

const ageOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    backgroundColor: '#1e293b',
    borderColor: '#334155',
    textStyle: { color: '#fff' },
  },
  legend: {
    data: ['男性', '女性'],
    textStyle: { color: '#94a3b8' },
    top: 0
  },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    data: ageData.value.map(d => d.name),
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#94a3b8' },
  },
  yAxis: {
    type: 'value',
    name: '人数',
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#94a3b8' },
    splitLine: { lineStyle: { color: '#334155' } },
  },
  series: [
    {
      name: '男性',
      type: 'bar',
      barGap: '10%', // 男女柱子之间的间距
      data: ageData.value.map(d => d.male || 0),
      itemStyle: { 
        color: '#3b82f6',
        borderRadius: [4, 4, 0, 0] 
      },
    },
    {
      name: '女性',
      type: 'bar',
      data: ageData.value.map(d => d.female || 0),
      itemStyle: { 
        color: '#ec4899', 
        borderRadius: [4, 4, 0, 0] 
      },
    },
  ],
}));

// 动态从后端数据中获取品类列表，确保顺序一致
const categories = computed(() => (genderAnalysis.radarData || []).map(d => d.category));

const getTopCities = (gender: string) => {
  return gender === '男' ? genderAnalysis.maleTopCities : genderAnalysis.femaleTopCities;
};

const comparisonOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#1e293b',
    borderColor: '#334155',
    textStyle: { color: '#fff' },
    formatter: (params: any) => {
      const metricName = params[0].name;
      let res = `<div style="font-weight:bold;margin-bottom:5px;border-bottom:1px solid #444;padding-bottom:3px;">${metricName}</div>`;
      params.forEach((item: any) => {
        const val = item.value;
        // 如果 X 轴指标是平均客单价，保留两位小数
        const formattedVal = metricName === '平均客单价' ? val.toFixed(2) : val.toLocaleString();
        res += `<div style="display:flex;justify-content:space-between;gap:15px;">
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
    data: comparisonData.value.map(d => d.metric),
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
      name: '男性',
      type: 'bar',
      data: comparisonData.value.map(d => d.男),
      itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] },
    },
    {
      name: '女性',
      type: 'bar',
      data: comparisonData.value.map(d => d.女),
      itemStyle: { color: '#ec4899', borderRadius: [4, 4, 0, 0] },
    },
  ],
}));

const radarOption = computed(() => {
  const data = genderAnalysis.radarData || [];
  const maxVal = Math.max(...data.map(d => Math.max(d.男 || 0, d.女 || 0)), 10);
  const indicators = categories.value.map(cat => ({ 
    name: cat, 
    max: Math.ceil(maxVal / 10) * 10 
  }));

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1e293b',
      borderColor: '#334155',
      textStyle: { color: '#fff' },
      formatter: (params: any) => {
        const list = categories.value.map((cat, i) => {
          const val = params.value[i];
          return `<div style="display:flex; justify-content:space-between; gap:20px;">
                    <span>${cat}</span>
                    <span style="font-weight:bold; color:${params.color}">${val.toFixed(2)}%</span>
                  </div>`;
        }).join('');
        return `<div style="font-weight:bold; margin-bottom:5px; border-bottom:1px solid #444; padding-bottom:3px;">${params.name}品类偏好</div>${list}`;
      }
    },
    legend: { textStyle: { color: '#94a3b8' }, bottom: 0 },
    radar: {
      indicator: indicators,
      splitArea: { show: false },
      splitLine: { lineStyle: { color: '#334155' } },
      axisLine: { lineStyle: { color: '#334155' } },
      name: { textStyle: { color: '#94a3b8' } },
    },
    series: [
      {
        name: '性别品类偏好',
        type: 'radar',
        data: [
          {
            value: data.map(d => d.男 || 0),
            name: '男性',
            itemStyle: { color: '#3b82f6' },
            areaStyle: { opacity: 0.3 },
          },
          {
            value: data.map(d => d.女 || 0),
            name: '女性',
            itemStyle: { color: '#ec4899' },
            areaStyle: { opacity: 0.3 },
          },
        ],
      },
    ],
  };
});
</script>
