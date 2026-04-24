<template>
  <div class="space-y-6">
    <!-- 标题与核心操作栏 -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg">
      <div class="flex items-center gap-3">
        <Database class="w-8 h-8 text-blue-400" />
        <div>
          <h1 class="text-2xl font-bold text-white">数据中心</h1>
          <p class="text-slate-400 text-sm">原始订单数据管理与维护</p>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-4 flex-1 justify-end">
        <!-- 搜索功能组 -->
        <div class="flex items-center bg-slate-700 rounded-lg overflow-hidden border border-slate-600 focus-within:border-blue-500 transition-all shadow-inner">
          <select v-model="searchColumn" class="bg-slate-800 text-slate-300 text-xs px-2 py-2 border-r border-slate-600 outline-none cursor-pointer">
            <option value="all">所有项</option>
            <option v-for="col in searchOptions" :key="col.value" :value="col.value">{{ col.label }}</option>
          </select>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索..." 
            class="bg-transparent text-white text-sm px-3 py-2 outline-none w-32 md:w-44"
            @keyup.enter="handleSearch"
          />
          <button @click="handleSearch" class="px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white transition-colors flex items-center gap-1">
            <Search class="w-3.5 h-3.5" />
            <span class="text-xs font-bold">搜索</span>
          </button>
        </div>

        <!-- 动作按钮组 -->
        <div class="flex items-center gap-2">
          <!-- 核心操作 -->
          <div class="flex items-center bg-slate-700/50 rounded-lg p-1 border border-slate-700">
            <button @click="triggerFileUpload" class="p-2 hover:bg-emerald-500/20 text-emerald-400 rounded-md transition-all flex items-center gap-1.5" title="上传 CSV">
              <Upload class="w-4 h-4" />
              <span class="text-xs font-medium hidden sm:inline">上传</span>
            </button>
            <div class="w-px h-4 bg-slate-700 mx-1"></div>
            <button @click="toggleAddForm" class="p-2 hover:bg-blue-500/20 text-blue-400 rounded-md transition-all flex items-center gap-1.5" title="添加数据">
              <Plus class="w-4 h-4" />
              <span class="text-xs font-medium hidden sm:inline">添加</span>
            </button>
          </div>

          <!-- 批量与清除操作 (动态宽度) -->
          <div class="flex items-center gap-2">
            <div 
              class="overflow-hidden transition-all duration-300 flex items-center"
              :style="{ width: selectedIds.size > 0 ? 'auto' : '0', opacity: selectedIds.size > 0 ? '1' : '0' }"
            >
              <button @click="handleBatchDelete" class="whitespace-nowrap flex items-center gap-2 px-3 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-bold shadow-lg shadow-amber-900/20 mr-2">
                <Trash2 class="w-3.5 h-3.5" />
                <span>删除选中的 {{ selectedIds.size }} 项</span>
              </button>
            </div>
            
            <button @click="handleClearAll" class="p-2 bg-rose-500/10 hover:bg-rose-500 text-rose-500 hover:text-white border border-rose-500/20 rounded-lg transition-all" title="清除全部数据">
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
          <input type="file" ref="fileInput" class="hidden" accept=".csv" @change="handleFileUpload" />
        </div>
      </div>
    </div>

    <!-- 添加数据面板 (Grid Layout) -->
    <div v-if="showAddForm" class="bg-slate-800 rounded-xl border border-blue-500/30 overflow-hidden animate-in fade-in slide-in-from-top-4 duration-300">
      <div class="bg-blue-500/10 px-6 py-3 border-b border-blue-500/20 flex justify-between items-center">
        <span class="text-blue-400 font-bold flex items-center gap-2 text-sm">
          <PlusCircle class="w-4 h-4" /> 新增订单记录
        </span>
      </div>
      <div class="p-6">
        <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <div v-for="h in headers" :key="h.key" class="space-y-1">
            <label class="text-xs text-slate-400 block px-1">{{ h.label }}</label>
            <input 
              v-model="newRecord[h.key]" 
              :type="h.key === 'price' || h.key === 'quantity' || h.key === 'amount' || h.key === 'age' ? 'number' : 'text'"
              :placeholder="h.label"
              @input="h.key === 'price' || h.key === 'quantity' ? calculateAmount() : null"
              class="w-full bg-slate-900 text-white text-sm p-2.5 rounded-lg outline-none border border-slate-700 focus:border-blue-500 transition-all shadow-inner"
            />
          </div>
        </div>
        <div class="mt-6 flex justify-end gap-3 border-t border-slate-700/50 pt-4">
          <button @click="toggleAddForm" class="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-all text-sm font-medium">
            取消
          </button>
          <button @click="submitNewRecord" class="px-8 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-all text-sm font-medium shadow-lg shadow-blue-900/20">
            确认提交
          </button>
        </div>
      </div>
    </div>

    <!-- 快速行内新增面板 (Grid Layout) -->
    <div v-if="inlineAddId" class="bg-slate-800 rounded-xl border border-blue-400 overflow-hidden animate-in fade-in slide-in-from-top-4 duration-300">
      <div class="bg-blue-600/10 px-6 py-3 border-b border-blue-600/20 flex justify-between items-center">
        <span class="text-blue-400 font-bold flex items-center gap-2 text-sm">
          <PlusCircle class="w-4 h-4" /> 快速为用户 [{{ inlineRecord.user_name }}] 新增订单
        </span>
      </div>
      <div class="p-6">
        <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <div v-for="h in headers" :key="'inline-'+h.key" class="space-y-1">
            <label class="text-xs text-slate-400 block px-1">{{ h.label }}</label>
            <input 
              v-model="inlineRecord[h.key]" 
              :type="h.key === 'price' || h.key === 'quantity' || h.key === 'amount' || h.key === 'age' ? 'number' : 'text'"
              :placeholder="h.label"
              :disabled="['user_id', 'user_name', 'city', 'gender', 'age'].includes(h.key)"
              @input="h.key === 'price' || h.key === 'quantity' ? calculateInlineAmount() : null"
              class="w-full bg-slate-900 text-white text-sm p-2.5 rounded-lg outline-none border border-slate-700 focus:border-blue-500 transition-all shadow-inner disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>
        </div>
        <div class="mt-6 flex justify-end gap-3 border-t border-slate-700/50 pt-4">
          <button @click="cancelInlineAdd" class="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-all text-sm font-medium">
            取消
          </button>
          <button @click="submitInlineAdd" class="px-8 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-all text-sm font-medium shadow-lg shadow-blue-900/20">
            确认快速提交
          </button>
        </div>
      </div>
    </div>

    <!-- 主数据表格 -->
    <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden shadow-lg">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-slate-700/50 text-slate-300 text-xs font-semibold uppercase tracking-wider border-b border-slate-700">
              <th class="py-4 px-4 text-center w-12">
                <input 
                  type="checkbox" 
                  :checked="isAllSelected" 
                  @change="toggleSelectAll"
                  class="w-4 h-4 rounded border-slate-600 bg-slate-800 text-blue-500 focus:ring-blue-500 focus:ring-offset-slate-800"
                />
              </th>
              <th v-for="h in headers" :key="h.key" class="py-4 px-4 text-left">{{ h.label }}</th>
              <th class="py-4 px-4 text-center">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-700/50">
            <tr v-if="loading" class="animate-pulse">
              <td :colspan="headers.length + 2" class="py-12 text-center text-slate-500">正在加载数据...</td>
            </tr>
            <tr v-else-if="orders.length === 0" class="hover:bg-slate-700/20 transition-colors">
              <td :colspan="headers.length + 2" class="py-12 text-center text-slate-500">未找到相关数据</td>
            </tr>
            <tr v-for="order in orders" :key="order.id" class="hover:bg-slate-700/30 transition-colors group" :class="{ 'bg-blue-500/5': selectedIds.has(Number(order.id)) }">
              <td class="py-4 px-4 text-center">
                <input 
                  type="checkbox" 
                  :checked="selectedIds.has(Number(order.id))"
                  @change="toggleSelect(Number(order.id))"
                  class="w-4 h-4 rounded border-slate-600 bg-slate-800 text-blue-500 focus:ring-blue-500 focus:ring-offset-slate-800"
                />
              </td>
              <template v-if="editingId === order.id">
                <!-- 编辑模式 -->
                <td v-for="h in headers" :key="h.key" class="py-3 px-2 border-b border-slate-700/50">
                  <input 
                    v-model="editRecord[h.key]" 
                    type="text" 
                    class="w-full bg-slate-900 text-white text-xs p-2 rounded border border-blue-500/50"
                  />
                </td>
                <td class="py-3 px-4 text-center">
                  <div class="flex items-center justify-center gap-2">
                    <button @click="saveEdit(order.id)" class="p-2 text-emerald-400 hover:bg-emerald-400/10 rounded transition-all">
                      <Save class="w-4 h-4" />
                    </button>
                    <button @click="cancelEdit" class="p-2 text-slate-400 hover:bg-slate-400/10 rounded transition-all">
                      <X class="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </template>
              <template v-else>
                <!-- 普通显示模式 -->
                <td v-for="h in headers" :key="h.key" class="py-4 px-4 text-sm text-slate-300">
                  <span v-if="h.key === 'amount' || h.key === 'price'" class="text-emerald-400 font-mono">¥{{ order[h.key]?.toLocaleString() }}</span>
                  <span v-else-if="h.key === 'purchase_time'" class="text-xs text-slate-400">{{ order[h.key] }}</span>
                  <span v-else>{{ order[h.key] }}</span>
                </td>
                <td class="py-4 px-4 text-center">
                  <div class="flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button @click="startInlineAdd(order)" class="p-2 text-blue-400 hover:bg-blue-400/10 rounded transition-all" title="以此用户快速新增">
                      <Plus class="w-4 h-4" />
                    </button>
                    <button @click="startEdit(order)" class="p-2 text-blue-400 hover:bg-blue-400/10 rounded transition-all" title="编辑">
                      <Edit2 class="w-4 h-4" />
                    </button>
                    <button @click="handleDelete(order.id)" class="p-2 text-red-400 hover:bg-red-400/10 rounded transition-all" title="删除">
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </template>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页控制 -->
      <div class="bg-slate-800/80 px-6 py-4 border-t border-slate-700 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div class="text-sm text-slate-400">
          显示 <span class="text-white font-medium">{{ startIndex + 1 }}</span> 到 <span class="text-white font-medium">{{ endIndex }}</span> 条，共 <span class="text-white font-medium">{{ total }}</span> 条记录
        </div>
        <div class="flex items-center gap-2">
          <button 
            @click="prevPage" 
            :disabled="currentPage === 1"
            class="p-2 bg-slate-700 hover:bg-slate-600 text-white rounded disabled:opacity-30 disabled:cursor-not-allowed transition-all"
          >
            <ChevronLeft class="w-5 h-5" />
          </button>
          
          <div class="flex items-center gap-1">
            <button 
              v-for="p in visiblePages" 
              :key="p" 
              @click="goToPage(p)"
              class="w-10 h-10 rounded text-sm font-medium transition-all"
              :class="currentPage === p ? 'bg-blue-600 text-white' : 'text-slate-400 hover:bg-slate-700 hover:text-white'"
            >
              {{ p }}
            </button>
          </div>

          <button 
            @click="nextPage" 
            :disabled="currentPage === totalPages"
            class="p-2 bg-slate-700 hover:bg-slate-600 text-white rounded disabled:opacity-30 disabled:cursor-not-allowed transition-all"
          >
            <ChevronRight class="w-5 h-5" />
          </button>
        </div>

        <!-- 跳转页面 -->
        <div class="flex items-center gap-2 border-l border-slate-700 pl-4">
          <span class="text-sm text-slate-400">前往</span>
          <div class="flex items-center bg-slate-700 rounded-lg overflow-hidden border border-slate-600 focus-within:border-blue-500 transition-all">
            <input 
              v-model="jumpPageNum" 
              type="number" 
              class="bg-transparent text-white text-sm px-3 py-1 outline-none w-16 text-center [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
              @keyup.enter="handleJumpPage"
            />
            <button @click="handleJumpPage" class="px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white transition-colors">
              <Search class="w-3.5 h-3.5" />
            </button>
          </div>
          <span class="text-sm text-slate-400">页</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue';
