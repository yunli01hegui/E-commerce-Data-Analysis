# 🎯 电商全栈数据分析与智能推荐系统

> 基于 **Vue 3 + Python Flask + MySQL + DeepSeek AI** 的全链路电商大数据分析平台。

本项目实现了从原始订单数据（CSV/MySQL）到可视化大屏洞察，再到 AI 驱动的深度商业分析的完整闭环。它不仅能处理天猫、京东、拼多多等跨平台数据，还集成了协同过滤算法与大语言模型，为电商运营提供精准的决策支持。

---

## ✨ 核心特性

### 📊 7 大维度数据看板 (ECharts 驱动)
*   **销售趋势分析**: 实时监控 GMV、订单量、客单价及月度环比增长率 (MoM)。
*   **用户画像洞察**: 性别比例、消费能力对比及品类偏好雷达图。
*   **年龄周期分析**: 划分为 7 个生命周期阶段，自动识别核心群体与高价值用户。
*   **城市消费矩阵**: 覆盖一线/新一线城市，通过散点图量化城市消费力。
*   **商品爆款排行**: 统计品类构成及全站 TOP 15 畅销单品。
*   **RFM 客户模型 ⭐**: 自动将客户划分为 8 类（重要价值、重要挽留等），支持精准营销。
*   **多维推荐系统**: 集成**基于用户的协同过滤 (User-CF)** 与**月度关联规则挖掘**。

### 🤖 DeepSeek AI 智能专家
*   **全链路分析报告**: 自动生成包含业绩评估、用户解析与增长建议的深度报告。
*   **用户行为建模**: 挖掘下单时段特征、消费决策路径与心理动机。
*   **算法优化方案**: AI 驱动的推荐引擎迭代建议，助力技术架构演进。
*   **智能缓存机制**: 基于数据库版本校验 (Checksum)，仅在数据变动时重生成报告，极大节省 Token 成本。

### 🛠️ 数据中心 (Data Management)
*   **多平台兼容**: 支持 1688、京东、拼多多、淘宝、天猫等各平台 CSV 数据一键导入。
*   **完整 CRUD**: 生产级别的订单管理功能，支持搜索、新增、行内编辑与批量删除。
*   **实时同步**: 数据库操作后，大屏分析数据与 AI 报告状态秒级同步。

---

## 🚀 快速开始

### 1. 环境准备
*   **前端**: Node.js (建议 18+)
*   **后端**: Python 3.9+
*   **数据库**: MySQL 8.0+

### 2. 后端配置
1.  安装依赖：`pip install -r backend/requirements.txt`
2.  配置数据库：在 `backend/app.py` 中修改 `DB_PASSWORD`。
3.  初始化数据：执行 `python backend/db_init.py`（默认加载 `backend/data/天猫.csv`）。
4.  配置 AI：在 `backend/app.py` 中填入你的 `DEEPSEEK_API_KEY`。
5.  启动服务：`npm run server` (或 `python backend/app.py`)。

### 3. 前端启动
1.  安装依赖：`npm install`
2.  启动预览：`npm run dev`
3.  访问地址：`http://localhost:5173`

---

## 📂 项目结构

```text
├── backend/              # Flask 后端
│   ├── app.py            # API 入口与 DeepSeek 逻辑
│   ├── db_init.py        # 数据库初始化与 CSV 导入
│   ├── data/             # 跨平台种子数据 (.csv)
│   └── ai_cache.json     # AI 报告版本化缓存
├── src/app/              # Vue 3 前端
│   ├── components/       # ECharts 可视化组件
│   ├── pages/            # 大屏、数据中心、AI 页面
│   ├── data/             # API 请求封装 (mockData.ts)
│   └── utils/            # 通用工具 (api.ts)
└── 数据计算公式文档.md      # 核心算法与 KPI 计算逻辑
```

---

## 🛠️ 技术栈详情

*   **前端**: Vue 3.4, TypeScript, Vite, Tailwind CSS v4, ECharts 5.5.
*   **后端**: Flask, Pandas (向量化计算), SQLAlchemy, PyMySQL.
*   **AI**: DeepSeek-V3 API, Markdown 动态渲染。
*   **算法**: 余弦相似度 (Cosine Similarity), 五分位数法 (RFM Score), 关联规则 (Association Rules).

---

## 📊 数据来源说明
基础数据集基于阿里云天池 [Tianchi Dataset 216886](https://tianchi.aliyun.com/dataset/216886)，经脱敏处理并由系统自动化扩展至生产级测试规模。

---

<div align="center">
  <strong>电商数据分析平台</strong> | Powered by DeepSeek AI & Flask
</div>
