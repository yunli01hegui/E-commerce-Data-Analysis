<template>
  <div class="space-y-6">
    <!-- 性别分布 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 class="text-xl font-semibold text-white mb-6">性别分布</h3>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="h-[250px]">
          <v-chart class="h-full w-full" :option="genderOption" autoresize />
        </div>
        <div class="flex flex-col justify-center space-y-4">
          <div v-for="(item, index) in genderData" :key="item.name" class="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg">
            <div class="flex items-center gap-3">
              <div
                class="w-4 h-4 rounded-full"
                :style="{ backgroundColor: genderColors[index] }"
              ></div>
              <span class="text-white font-medium">{{ item.name === '男' ? '男性用户' : '女性用户' }}</span>
            </div>
            <div class="text-right">
              <div class="text-white font-semibold">{{ item.value }}人</div>
              <div class="text-slate-400 text-sm">¥{{ item.amount.toLocaleString() }}</div>
            </div>
          </div>
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

    <!-- 地域分布 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 class="text-xl font-semibold text-white mb-6">地域分布 TOP 10</h3>
      <div class="h-[350px]">
        <v-chart class="h-full w-full" :option="cityOption" autoresize />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart, BarChart } from 'echarts/charts';
import {
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';
import { userDistribution } from '../data/mockData';

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

const genderData = computed(() => userDistribution.genderData);
const ageData = computed(() => userDistribution.ageData);
const cityData = computed(() => userDistribution.cityData);

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

const cityOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#1e293b',
    borderColor: '#334155',
    textStyle: { color: '#fff' },
    formatter: (params: any) => {
      const data = cityData.value[params[0].dataIndex];
      return `${data.city}<br/>订单数: ${data.count}<br/>销售额: ¥${data.amount.toLocaleString()}`;
    }
  },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'value',
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#94a3b8' },
    splitLine: { lineStyle: { color: '#334155' } },
  },
  yAxis: {
    type: 'category',
    data: cityData.value.map(d => d.city),
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#94a3b8' },
  },
  series: [
    {
      name: '订单数',
      type: 'bar',
      data: cityData.value.map(d => d.count),
      itemStyle: { color: '#10b981', borderRadius: [0, 4, 4, 0] },
    },
  ],
}));
</script>