import { 
  Database, Search, Plus, Upload, Trash2, Edit2, ChevronLeft, ChevronRight, 
  Save, X, PlusCircle, Check 
} from 'lucide-vue-next';
import { fetchAllStats } from '../data/mockData';

// 接口基础配置
const BASE_URL = '/api';

// 表头定义
const headers = [
  { key: 'user_id', label: '用户ID' },
  { key: 'user_name', label: '用户姓名' },
  { key: 'product_id', label: '商品ID' },
  { key: 'product_name', label: '商品名称' },
  { key: 'category', label: '商品类别' },
  { key: 'price', label: '单价' },
  { key: 'purchase_time', label: '购买时间' },
  { key: 'quantity', label: '购买数量' },
  { key: 'amount', label: '消费金额' },
  { key: 'city', label: '用户城市' },
  { key: 'gender', label: '用户性别' },
  { key: 'age', label: '用户年龄' },
];

const searchOptions = [
  { value: 'user_id', label: '用户ID' },
  { value: 'user_name', label: '用户姓名' },
  { value: 'product_id', label: '商品ID' },
  { value: 'product_name', label: '商品名称' },
  { value: 'category', label: '商品类别' },
  { value: 'price', label: '单价' },
  { value: 'purchase_time', label: '购买时间' },
  { value: 'quantity', label: '购买数量' },
  { value: 'amount', label: '消费金额' },
  { value: 'city', label: '用户城市' },
  { value: 'gender', label: '用户性别' },
  { value: 'age', label: '用户年龄' },
];

