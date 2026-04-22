import { ref, reactive } from 'vue';

const BASE_URL = 'http://localhost:5000/api';

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
  categoryByAge: [] as any[]
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
    const [sales, users, products, rfm, gender, age, cities, allUsers, associations] = await Promise.all([
      apiFetch('/stats/sales-trend'),
      apiFetch('/stats/user-distribution'),
      apiFetch('/stats/product-analysis'),
      apiFetch('/stats/rfm-analysis'),
      apiFetch('/stats/gender-analysis'),
      apiFetch('/stats/age-analysis'),
      apiFetch('/stats/city-consumption'),
      apiFetch('/users'),
      apiFetch('/recommendation/association')
    ]);

    // 更新响应式对象
    Object.assign(dashboardStats, sales);
    Object.assign(userDistribution, users);
    Object.assign(productAnalysis, products);
    Object.assign(rfmAnalysis, rfm);
    Object.assign(genderAnalysis, gender);
    Object.assign(ageAnalysis, age);
    Object.assign(cityConsumption, cities);
    Object.assign(productRecommendation, { associationRules: associations });

    userList.length = 0;
    userList.push(...allUsers);

    console.log('Successfully loaded all stats from Flask backend');
  } catch (err) {
    console.error('Failed to fetch from backend:', err);
    error.value = '无法连接到 Python 后端。请确认 MySQL 已启动并运行 "npm run server"';
  } finally {
    isLoading.value = false;
  }
}

export const allOrderData = reactive<any[]>([]);
export async function fetchOrderData() {
  await fetchAllStats();
}
