<template>
  <div class="space-y-6">
    <!-- 标题说明 -->
    <div class="bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-lg p-6 border border-purple-500/20">
      <div class="flex items-center gap-3 mb-2">
        <Sparkles class="w-6 h-6 text-purple-400" />
        <h2 class="text-2xl font-bold text-white">智能商品推荐系统</h2>
      </div>
      <p class="text-slate-300">基于协同过滤、关联规则和热度分析的多维度商品推荐</p>
    </div>

    <!-- 个性化推荐（协同过滤） -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div class="flex items-center gap-2 mb-4">
        <Users class="w-5 h-5 text-blue-400" />
        <h3 class="text-xl font-semibold text-white">个性化推荐（协同过滤）</h3>
      </div>
      <p class="text-slate-400 text-sm mb-4">
        基于相似用户的购买行为，推荐您可能感兴趣但尚未尝试的商品
      </p>
      
      <div class="mb-6 space-y-6">
        <div class="flex flex-col lg:flex-row gap-6 items-end">
          <!-- 搜索部分 -->
          <div class="flex-1 w-full lg:max-w-xl">
            <label class="block text-slate-400 text-xs font-medium mb-1.5 px-1">精准搜索用户</label>
            <div class="flex items-center bg-slate-700 rounded-lg border border-slate-600 focus-within:border-blue-500 transition-all overflow-hidden">
              <select v-model="searchType" class="bg-slate-800 text-slate-300 text-sm px-3 py-2 border-r border-slate-600 outline-none cursor-pointer">
                <option value="id">用户ID</option>
                <option value="name">用户姓名</option>
              </select>
              <div class="relative flex-1">
                <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input 
                  v-model="searchKeyword" 
                  type="text" 
                  :placeholder="searchType === 'id' ? '输入完整ID...' : '输入姓名关键词...'" 
                  class="w-full bg-transparent text-white text-sm pl-10 pr-4 py-2 outline-none"
                  @keyup.enter="handleManualSearch"
                />
              </div>
              <button @click="handleManualSearch" class="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold transition-colors">
                搜索并应用
              </button>
            </div>
          </div>
          
          <div class="hidden lg:flex items-center justify-center py-2 h-10">
            <div class="w-px h-8 bg-slate-700"></div>
            <span class="px-3 text-slate-500 text-xs font-bold italic">OR</span>
            <div class="w-px h-8 bg-slate-700"></div>
          </div>

          <!-- 直接选择部分 -->
          <div class="flex-1 w-full lg:max-w-xs">
            <label class="block text-slate-400 text-xs font-medium mb-1.5 px-1">从列表挑选用户</label>
            <select
              v-model="selectedUserId"
              @change="onUserChange"
              class="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2 text-sm focus:border-blue-500 outline-none transition-all cursor-pointer"
            >
              <option value="">-- 直接点击挑选 --</option>
              <option v-for="user in allAvailableUsers" :key="user.id" :value="user.id">
                {{ user.id }} - {{ user.name }}
              </option>
            </select>
          </div>
        </div>
        
        <!-- 搜索状态提示 -->
        <p v-if="searchStatus" :class="searchStatus.type === 'success' ? 'text-emerald-400' : 'text-rose-400'" class="text-xs px-1 animate-pulse font-medium">
          {{ searchStatus.msg }}
        </p>
      </div>

      <div v-if="selectedUserId && userRecs.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="rec in userRecs" :key="rec.productName" class="bg-slate-700/50 rounded-lg p-4 hover:bg-slate-700 transition-colors">
          <div class="flex items-start justify-between mb-2">
            <span class="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded">
              {{ rec.category }}
            </span>
            <span class="text-xs text-slate-400">{{ rec.buyCount }}人购买</span>
          </div>
          <h4 class="text-white font-medium mb-2">{{ rec.productName }}</h4>
          <div class="flex items-center justify-between">
            <span class="text-green-400 font-semibold">
              ¥{{ rec.avgPrice.toLocaleString() }}
            </span>
            <div class="text-xs text-slate-500">推荐指数: {{ rec.score.toFixed(1) }}</div>
          </div>
        </div>
      </div>

      <div v-else-if="selectedUserId" class="text-center py-8 text-slate-400 bg-slate-700/20 rounded-lg border border-dashed border-slate-600">
        正在为您计算推荐或该用户已购买所有品类...
      </div>
    </div>

    <!-- 组合推荐（关联规则） -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div class="flex items-center gap-2 mb-4">
        <Layers class="w-5 h-5 text-green-400" />
        <h3 class="text-xl font-semibold text-white">组合推荐（关联规则）</h3>
      </div>
      <p class="text-slate-400 text-sm mb-6">
        基于历史订单发现经常一起购买的品类组合，通过交叉销售提升客单价
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="pair in associationRules" :key="pair.items.join('-')" class="bg-slate-700/50 rounded-lg p-4 hover:bg-slate-700 transition-colors border border-transparent hover:border-green-500/30">
          <div class="flex items-start justify-between mb-3">
            <div class="flex gap-1 flex-wrap">
              <span class="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded">{{ pair.items[0] }}</span>
              <span class="text-slate-500 text-xs py-1">+</span>
              <span class="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded">{{ pair.items[1] }}</span>
            </div>
            <span class="text-xs text-slate-500 font-mono">支持度: {{ pair.support }}</span>
          </div>
          <p class="text-white text-sm font-medium mb-3 leading-relaxed">
            {{ pair.description }}
          </p>
          <div class="pt-2 border-t border-slate-700">
            <span class="text-green-400 text-xs font-bold">{{ pair.potential }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 热门商品推荐 -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div class="flex items-center gap-2 mb-4">
        <TrendingUp class="w-5 h-5 text-orange-400" />
        <h3 class="text-xl font-semibold text-white">热门商品推荐</h3>
      </div>
      <p class="text-slate-400 text-sm mb-6">
        基于全平台销量和收入的顶级爆款排行
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mb-8">
        <div v-for="(product, index) in visiblePopularProducts" :key="product.productId" class="bg-slate-700/50 rounded-lg p-4 hover:bg-slate-700 transition-all duration-300">
          <div class="flex items-start justify-between mb-3">
            <div :class="[
              'w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm',
              index === 0 ? 'bg-yellow-500 text-slate-900' :
              index === 1 ? 'bg-slate-400 text-slate-900' :
              index === 2 ? 'bg-orange-600 text-white' :
              'bg-slate-600 text-slate-300'
            ]">
              {{ index + 1 }}
            </div>
            <span class="px-2 py-1 bg-orange-500/20 text-orange-400 text-xs rounded">
              {{ product.category }}
            </span>
          </div>
          <h4 class="text-white font-medium mb-3 line-clamp-2 min-h-[2.5rem]">
            {{ product.productName }}
          </h4>
          <div class="space-y-2">
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">销量</span>
              <span class="text-white font-semibold">{{ product.sales }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">总消费额</span>
              <span class="text-green-400 font-semibold">
                ¥{{ product.revenue.toLocaleString(undefined, { maximumFractionDigits: 0 }) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="flex flex-col items-center gap-4">
        <div v-if="visiblePopularCount < popularProducts.length" class="flex items-center justify-center gap-4">
          <button 
            @click="showMorePopular"
            class="flex items-center gap-2 px-8 py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-all text-sm font-medium border border-slate-600 active:scale-95"
          >
            查看更多 (剩 {{ popularProducts.length - visiblePopularCount }})
          </button>
          <button 
            @click="showAllPopular"
            class="flex items-center gap-2 px-8 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-all text-sm font-medium shadow-lg shadow-blue-900/20 active:scale-95"
          >
            显示全部商品
          </button>
        </div>
        
        <button 
          v-if="visiblePopularCount > 8"
          @click="visiblePopularCount = 8"
          class="px-8 py-2 text-slate-500 hover:text-slate-300 text-sm transition-colors border border-transparent hover:border-slate-700 rounded-lg"
        >
          收起列表
        </button>
      </div>
    </div>

    <!-- 推荐算法说明 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-slate-800/50 rounded-xl p-6 border border-slate-700 hover:border-blue-500/30 transition-all">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
            <Users class="w-6 h-6 text-blue-400" />
          </div>
          <h4 class="text-white font-bold text-lg">协同过滤</h4>
        </div>
        <p class="text-slate-400 text-sm leading-relaxed">
          分析相似用户的购买行为，推荐“喜欢这个的人也喜欢...”类型的商品，提升转换率。
        </p>
      </div>
      
      <div class="bg-slate-800/50 rounded-xl p-6 border border-slate-700 hover:border-green-500/30 transition-all">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
            <Layers class="w-6 h-6 text-green-400" />
          </div>
          <h4 class="text-white font-bold text-lg">关联规则</h4>
        </div>
        <p class="text-slate-400 text-sm leading-relaxed">
          挖掘商品之间的关联关系，推荐经常一起购买的商品组合，提升客单价和交叉销售。
        </p>
      </div>

      <div class="bg-slate-800/50 rounded-xl p-6 border border-slate-700 hover:border-orange-500/30 transition-all">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center">
            <TrendingUp class="w-6 h-6 text-orange-400" />
          </div>
          <h4 class="text-white font-bold text-lg">热度分析</h4>
        </div>
        <p class="text-slate-400 text-sm leading-relaxed">
          基于销量和收入数据，推荐当前最受欢迎的商品，利用从众心理促进购买决策。
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { Sparkles, TrendingUp, Users, Layers, Search } from 'lucide-vue-next';
import { productAnalysis, userList, productRecommendation, fetchUserRecs, BASE_URL } from '../data/mockData';

const selectedUserId = ref('');
const searchType = ref<'id' | 'name'>('name');
const searchKeyword = ref('');
const searchStatus = ref<{ type: 'success' | 'error', msg: string } | null>(null);

const onUserChange = () => {
  if (selectedUserId.value) {
    searchKeyword.value = '';
    searchStatus.value = null;
    fetchUserRecs(selectedUserId.value);
  }
};

const handleManualSearch = async () => {
  const kw = searchKeyword.value.trim();
  if (!kw) return;

  searchStatus.value = { type: 'success', msg: '正在数据库中检索...' };

  try {
    const res = await fetch(`${BASE_URL}/users/search?keyword=${encodeURIComponent(kw)}&type=${searchType.value}`);
    const found = await res.json();

    if (found) {
      selectedUserId.value = found.id;
      searchStatus.value = { type: 'success', msg: `已找到并选中用户: ${found.name} (${found.id})` };
      fetchUserRecs(found.id);
    } else {
      searchStatus.value = { type: 'error', msg: `数据库中未找到匹配的${searchType.value === 'id' ? '用户ID' : '姓名'}` };
    }
  } catch (err) {
    searchStatus.value = { type: 'error', msg: '搜索请求失败，请检查后端服务' };
  }
};

const userRecs = computed(() => productRecommendation.userRecs);
const associationRules = computed(() => productRecommendation.associationRules);

const popularProducts = computed(() => {
  return (productAnalysis.productRanking || []).map(p => ({
    productId: p.key,
    productName: p.name,
    category: p.category,
    sales: p.sales,
    revenue: p.revenue
  }));
});

// 热门商品列表控制
const visiblePopularCount = ref(8);
const visiblePopularProducts = computed(() => popularProducts.value.slice(0, visiblePopularCount.value));

const showMorePopular = () => {
  visiblePopularCount.value += 8;
};

const showAllPopular = () => {
  visiblePopularCount.value = popularProducts.value.length;
};

const allAvailableUsers = computed(() => userList.slice(0, 100));
</script>