// 状态管理
const orders = ref<any[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = 10;
const loading = ref(false);
const searchQuery = ref('');
const searchColumn = ref('all');
const showAddForm = ref(false);
const fileInput = ref<HTMLInputElement | null>(null);
const jumpPageNum = ref<number | string>('');

// 选中状态
const selectedIds = ref(new Set<number>());
const isAllSelected = computed(() => {
  return orders.value.length > 0 && orders.value.every(o => selectedIds.value.has(Number(o.id)));
});

const toggleSelect = (id: number) => {
  if (selectedIds.value.has(id)) {
    selectedIds.value.delete(id);
  } else {
    selectedIds.value.add(id);
  }
};

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    orders.value.forEach(o => selectedIds.value.delete(Number(o.id)));
  } else {
    orders.value.forEach(o => selectedIds.value.add(Number(o.id)));
  }
};

const handleClearAll = async () => {
  if (!confirm('警告：此操作将永久删除数据库中的【全部】订单记录！是否继续？')) return;
  try {
    const res = await fetch(`${BASE_URL}/orders/clear`, { method: 'DELETE' });
    if (res.ok) {
      alert('已清空全部数据');
      fetchOrders();
      fetchAllStats();
    }
  } catch (err) {
    alert('操作失败');
  }
};

const handleBatchDelete = async () => {
  if (!confirm(`确定要删除选中的 ${selectedIds.value.size} 条记录吗？`)) return;
  try {
    const res = await fetch(`${BASE_URL}/orders/batch`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids: Array.from(selectedIds.value) })
    });
    if (res.ok) {
      selectedIds.value.clear();
      fetchOrders();
      fetchAllStats();
    }
  } catch (err) {
    alert('操作失败');
  }
};

