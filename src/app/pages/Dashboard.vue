<template>
  <div class="space-y-6">
    <!-- 标题 -->
    <div class="flex items-center gap-3">
      <BarChart3 class="w-8 h-8 text-blue-400" />
      <div>
        <h1 class="text-3xl font-bold text-white">电商数据分析大屏</h1>
        <p class="text-slate-400 mt-1">实时监控核心业务指标与数据洞察</p>
      </div>
    </div>

    <!-- 标签页导航 -->
    <div class="bg-slate-800 rounded-lg p-2 border border-slate-700 overflow-x-auto">
      <div class="flex gap-2 min-w-max">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="flex items-center gap-2 px-4 py-3 rounded-lg transition-all whitespace-nowrap"
          :class="activeTab === tab.id
            ? 'bg-blue-500 text-white'
            : 'text-slate-400 hover:text-white hover:bg-slate-700'"
        >
          <component :is="tab.icon" class="w-5 h-5" />
          <span class="font-medium">{{ tab.label }}</span>
        </button>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="relative min-h-[400px]">
      <component :is="currentComponent" :key="activeTab" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, shallowRef, markRaw } from 'vue';
import { 
  BarChart3, Users, Package, TrendingUp, User, MapPin, Award, Sparkles 
} from 'lucide-vue-next';
import SalesTrend from '../components/SalesTrend.vue';
import UserDistribution from '../components/UserDistribution.vue';
import ProductAnalysis from '../components/ProductAnalysis.vue';
import GenderAnalysis from '../components/GenderAnalysis.vue';
import AgeAnalysis from '../components/AgeAnalysis.vue';
import CityConsumption from '../components/CityConsumption.vue';
import RFMAnalysis from '../components/RFMAnalysis.vue';
import ProductRecommendation from '../components/ProductRecommendation.vue';
import { fetchAllStats } from '../data/mockData';

type TabType = 'trend' | 'users' | 'products' | 'gender' | 'age' | 'city' | 'rfm' | 'recommendation';

const activeTab = ref<TabType>('trend');

onMounted(() => {
  fetchAllStats();
});

const tabs = [
  { id: 'trend' as TabType, label: '销售趋势', icon: markRaw(TrendingUp) },
  { id: 'users' as TabType, label: '用户分析', icon: markRaw(Users) },
  { id: 'gender' as TabType, label: '性别分析', icon: markRaw(Users) },
  { id: 'age' as TabType, label: '年龄分析', icon: markRaw(User) },
  { id: 'city' as TabType, label: '城市消费', icon: markRaw(MapPin) },
  { id: 'products' as TabType, label: '商品销售', icon: markRaw(Package) },
  { id: 'rfm' as TabType, label: 'RFM分析', icon: markRaw(Award) },
  { id: 'recommendation' as TabType, label: '商品推荐', icon: markRaw(Sparkles) },
];

const componentMap: Record<TabType, any> = {
  trend: markRaw(SalesTrend),
  users: markRaw(UserDistribution),
  products: markRaw(ProductAnalysis),
  gender: markRaw(GenderAnalysis),
  age: markRaw(AgeAnalysis),
  city: markRaw(CityConsumption),
  rfm: markRaw(RFMAnalysis),
  recommendation: markRaw(ProductRecommendation),
};

const currentComponent = computed(() => componentMap[activeTab.value]);
</script>
