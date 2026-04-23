<template>
  <div class="space-y-6">
    <!-- RFM指标说明 -->
    <div class="bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg p-6 border border-blue-500/20">
      <h3 class="text-xl font-semibold text-white mb-4">RFM 模型分析</h3>
      <p class="text-slate-300 mb-4">
        RFM模型是衡量客户价值和创造利润能力的重要工具，通过三个维度评估客户：
      </p>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-for="desc in rfmDescriptions" :key="desc.title" class="bg-slate-800/50 rounded-lg p-4">
          <div class="flex items-center gap-2 mb-2">
            <component :is="desc.icon" :class="['w-5 h-5', desc.iconClass]" />
            <span class="text-white font-semibold">{{ desc.title }}</span>
          </div>
          <p class="text-slate-400 text-sm">{{ desc.content }}</p>
        </div>
      </div>
    </div>

    <!-- 客户分群概览 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div class="flex items-center gap-2 mb-6">
        <Users class="w-5 h-5 text-blue-400" />
        <h3 class="text-xl font-semibold text-white">客户分群概览</h3>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="seg in segmentArray" :key="seg.segment" class="bg-slate-700/50 rounded-lg p-4 border-l-4" :style="{ borderLeftColor: seg.color }">
          <div class="flex items-center justify-between mb-2">
            <h4 class="text-white font-semibold">{{ seg.segment }}</h4>
            <div 
              class="w-3 h-3 rounded-full"
              :style="{ backgroundColor: seg.color }"
            ></div>
          </div>
          <p class="text-slate-400 text-xs mb-3">{{ seg.desc }}</p>
          <div class="space-y-2">
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">RFM得分</span>
              <span class="text-white font-bold">{{ seg.avgRFM || '0.0' }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">客户数</span>
              <span class="text-white font-semibold">{{ seg.count }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">总消费</span>
              <span class="text-green-400 font-semibold">
                ¥{{ seg.totalAmount.toLocaleString(undefined, { maximumFractionDigits: 0 }) }}
              </span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">人均消费</span>
              <span class="text-blue-400 font-semibold">
                ¥{{ (seg.totalAmount / seg.count).toLocaleString(undefined, { maximumFractionDigits: 0 }) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- RFM二维矩阵：频率 vs 消费金额 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 class="text-xl font-semibold text-white mb-6">客户价值分布矩阵</h3>
      <p class="text-slate-400 text-sm mb-4">横轴：购买频率 | 纵轴：消费金额 | 颜色：客户分群</p>
      <div class="h-[450px]">
        <v-chart class="h-full w-full" :option="rfmMatrixOption" autoresize />
      </div>
    </div>

    <!-- TOP20 高价值客户 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div class="flex items-center gap-2 mb-6">
        <Award class="w-5 h-5 text-yellow-400" />
        <h3 class="text-xl font-semibold text-white">TOP 20 高价值客户</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-slate-700">
              <th class="text-left py-3 px-4 text-slate-400 font-medium">排名</th>
              <th class="text-left py-3 px-4 text-slate-400 font-medium">客户ID</th>
              <th class="text-left py-3 px-4 text-slate-400 font-medium">客户名称</th>
              <th class="text-left py-3 px-4 text-slate-400 font-medium">客户分群</th>
              <th class="text-center py-3 px-4 text-slate-400 font-medium">R评分</th>
              <th class="text-center py-3 px-4 text-slate-400 font-medium">F评分</th>
              <th class="text-center py-3 px-4 text-slate-400 font-medium">M评分</th>
              <th class="text-right py-3 px-4 text-slate-400 font-medium">消费总额</th>
              <th class="text-right py-3 px-4 text-slate-400 font-medium">购买次数</th>
              <th class="text-right py-3 px-4 text-slate-400 font-medium">距今天数</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(user, index) in rfmSegmented.slice(0, 20)" :key="user.userId" class="border-b border-slate-700/50 hover:bg-slate-700/30">
              <td class="py-3 px-4">
                <div :class="[
                  'w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm',
                  index === 0 ? 'bg-yellow-500 text-slate-900' :
                  index === 1 ? 'bg-slate-400 text-slate-900' :
                  index === 2 ? 'bg-orange-600 text-white' :
                  'bg-slate-600 text-slate-300'
                ]">
                  {{ index + 1 }}
                </div>
              </td>
              <td class="py-3 px-4 text-slate-300 font-mono text-sm">{{ user.userId }}</td>
              <td class="py-3 px-4 text-white">{{ user.userName }}</td>
              <td class="py-3 px-4">
                <span 
                  class="px-2 py-1 rounded text-xs font-medium"
                  :style="{ backgroundColor: `${user.segmentColor}20`, color: user.segmentColor }"
                >
                  {{ user.segment }}
                </span>
              </td>
              <td class="py-3 px-4 text-center">
                <span class="text-blue-400 font-semibold">{{ user.R }}</span>
              </td>
              <td class="py-3 px-4 text-center">
                <span class="text-purple-400 font-semibold">{{ user.F }}</span>
              </td>
              <td class="py-3 px-4 text-center">
                <span class="text-green-400 font-semibold">{{ user.M }}</span>
              </td>
              <td class="py-3 px-4 text-right text-green-400 font-semibold">
                ¥{{ user.monetary.toLocaleString() }}
              </td>
              <td class="py-3 px-4 text-right text-white">{{ user.frequency }}</td>
              <td class="py-3 px-4 text-right text-slate-400">{{ user.recency }}天</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 客户策略 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div class="flex items-center gap-2 mb-6">
        <Sparkles class="w-5 h-5 text-purple-400" />
        <h3 class="text-xl font-semibold text-white">针对性客户策略</h3>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="strategy in activeStrategies" :key="strategy.segment" class="bg-slate-700/30 rounded-xl p-5 border border-slate-600 hover:border-blue-500/50 transition-all">
          <div class="flex items-center gap-3 mb-4">
            <div 
              class="w-4 h-4 rounded-full"
              :style="{ backgroundColor: strategy.color }"
            ></div>
            <h4 class="text-white font-bold text-lg">{{ strategy.segment }}策略</h4>
          </div>
          <div class="space-y-3">
            <div v-for="(item, idx) in strategy.items" :key="idx" class="flex gap-3">
              <span class="flex-shrink-0 w-5 h-5 rounded-full bg-slate-600 text-blue-400 text-xs flex items-center justify-center font-bold">
                {{ idx + 1 }}
              </span>
              <p class="text-slate-300 text-sm leading-relaxed">{{ item }}</p>
            </div>
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
import { ScatterChart } from 'echarts/charts';
import {
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';
import { Users, Clock, ShoppingCart, DollarSign, Award, Sparkles } from 'lucide-vue-next';
import { rfmAnalysis } from '../data/mockData';

use([
  CanvasRenderer,
  ScatterChart,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

// 使用从后端预计算的响应式数据
const rfmSegmented = computed(() => rfmAnalysis.rfmSegmented);
const segmentStats = computed(() => rfmAnalysis.segmentStats);

const segmentArray = computed(() => {
  return Object.values(segmentStats.value).sort((a: any, b: any) => (b.avgRFM || 0) - (a.avgRFM || 0));
});

const rfmDescriptions = [
  { title: 'Recency (最近一次购买)', content: '客户最近一次购买距今的时间，越近越好', icon: Clock, iconClass: 'text-blue-400' },
  { title: 'Frequency (购买频率)', content: '客户在一定时期内的购买次数，越多越好', icon: ShoppingCart, iconClass: 'text-purple-400' },
  { title: 'Monetary (消费金额)', content: '客户在一定时期内的消费总额，越高越好', icon: DollarSign, iconClass: 'text-green-400' },
];

const strategyMap: Record<string, string[]> = {
  '重要价值客户': [
    '维持其高频消费，推送高客单价新品',
    '邀请加入 VIP 社群，提供专属管家服务',
    '定期进行专属回访，确保其对品牌的极高忠诚度'
  ],
  '重要发展客户': [
    '分析其近期购买品类，精准推送关联商品组合',
    '提供大额优惠券激励复购，提升购买频次',
    '将其纳入会员培养体系，关注其成长轨迹'
  ],
  '重要保持客户': [
    '提供重聚礼包，通过老客召回活动激活',
    '分析流失前购买习惯，推送其最感兴趣的内容',
    '加强品牌情感连接，提醒其积分即将过期'
  ],
  '重要挽留客户': [
    '重点回访，通过电话或短信进行深度关怀',
    '赠送高面额礼券，通过大力度促销吸引回归',
    '深入调研流失原因，改善服务细节'
  ],
  '一般价值客户': [
    '重点进行交叉销售，通过组合购买提升消费额',
    '引导其关注官方社交账号，增强品牌心智',
    '定期推送新品资讯和大众化活动'
  ],
  '一般发展客户': [
    '推荐平台热门爆款，降低其试错成本',
    '引导参与签到、抽奖等互动，提高访问频率',
    '推送其曾经浏览但未下单的商品折扣'
  ],
  '一般保持客户': [
    '推送低门槛激活券，测试其回归意愿',
    '保持周期性的品牌曝光，不进行强力打扰',
    '推荐相似品类的替代款，挖掘潜在需求'
  ],
  '一般挽留客户': [
    '进行低成本唤醒，如节假日祝福和限时活动',
    '利用极低价格的清仓活动吸引二次尝试',
    '保持基础曝光，等待需求自然恢复'
  ],
  '潜力客户': [
    '推荐热门新品，引导尝试更多品类',
    '设置会员升级阶梯奖励，激发成长动力',
    '加强互动沟通，建立初步品牌认知'
  ]
};

// 动态生成策略列表，确保与后端返回的分群对应
const activeStrategies = computed(() => {
  return segmentArray.value.map(seg => ({
    segment: seg.segment,
    color: seg.color,
    items: strategyMap[seg.segment] || ['持续关注客户需求，提供标准服务', '定期推送平台资讯', '保持基础沟通渠道']
  }));
});

const rfmMatrixOption = computed(() => {
  const maxFreq = rfmAnalysis.scatterData.length > 0 
    ? Math.max(...rfmAnalysis.scatterData.map((d: any) => d.x)) 
    : 10;

  return {
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: '#1e293b',
      borderColor: '#334155',
      textStyle: { color: '#fff' },
      formatter: (params: any) => {
        return `${params.data[3]} (${params.data[4]})<br/>频次: ${params.data[0]}<br/>金额: ¥${params.data[1].toLocaleString()}`;
      }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'value',
      name: '购买频率',
      max: maxFreq + 1,
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#334155' } },
    },
    yAxis: {
      type: 'value',
      name: '消费金额',
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#334155' } },
    },
    series: [
      {
        name: '客户价值',
        type: 'scatter',
        data: rfmAnalysis.scatterData.map((d: any) => [d.x, d.y, d.z, d.name, d.segment, d.segmentColor]),
        symbolSize: (data: any) => Math.sqrt(data[1]) / 5,
        itemStyle: {
          color: (params: any) => params.data[5],
          opacity: 0.7
        },
      },
    ],
  };
});
</script>