// 编辑状态
const editingId = ref<number | null>(null);
const inlineAddId = ref<number | null>(null);
const editRecord = reactive<any>({});
const inlineRecord = reactive<any>({
  user_id: '', user_name: '', product_id: '', product_name: '',
  category: '', price: null, purchase_time: '',
  quantity: 1, amount: null, city: '', gender: '', age: null
});
const newRecord = reactive<any>({
  user_id: '', user_name: '', product_id: '', product_name: '',
  category: '', price: null, purchase_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
  quantity: 1, amount: null, city: '', gender: '', age: null
});

// 计算属性
const totalPages = computed(() => Math.ceil(total.value / pageSize));
const startIndex = computed(() => (currentPage.value - 1) * pageSize);
const endIndex = computed(() => Math.min(startIndex.value + pageSize, total.value));

const visiblePages = computed(() => {
  const range = [];
  const start = Math.max(1, currentPage.value - 2);
  const end = Math.min(totalPages.value, start + 4);
  for (let i = start; i <= end; i++) range.push(i);
  return range;
});

// 方法
const fetchOrders = async () => {
  loading.value = true;
  try {
    const url = new URL(`${BASE_URL}/orders`);
    url.searchParams.append('page', currentPage.value.toString());
    url.searchParams.append('limit', pageSize.toString());
    url.searchParams.append('search', searchQuery.value);
    url.searchParams.append('column', searchColumn.value);
    
    const res = await fetch(url.toString());
    const data = await res.json();
    
    if (res.ok) {
      orders.value = data.data || [];
      total.value = data.total || 0;
    } else {
      console.error('Backend error:', data.error);
      alert('加载数据失败: ' + (data.error || '未知错误'));
    }
  } catch (err) {
    console.error('Fetch error:', err);
    alert('无法连接到后端，请确保 Python 服务已启动。');
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  currentPage.value = 1;
  fetchOrders();
};

const triggerFileUpload = () => fileInput.value?.click();

const handleFileUpload = async (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch(`${BASE_URL}/upload`, {
      method: 'POST',
      body: formData
    });
    if (res.ok) {
      alert('上传成功并同步数据库！');
      fetchOrders();
      fetchAllStats(); // 同步大屏数据
    } else {
      const err = await res.json();
      alert('上传失败: ' + err.error);
    }
  } catch (err) {
    alert('请求失败，请检查后端。');
  }
};

const toggleAddForm = () => {
  showAddForm.value = !showAddForm.value;
};

