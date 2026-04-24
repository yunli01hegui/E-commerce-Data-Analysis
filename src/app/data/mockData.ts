import { ref, reactive } from 'vue';

export const BASE_URL = '/api';

export const dashboardStats = reactive({
  monthlyData: [] as any[],
  dailyData: [] as any[],
  kpi: {} as any
});

export const userDistribution = reactive({
  genderData: [] as any[],
  ageData: [] as any[],
  cityData: [] as any[]
});

export const productAnalysis = reactive({
  categoryData: [] as any[],
  productRanking: [] as any[]
});

export const rfmAnalysis = reactive({
  segmentStats: [] as any[],
  scatterData: [] as any[],
  rfmSegmented: [] as any[]
});

export const genderAnalysis = reactive({
  genderStats: {} as any,
  comparisonData: [] as any[],
  radarData: [] as any[],
  maleTopCities: [] as any[],
  femaleTopCities: [] as any[]
});

export const ageAnalysis = reactive({
  ageRangeStats: [] as any[],
  ageDistribution: [] as any[],
  categoryByAge: [] as any[],
  insights: [] as any[]
});

export const cityConsumption = reactive({
  cityData: [] as any[],
  tierStats: [] as any[]
});

export const userList = reactive([] as any[]);

export const productRecommendation = reactive({
  userRecs: [] as any[],
  associationRules: [] as any[]
});

export const isLoading = ref(false);
export const error = ref<string | null>(null);

/**
 * 通用的 fetch 函数
 */
async function apiFetch(endpoint: string) {
  const response = await fetch(`${BASE_URL}${endpoint}`);
  if (!response.ok) throw new Error(`Fetch failed: ${endpoint} ${response.status}`);
  return await response.json();
}

/**
 * 获取指定用户的协同过滤推荐
 */
export async function fetchUserRecs(userId: string) {
  if (!userId) return;
  try {
    const data = await apiFetch(`/recommendation/cf/${userId}`);
    productRecommendation.userRecs = data;
  } catch (err) {
    console.error('Failed to fetch user recs:', err);
  }
}

/**
 * 加载所有仪表盘数据
 */
export async function fetchAllStats() {
  isLoading.value = true;
  error.value = null;
  try {
    const endpoints = [
      { path: '/stats/sales-trend', target: dashboardStats },
      { path: '/stats/user-distribution', target: userDistribution },
      { path: '/stats/product-analysis', target: productAnalysis },
      { path: '/stats/rfm-analysis', target: rfmAnalysis },
      { path: '/stats/gender-analysis', target: genderAnalysis },
      { path: '/stats/age-analysis', target: ageAnalysis },
      { path: '/stats/city-consumption', target: cityConsumption },
      { path: '/users', target: userList, isArray: true },
      { path: '/recommendation/association', target: productRecommendation, isKey: 'associationRules' }
    ];

    const results = await Promise.allSettled(endpoints.map(e => apiFetch(e.path)));

    results.forEach((result, index) => {
      const endpoint = endpoints[index];
      if (result.status === 'fulfilled') {
        if (endpoint.isArray) {
          (endpoint.target as any[]).length = 0;
          (endpoint.target as any[]).push(...result.value);
        } else if (endpoint.isKey) {
          Object.assign(endpoint.target, { [endpoint.isKey]: result.value });
        } else {
          Object.assign(endpoint.target, result.value);
        }
      } else {
        console.error(`Failed to fetch ${endpoint.path}:`, result.reason);
      }
    });

    console.log('Finished loading stats from Flask backend (some may have failed)');
  } catch (err) {
    console.error('Critical failure in fetchAllStats:', err);
    error.value = '无法连接到 Python 后端。请确认服务已启动。';
  } finally {
    isLoading.value = false;
  }
}

export const allOrderData = reactive<any[]>([]);
export async function fetchOrderData() {
  await fetchAllStats();
}