const startInlineAdd = (order: any) => {
  inlineAddId.value = order.id;
  // Pre-populate with user info
  inlineRecord.user_id = order.user_id;
  inlineRecord.user_name = order.user_name;
  inlineRecord.city = order.city;
  inlineRecord.gender = order.gender;
  inlineRecord.age = order.age;
  // Defaults for new fields
  inlineRecord.product_id = '';
  inlineRecord.product_name = '';
  inlineRecord.category = '';
  inlineRecord.price = null;
  inlineRecord.quantity = 1;
  inlineRecord.amount = null;
  inlineRecord.purchase_time = new Date().toISOString().slice(0, 19).replace('T', ' ');
};

const cancelInlineAdd = () => {
  inlineAddId.value = null;
};

const calculateInlineAmount = () => {
  const price = parseFloat(inlineRecord.price);
  const qty = parseInt(inlineRecord.quantity);
  if (!isNaN(price) && !isNaN(qty)) {
    inlineRecord.amount = Number((price * qty).toFixed(2));
  } else if (!isNaN(price)) {
    inlineRecord.amount = price;
  }
};

const submitInlineAdd = async () => {
  try {
    if (!inlineRecord.product_id || !inlineRecord.price) {
      alert('请填写商品 ID 和单价');
      return;
    }
    const res = await fetch(`${BASE_URL}/orders`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(inlineRecord)
    });
    if (res.ok) {
      alert('行内添加成功！');
      inlineAddId.value = null;
      fetchOrders();
      fetchAllStats();
    }
  } catch (err) {
    alert('提交失败');
  }
};

const calculateAmount = () => {
  const price = parseFloat(newRecord.price);
  const qty = parseInt(newRecord.quantity);
  
  if (!isNaN(price) && !isNaN(qty)) {
    newRecord.amount = Number((price * qty).toFixed(2));
  } else if (!isNaN(price)) {
    newRecord.amount = price;
  }
};

const submitNewRecord = async () => {
  try {
    if (!newRecord.user_id || !newRecord.product_id || !newRecord.price) {
      alert('请填写必要字段：用户ID、商品ID、单价');
      return;
    }

    const res = await fetch(`${BASE_URL}/orders`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newRecord)
    });
    const data = await res.json();
    if (res.ok) {
      alert('添加成功！');
      showAddForm.value = false;
      
      // Reset form
      newRecord.user_id = '';
      newRecord.user_name = '';
      newRecord.product_id = '';
      newRecord.product_name = '';
      newRecord.category = '';
      newRecord.price = null;
      newRecord.purchase_time = new Date().toISOString().slice(0, 19).replace('T', ' ');
      newRecord.quantity = 1;
      newRecord.amount = null;
      newRecord.city = '';
      newRecord.gender = '';
      newRecord.age = null;

      fetchOrders();
      fetchAllStats(); // 同步大屏数据
    } else {
      alert('添加失败: ' + (data.error || '未知错误'));
    }
  } catch (err) {
    console.error('Submit error:', err);
    alert('提交失败，请检查网络或后端服务。');
  }
};

const startEdit = (order: any) => {
  editingId.value = order.id;
  Object.assign(editRecord, order);
};

const cancelEdit = () => {
  editingId.value = null;
};

const saveEdit = async (id: number) => {
  try {
    const res = await fetch(`${BASE_URL}/orders/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editRecord)
    });
    if (res.ok) {
      editingId.value = null;
      fetchOrders();
      fetchAllStats(); // 同步大屏数据
    }
  } catch (err) {
    alert('更新失败');
  }
};

const handleDelete = async (id: number) => {
  if (!confirm('确定删除此记录吗？')) return;
  try {
    const res = await fetch(`${BASE_URL}/orders/${id}`, {
      method: 'DELETE'
    });
    if (res.ok) {
      fetchOrders();
      fetchAllStats(); // 同步大屏数据
    }
  } catch (err) {
    alert('删除失败');
  }
};

const prevPage = () => { if (currentPage.value > 1) { currentPage.value--; fetchOrders(); } };
const nextPage = () => { if (currentPage.value < totalPages.value) { currentPage.value++; fetchOrders(); } };
const goToPage = (p: number) => { currentPage.value = p; jumpPageNum.value = p; fetchOrders(); };

const handleJumpPage = () => {
  const page = Number(jumpPageNum.value);
  if (page >= 1 && page <= totalPages.value) {
    goToPage(page);
  } else {
    alert(`请输入 1 到 ${totalPages.value} 之间的有效页码`);
  }
};

onMounted(fetchOrders);
</script>

<style scoped>
/* 自定义动画效果 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-in {
  animation: fadeIn 0.3s ease-out forwards;
}
</style>
