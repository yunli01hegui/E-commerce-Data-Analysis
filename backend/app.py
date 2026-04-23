from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
from sqlalchemy import create_engine, text
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
import importlib

# =================================================================
# 后端程序入口文件
# 架构：Flask + SQLAlchemy + Pandas + Flasgger
# 功能：为前端提供电商数据分析所需的统计、推荐及数据管理接口
# =================================================================

# 将当前目录添加到系统路径，确保能够正确导入同级目录下的 db_init.py 脚本
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# 开启跨域资源共享 (CORS)，允许前端（通常运行在 5173 端口）跨域调用本接口
CORS(app)

# -----------------------------------------------------------------
# Swagger API 文档配置
# 访问地址：http://localhost:5000/apidocs
# -----------------------------------------------------------------
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda rule: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

template = {
    "swagger": "2.0",
    "info": {
        "title": "电商全栈数据分析系统 - API 接口文档",
        "description": "本接口文档详细列出了系统的所有后端服务。包括基于大数据量的统计接口、基于机器学习思路的推荐算法接口，以及数据中心管理接口。",
        "contact": {
            "responsibleOrganization": "Data Team",
            "email": "support@example.com"
        },
        "version": "1.0.0"
    },
    "basePath": "/api",  # 所有接口的基础路径
    "schemes": ["http"]
}

swagger = Swagger(app, config=swagger_config, template=template)

# -----------------------------------------------------------------
# 数据库连接配置
# -----------------------------------------------------------------
DB_USER = 'root'
DB_PASSWORD = '' # 如果 MySQL 设置了密码，请在此填写
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'tmall_analytics'

# 创建 SQLAlchemy 数据库连接引擎
# 使用 pymysql 驱动连接 MySQL
engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

def get_df():
    """
    【通用数据加载函数】
    逻辑：
    1. 执行全表查询从 MySQL 获取最新订单数据。
    2. 使用 Pandas 加载数据，以便进行高效的向量化计算。
    3. 将 'purchase_time' 强制转换为 datetime 类型，确保后续的时间序列分析正确。
    """
    try:
        df = pd.read_sql("SELECT * FROM orders", con=engine)
        if 'purchase_time' in df.columns:
            df['purchase_time'] = pd.to_datetime(df['purchase_time'])
        return df
    except Exception as e:
        print(f"致命错误：无法读取数据库数据。原因: {e}")
        return pd.DataFrame()

# =================================================================
# 1. 数据统计接口组 (Data Visualization Stats)
# =================================================================

@app.route('/api/stats/user-distribution', methods=['GET'])
def user_distribution():
    """
    获取用户画像分布（性别、年龄、城市）
    ---
    tags:
      - 大屏数据接口
    description: 综合分析用户的基础属性分布，用于大屏“用户分布”模块。
    responses:
      200:
        description: 成功返回 JSON 格式的分组统计数据
    """
    try:
        df = get_df()
        if df.empty: return jsonify({'genderData': [], 'ageData': [], 'cityData': []})
        
        # 1. 性别分布：按性别分组，统计人数(value)和累计消费金额(amount)
        gender_data = df.groupby('gender').agg(
            value=('user_id', 'count'),
            amount=('amount', 'sum')
        ).reset_index().rename(columns={'gender': 'name'})
        gender_data['amount'] = gender_data['amount'].astype(float)
        gender_data_list = gender_data.to_dict('records')

        # 2. 年龄分布：根据业务逻辑将年龄切分为不同生命周期阶段，并包含性别细分
        age_bins = [0, 18, 25, 35, 45, 55, 65, 120]
        age_labels = ['18岁以下', '18-25岁', '26-35岁', '36-45岁', '46-55岁', '56-65岁', '66岁以上']
        df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels, include_lowest=True)
        
        # 基础统计（总数、金额）
        age_base = df.groupby('age_group', observed=False).agg(
            count=('user_id', 'count'),
            amount=('amount', 'sum')
        ).reset_index()
        
        # 性别细分统计
        age_gender = df.groupby(['age_group', 'gender'], observed=False).size().unstack(fill_value=0).reset_index()
        
        # 合并数据
        age_combined = pd.merge(age_base, age_gender, on='age_group')
        
        # 转换为前端格式
        age_data_list = []
        for _, row in age_combined.iterrows():
            age_data_list.append({
                'name': str(row['age_group']),
                'count': int(row['count']),
                'amount': float(row['amount']),
                'male': int(row.get('男', 0)),
                'female': int(row.get('女', 0))
            })

        # 3. 城市消费排行：找出消费力最强的 TOP 10 城市
        city_data = df.groupby('city').agg(
            count=('user_id', 'count'),
            amount=('amount', 'sum')
        ).reset_index().sort_values('amount', ascending=False).head(10)
        city_data['amount'] = city_data['amount'].astype(float)
        city_data_list = city_data.to_dict('records')

        return jsonify({
            'genderData': gender_data_list,
            'ageData': age_data_list,
            'cityData': city_data_list
        })
    except Exception as e:
        print(f"Error in user_distribution: {e}")
        return jsonify({'genderData': [], 'ageData': [], 'cityData': []})

@app.route('/api/stats/product-analysis', methods=['GET'])
def product_analysis():
    """
    获取商品及品类销售分析
    ---
    tags:
      - 大屏数据接口
    description: 统计全站品类的销售构成，并罗列出吸金能力最强的爆款商品.
    responses:
      200:
        description: 包含品类占比和商品排行榜
    """
    try:
        df = get_df()
        if df.empty: return jsonify({'categoryData': [], 'productRanking': []})
        
        # 1. 品类统计：计算各品类的总销售额和订单占比
        category_data = df.groupby('category').agg(
            value=('amount', 'sum'),
            count=('user_id', 'count')
        ).reset_index().rename(columns={'category': 'name'}).sort_values('value', ascending=False)
        category_data['value'] = category_data['value'].astype(float)
        category_data_list = category_data.to_dict('records')

        # 2. 爆款排行：综合统计单个商品的销售总量、总收入和成单数
        product_ranking = df.groupby(['product_name', 'category']).agg(
            sales=('quantity', 'sum'),
            revenue=('amount', 'sum'),
            orders=('user_id', 'count')
        ).reset_index().sort_values('revenue', ascending=False).head(15)
        
        product_ranking['revenue'] = product_ranking['revenue'].astype(float)
        product_ranking['sales'] = product_ranking['sales'].astype(int)
        product_ranking_list = product_ranking.to_dict('records')
        
        # 构建唯一键，解决前端表格渲染 Key 重复问题
        for p in product_ranking_list:
            p['key'] = f"{p['product_name']}-{p['category']}"
            p['name'] = p.pop('product_name')

        return jsonify({
            'categoryData': category_data_list,
            'productRanking': product_ranking_list
        })
    except Exception as e:
        print(f"Error in product_analysis: {e}")
        return jsonify({'categoryData': [], 'productRanking': []})

@app.route('/api/stats/sales-trend', methods=['GET'])
def sales_trend():
    """
    获取全站销售趋势及关键绩效指标 (KPI)
    ---
    tags:
      - 大屏数据接口
    description: 计算最近 12 个月的月度趋势，以及过去 30 天的实时销量。
    responses:
      200:
        description: 成功返回趋势图数据及 KPI
    """
    try:
        df = get_df()
        if df.empty: return jsonify({'monthlyData': [], 'dailyData': [], 'kpi': {}})
        
        # 1. 月度趋势：只显示有数据的年月
        # 使用 strftime 格式化日期作为分组键
        df['month_key'] = df['purchase_time'].dt.strftime('%Y-%m')
        monthly_stats = df.groupby('month_key').agg(
            sales=('amount', 'sum'),
            orders=('user_id', 'count')
        ).sort_index().reset_index()
        
        monthly_data = []
        for _, row in monthly_stats.iterrows():
            orders_val = int(row['orders'])
            sales_val = float(row['sales'])
            monthly_data.append({
                'month': str(row['month_key']),
                'sales': sales_val,
                'orders': orders_val,
                'avgAmount': float(sales_val / orders_val) if orders_val > 0 else 0.0
            })
        # 2. 每日趋势：显示数据库中所有有数据的日期，按日期排序
        daily = df.groupby(df['purchase_time'].dt.date).agg(
            sales=('amount', 'sum'),
            orders=('user_id', 'count')
        ).sort_index().reset_index()
        
        daily['date'] = daily['purchase_time'].apply(lambda x: x.strftime('%Y-%m-%d'))
        daily_data = daily[['date', 'sales', 'orders']].to_dict('records')

        # 3. 计算全局 KPI 指标
        total_sales = float(df['amount'].sum())
        total_orders = int(len(df))
        avg_price = float(total_sales / total_orders) if total_orders > 0 else 0.0
        
        # 环比增长率计算：对比数据中的最新月份和上一个月
        if not monthly_stats.empty:
            # 按月份排序获取最后一个月作为“本月”
            sorted_stats = monthly_stats.sort_values('month_key')
            latest_row = sorted_stats.iloc[-1]
            curr_month_key = latest_row['month_key']
            curr_sales = float(latest_row['sales'])
            
            # 计算上个月的 key
            latest_date = pd.to_datetime(curr_month_key + '-01')
            prev_month_date = latest_date - pd.Timedelta(days=1)
            last_month_key = prev_month_date.strftime('%Y-%m')
            
            prev_sales = float(monthly_stats[monthly_stats['month_key'] == last_month_key]['sales'].sum())
            growth_rate = float(((curr_sales - prev_sales) / prev_sales * 100)) if prev_sales > 0 else 0.0
        else:
            growth_rate = 0.0

        return jsonify({
            'monthlyData': monthly_data,
            'dailyData': daily_data,
            'kpi': {
                'totalSales': total_sales,
                'totalOrders': total_orders,
                'avgPrice': avg_price,
                'growthRate': growth_rate
            }
        })
    except Exception as e:
        print(f"Error in sales_trend: {e}")
        return jsonify({'monthlyData': [], 'dailyData': [], 'kpi': {}})

@app.route('/api/stats/gender-analysis', methods=['GET'])
def gender_analysis():
    """
    获取多维度的性别消费对比分析
    """
    try:
        df = get_df()
        if df.empty: return jsonify({'genderStats': {}, 'comparisonData': [], 'radarData': [], 'maleTopCities': [], 'femaleTopCities': []})

        # 1. 基础指标对比 (平均客单价、订单数量、购买件数)
        gender_groups = df.groupby('gender')
        
        # 构建 genderStats 用于汇总卡片
        gender_stats_dict = {}
        for gender in ['男', '女']:
            subset = df[df['gender'] == gender]
            if not subset.empty:
                gender_stats_dict[gender] = {
                    'totalAmount': float(subset['amount'].sum()),
                    'orderCount': int(len(subset)),
                    'totalQuantity': int(subset['quantity'].sum())
                }
            else:
                gender_stats_dict[gender] = {'totalAmount': 0.0, 'orderCount': 0, 'totalQuantity': 0}

        metrics = []
        # 平均客单价
        avg_amount = gender_groups['amount'].mean()
        metrics.append({
            'metric': '平均客单价',
            '男': float(avg_amount.get('男', 0)),
            '女': float(avg_amount.get('女', 0))
        })
        # 订单数量
        order_count = gender_groups['user_id'].count()
        metrics.append({
            'metric': '订单数量',
            '男': int(order_count.get('男', 0)),
            '女': int(order_count.get('女', 0))
        })
        # 购买件数
        total_qty = gender_groups['quantity'].sum()
        metrics.append({
            'metric': '购买件数',
            '男': int(total_qty.get('男', 0)),
            '女': int(total_qty.get('女', 0))
        })

        # 2. 品类偏好雷达图 (占比计算)
        cat_gender = df.groupby(['category', 'gender'])['amount'].sum().unstack().fillna(0)
        radar_data = []
        for cat, row in cat_gender.iterrows():
            total_cat_amount = row.sum()
            radar_data.append({
                'category': cat,
                '男': float(row.get('男', 0) / total_cat_amount * 100) if total_cat_amount > 0 else 0,
                '女': float(row.get('女', 0) / total_cat_amount * 100) if total_cat_amount > 0 else 0
            })

        # 3. TOP 5 城市分布
        male_cities = df[df['gender'] == '男'].groupby('city')['user_id'].count().sort_values(ascending=False).head(5).reset_index()
        female_cities = df[df['gender'] == '女'].groupby('city')['user_id'].count().sort_values(ascending=False).head(5).reset_index()

        return jsonify({
            'genderStats': gender_stats_dict,
            'comparisonData': metrics,
            'radarData': radar_data,
            'maleTopCities': male_cities.rename(columns={'city': 'city', 'user_id': 'count'}).to_dict('records'),
            'femaleTopCities': female_cities.rename(columns={'city': 'city', 'user_id': 'count'}).to_dict('records')
        })
    except Exception as e:
        print(f"Error in gender_analysis: {e}")
        return jsonify({'genderStats': {}, 'comparisonData': [], 'radarData': [], 'maleTopCities': [], 'femaleTopCities': []})

@app.route('/api/stats/age-analysis', methods=['GET'])
def age_analysis():
    """
    获取细分年龄段及单岁分布分析
    """
    try:
        df = get_df()
        if df.empty: return jsonify({'ageRangeStats': [], 'ageDistribution': [], 'categoryByAge': []})

        # 年龄段定义
        age_bins = [0, 18, 25, 35, 45, 55, 65, 120]
        age_labels = ['18岁以下', '18-25岁', '26-35岁', '36-45岁', '46-55岁', '56-65岁', '66岁以上']
        df['age_range'] = pd.cut(df['age'], bins=age_bins, labels=age_labels, include_lowest=True)

        # 1. 年龄段统计
        range_stats = df.groupby('age_range', observed=False).agg(
            count=('user_id', 'count'),
            totalAmount=('amount', 'sum')
        ).reset_index()
        range_stats['avgAmount'] = np.where(range_stats['count'] > 0, range_stats['totalAmount'] / range_stats['count'], 0)
        
        # 获取每个年龄段最喜欢的品类
        top_cats = []
        for label in age_labels:
            subset = df[df['age_range'] == label]
            if not subset.empty:
                top_cat = subset.groupby('category')['amount'].sum().idxmax()
            else:
                top_cat = '无'
            top_cats.append(top_cat)
        range_stats['topCategory'] = top_cats
        
        range_stats_list = range_stats.rename(columns={'age_range': 'range'}).to_dict('records')
        for item in range_stats_list:
            item['totalAmount'] = float(item['totalAmount'])
            item['avgAmount'] = float(item['avgAmount'])

        # 2. 单岁分布
        age_dist = df.groupby('age').agg(
            count=('user_id', 'count'),
            amount=('amount', 'sum')
        ).reset_index()
        age_dist['amount'] = age_dist['amount'].astype(float)
        
        # 3. 年龄段品类偏好矩阵
        cat_by_age = df.pivot_table(index='age_range', columns='category', values='amount', aggfunc='sum', observed=False).fillna(0)
        cat_by_age_list = []
        for range_label, row in cat_by_age.iterrows():
            item = {'ageRange': range_label}
            for cat, val in row.items():
                item[cat] = float(val)
            cat_by_age_list.append(item)

        return jsonify({
            'ageRangeStats': range_stats_list,
            'ageDistribution': age_dist.to_dict('records'),
            'categoryByAge': cat_by_age_list
        })
    except Exception as e:
        print(f"Error in age_analysis: {e}")
        return jsonify({'ageRangeStats': [], 'ageDistribution': [], 'categoryByAge': []})

@app.route('/api/stats/city-consumption', methods=['GET'])
def city_consumption():
    """
    获取城市消费能力矩阵及等级分布
    """
    try:
        df = get_df()
        if df.empty: return jsonify({'cityData': [], 'tierStats': [], 'matrixData': []})

        # 1. 城市消费统计
        city_stats_df = df.groupby('city').agg(
            totalAmount=('amount', 'sum'),
            orderCount=('user_id', 'count'),
            userCount=('user_id', 'nunique')
        ).reset_index().sort_values('totalAmount', ascending=False)
        city_stats_df['avgAmount'] = city_stats_df['totalAmount'] / city_stats_df['orderCount']        
        # 获取每个城市最喜欢的品类
        top_cats = []
        for city in city_stats_df['city']:
            subset = df[df['city'] == city]
            if not subset.empty:
                top_cat = subset.groupby('category')['amount'].sum().idxmax()
            else:
                top_cat = '无'
            top_cats.append(top_cat)
        city_stats_df['topCategory'] = top_cats
        
        # 城市等级定义
        tiers = {
            '一线城市': ['北京', '上海', '广州', '深圳'],
            '新一线城市': ['杭州', '成都', '重庆', '南京', '苏州', '武汉', '西安', '天津']
        }
        def get_tier(city):
            if city in tiers['一线城市']: return '一线城市'
            if city in tiers['新一线城市']: return '新一线城市'
            return '其他城市'
        
        city_stats_df['tier'] = city_stats_df['city'].apply(get_tier)
        
        # 2. 城市分级统计
        tier_stats = city_stats_df.groupby('tier').agg(
            cityCount=('city', 'count'),
            totalAmount=('totalAmount', 'sum'),
            orderCount=('orderCount', 'sum')
        ).reset_index()
        tier_stats['avgAmount'] = tier_stats['totalAmount'] / tier_stats['orderCount']
        tier_stats['totalAmount'] = tier_stats['totalAmount'].astype(float)
        tier_stats['avgAmount'] = tier_stats['avgAmount'].astype(float)

        # 3. 消费力矩阵 (用于散点图)
        matrix_data = []
        for _, row in city_stats_df.iterrows():
            matrix_data.append({
                'city': row['city'],
                'orderCount': int(row['orderCount']),
                'avgAmount': float(row['avgAmount']),
                'totalAmount': float(row['totalAmount']),
                'tier': row['tier']
            })

        return jsonify({
            'cityData': city_stats_df.sort_values('totalAmount', ascending=False).to_dict('records'),
            'tierStats': tier_stats.to_dict('records'),
            'matrixData': matrix_data
        })
    except Exception as e:
        print(f"Error in city_consumption: {e}")
        return jsonify({'cityData': [], 'tierStats': [], 'matrixData': []})

@app.route('/api/stats/rfm-analysis', methods=['GET'])
def rfm_analysis():
    """
    获取 RFM 客户价值分群分析
    """
    try:
        df = get_df()
        if df.empty: return jsonify({'segmentStats': [], 'scatterData': [], 'rfmSegmented': []})

        # 参考日期
        ref_date = df['purchase_time'].max()
        
        # 1. 计算 RFM 基础指标
        rfm = df.groupby(['user_id', 'user_name']).agg(
            recency=('purchase_time', lambda x: (ref_date - x.max()).days),
            frequency=('user_id', 'count'),
            monetary=('amount', 'sum')
        ).reset_index()

        # 2. 评分逻辑 (1-5分，五分位数)
        try:
            rfm['R_score'] = pd.qcut(rfm['recency'].rank(method='first'), 5, labels=[5, 4, 3, 2, 1])
            rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
            rfm['M_score'] = pd.qcut(rfm['monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
        except:
            # 如果数据量太少无法使用 qcut，降级为等分
            rfm['R_score'] = 3
            rfm['F_score'] = 3
            rfm['M_score'] = 3

        rfm['R_score'] = rfm['R_score'].astype(int)
        rfm['F_score'] = rfm['F_score'].astype(int)
        rfm['M_score'] = rfm['M_score'].astype(int)
        rfm['rfm_score'] = rfm['R_score'] + rfm['F_score'] + rfm['M_score']

        # 3. 客户分群
        def segment_user(row):
            r, f, m = row['R_score'], row['F_score'], row['M_score']
            if r >= 4 and f >= 4 and m >= 4: return '重要价值客户', '#ef4444', '高价值核心客户，需重点维护'
            if r >= 4 and f <= 2 and m >= 4: return '重要发展客户', '#f59e0b', '高消费潜力新客，需引导复购'
            if r <= 2 and f >= 4 and m >= 4: return '重要保持客户', '#3b82f6', '活跃度下降的高价值客，需唤回'
            if r <= 2 and f <= 2 and m >= 4: return '重要挽留客户', '#8b5cf6', '即将流失的高价值客，需强力挽留'
            if r >= 4 and f >= 4 and m <= 2: return '一般价值客户', '#10b981', '忠诚度高但消费力有限，需交叉销售'
            if r >= 4 and f <= 2 and m <= 2: return '一般发展客户', '#94a3b8', '刚起步的普通新客，需持续培育'
            if r <= 2 and f >= 4 and m <= 2: return '一般保持客户', '#64748b', '忠诚度下降的普通客，需活动激活'
            if r <= 2 and f <= 2 and m <= 2: return '一般挽留客户', '#475569', '流失边缘的低价值客，可尝试唤醒'
            return '潜力客户', '#06b6d4', '各项表现均衡，有待进一步挖掘'

        rfm[['segment', 'segmentColor', 'desc']] = rfm.apply(lambda x: pd.Series(segment_user(x)), axis=1)

        # 4. 统计分群数据
        seg_stats = rfm.groupby(['segment', 'segmentColor', 'desc']).agg(
            count=('user_id', 'count'),
            totalAmount=('monetary', 'sum')
        ).reset_index().sort_values('totalAmount', ascending=False)
        seg_stats['totalAmount'] = seg_stats['totalAmount'].astype(float)
        
        # 重命名列以匹配前端
        seg_stats = seg_stats.rename(columns={'segmentColor': 'color'})

        # 5. 散点图数据
        scatter_data = []
        for _, row in rfm.iterrows():
            scatter_data.append({
                'x': int(row['frequency']),
                'y': float(row['monetary']),
                'z': int(row['recency']),
                'segment': row['segment'],
                'segmentColor': row['segmentColor'],
                'name': row['user_name']
            })

        # 格式化表格数据以匹配前端字段名
        rfm_table = rfm.rename(columns={
            'user_id': 'userId',
            'user_name': 'userName',
            'R_score': 'R',
            'F_score': 'F',
            'M_score': 'M'
        }).sort_values('rfm_score', ascending=False).head(100)

        return jsonify({
            'segmentStats': seg_stats.to_dict('records'),
            'scatterData': scatter_data,
            'rfmSegmented': rfm_table.to_dict('records')
        })
    except Exception as e:
        print(f"Error in rfm_analysis: {e}")
        return jsonify({'segmentStats': [], 'scatterData': [], 'rfmSegmented': []})

# =================================================================
# 2. 推荐算法接口组 (Smart Recommendation Algorithms)
# =================================================================

@app.route('/api/recommendation/cf/<user_id>', methods=['GET'])
def collaborative_filtering(user_id):
    """
    【个性化推荐】基于用户的协同过滤算法 (User-Based CF)
    ---
    tags:
      - 智能推荐系统
    description: 找到品类购买偏好最相似的 10 位用户，并向当前用户推荐他未买过但相似用户高频购买的商品。
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: 目标用户 ID
    """
    df = get_df()
    if df.empty: return jsonify([])

    # 统一类型为字符串，防止 ID 匹配失败
    df['user_id'] = df['user_id'].astype(str)
    user_id = str(user_id)

    # 1. 建立用户-品类偏好矩阵（行：用户，列：品类，值：累计金额）
    user_item_matrix = df.pivot_table(index='user_id', columns='category', values='amount', aggfunc='sum').fillna(0)
    
    if user_id not in user_item_matrix.index:
        return jsonify([])

    # 2. 计算余弦相似度 (Cosine Similarity)
    user_vector = user_item_matrix.loc[user_id].values.reshape(1, -1)
    similarities = {}
    for other_user in user_item_matrix.index:
        if other_user == user_id: continue
        other_vector = user_item_matrix.loc[other_user].values.reshape(1, -1)
        # 余弦公式：(A dot B) / (||A|| * ||B||)
        sim = np.dot(user_vector, other_vector.T) / (np.linalg.norm(user_vector) * np.linalg.norm(other_vector) + 1e-9)
        similarities[other_user] = sim[0][0]

    # 3. 提取前 10 位最相似的“邻居”
    top_similar_users = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # 4. 推荐过滤：排除已购商品，聚合相似用户喜欢的商品
    user_bought = set(df[df['user_id'] == user_id]['product_name'])
    recommendations = {}
    
    for sim_user, score in top_similar_users:
        sim_user_orders = df[df['user_id'] == sim_user]
        for _, row in sim_user_orders.iterrows():
            if row['product_name'] not in user_bought:
                prod_name = row['product_name']
                if prod_name not in recommendations:
                    recommendations[prod_name] = {
                        'productName': prod_name,
                        'category': row['category'],
                        'avgPrice': float(row['price']),
                        'buyCount': 0,
                        'score': 0
                    }
                # 加权推荐分：相似度分值 * 购买次数
                recommendations[prod_name]['score'] += score
                recommendations[prod_name]['buyCount'] += 1

    # 5. 返回前 6 名最值得推荐的商品
    result = sorted(recommendations.values(), key=lambda x: x['score'], reverse=True)[:6]
    for r in result:
        # 补全商品全站统计信息
        prod_data = df[df['product_name'] == r['productName']]
        r['buyCount'] = int(prod_data['user_id'].nunique())
        r['avgPrice'] = float(prod_data['price'].mean())

    return jsonify(result)

@app.route('/api/recommendation/association', methods=['GET'])
def association_rules():
    """
    【组合推荐】基于月度跨品类购买行为的关联规则挖掘
    ---
    tags:
      - 智能推荐系统
    description: 分析同一用户在一个月内共同购买的品类，发现“买过 A 的人通常也会买 B”的月度规律。
    """
    try:
        df = get_df()
        if df.empty or len(df) < 5: return jsonify([])

        df['year_month'] = df['purchase_time'].dt.to_period('M')

        # 1. 构建月度购物篮集合
        user_month_cat_groups = df.groupby(['user_id', 'year_month'])['category'].apply(set).tolist()
        
        pairs = {}
        for items in user_month_cat_groups:
            items_list = sorted(list(items))
            if len(items_list) < 2: continue # 只有购买了两种及以上品类才构成关联
            for i in range(len(items_list)):
                for j in range(i + 1, len(items_list)):
                    pair = tuple(sorted([items_list[i], items_list[j]]))
                    pairs[pair] = pairs.get(pair, 0) + 1
        
        # 2. 如果品类级关联较少，则降级进行商品名级关联分析
        if not pairs:
            user_month_prod_groups = df.groupby(['user_id', 'year_month'])['product_name'].apply(set).tolist()
            for items in user_month_prod_groups:
                items_list = sorted(list(items))
                if len(items_list) < 2: continue
                for i in range(len(items_list)):
                    for j in range(i + 1, len(items_list)):
                        pair = tuple(sorted([items_list[i], items_list[j]]))
                        pairs[pair] = pairs.get(pair, 0) + 1

        # 3. 排序并计算指标
        sorted_pairs = sorted(pairs.items(), key=lambda x: x[1], reverse=True)[:4]
        
        result = []
        total_monthly_baskets = len(user_month_cat_groups)
        for (item1, item2), count in sorted_pairs:
            support = round((count / total_monthly_baskets) * 100, 1)
            result.append({
                'items': [item1, item2],
                'support': count,
                'description': f"基于月度消费分析：购买过 {item1} 的顾客，通常在同月内也会选购 {item2}",
                'potential': f"月度关联度: {support}% (建议进行跨品类套餐促销)"
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify([])

# =================================================================
# 3. 数据中心管理接口组 (Admin & CRUD Operations)
# =================================================================

@app.route('/api/users', methods=['GET'])
def get_all_users():
    """
    获取系统中所有去重后的活跃用户列表
    """
    df = get_df()
    if df.empty: return jsonify([])
    users = df[['user_id', 'user_name']].drop_duplicates().rename(columns={'user_id': 'id', 'user_name': 'name'})
    return jsonify(users.to_dict('records'))

@app.route('/api/users/search', methods=['GET'])
def search_user():
    """
    根据 ID 或姓名关键词精准搜索用户
    """
    kw = request.args.get('keyword', '')
    search_type = request.args.get('type', 'name')
    if not kw: return jsonify(None)
    
    df = get_df()
    if df.empty: return jsonify(None)
    
    if search_type == 'id':
        match = df[df['user_id'].astype(str) == str(kw)]
    else:
        match = df[df['user_name'].str.contains(kw, na=False)]
        
    if match.empty: return jsonify(None)
    
    user = match.iloc[0]
    return jsonify({'id': str(user['user_id']), 'name': user['user_name']})

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """
    【列表查询】获取分页及搜索后的原始订单数据
    ---
    tags:
      - 数据中心接口
    """
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search = request.args.get('search', '')
        column = request.args.get('column', 'all')
        
        query = "SELECT * FROM orders"
        params = []
        
        # 搜索过滤逻辑
        if search:
            if column == 'all':
                # 全字段全局模糊搜索
                columns = ['user_id', 'user_name', 'product_id', 'product_name', 'category', 'price', 'purchase_time', 'quantity', 'amount', 'city', 'gender', 'age']
                query += " WHERE (" + " OR ".join([f"CAST({col} AS CHAR) LIKE %s" for col in columns]) + ")"
                params = [f"%{search}%"] * len(columns)
            else:
                # 特定列搜索
                query += f" WHERE {column} LIKE %s"
                params = [f"%{search}%"]
                
        sql_params = tuple(params) if params else None
        
        # 统计搜索后的总数用于前端显示分页
        count_query = f"SELECT COUNT(*) as total FROM ({query}) as t"
        total_df = pd.read_sql(count_query, con=engine, params=sql_params)
        total = total_df.iloc[0]['total'] if not total_df.empty else 0
        
        # 添加排序（最新日期在前）和分页限制
        paginated_query = query + " ORDER BY purchase_time DESC LIMIT %s OFFSET %s"
        p_params = params + [limit, (page - 1) * limit]
        
        df = pd.read_sql(paginated_query, con=engine, params=tuple(p_params))
        if not df.empty:
            df['purchase_time'] = pd.to_datetime(df['purchase_time']).dt.strftime('%Y-%m-%d %H:%M:%S')
            df['amount'] = df['amount'].astype(float)
            df['price'] = df['price'].astype(float)
        
        return jsonify({
            'data': df.to_dict('records'),
            'total': int(total),
            'page': page,
            'limit': limit
        })
    except Exception as e:
        return jsonify({'error': str(e), 'data': [], 'total': 0}), 500

@app.route('/api/orders', methods=['POST'])
def add_order():
    """
    【新增数据】手动添加单条订单
    ---
    tags:
      - 数据中心接口
    """
    data = request.json
    try:
        # 数据类型清洗
        def safe_float(val, default=0.0):
            try: return float(val) if val and str(val).strip() else default
            except: return default
            
        def safe_int(val, default=0):
            try: return int(val) if val and str(val).strip() else default
            except: return default

        data['price'] = safe_float(data.get('price'))
        data['quantity'] = safe_int(data.get('quantity'))
        data['amount'] = safe_float(data.get('amount'))
        data['age'] = safe_int(data.get('age'))
        
        # 如果未传时间，默认使用当前时间
        if not data.get('purchase_time'):
            data['purchase_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        df = pd.DataFrame([data])
        df['purchase_time'] = pd.to_datetime(df['purchase_time'])
        # 追加写入 MySQL
        df.to_sql('orders', con=engine, if_exists='append', index=False)
        return jsonify({'message': '成功'}), 201
    except Exception as e:
        return jsonify({'error': f"添加失败: {str(e)}"}), 400

@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """
    【修改数据】更新单条订单记录
    """
    data = request.json
    try:
        # 构建更新 SQL，使用 SQLAlchemy 的命名参数绑定 :key
        fields = []
        bound_params = {}
        for i, (key, value) in enumerate(data.items()):
            if key == 'id' or key not in ['user_id', 'user_name', 'product_id', 'product_name', 'category', 'price', 'purchase_time', 'quantity', 'amount', 'city', 'gender', 'age']: 
                continue 
            param_name = f"v{i}"
            fields.append(f"{key} = :{param_name}")
            bound_params[param_name] = value
        
        if not fields:
            return jsonify({'message': '无有效更新内容'}), 400
            
        sql = f"UPDATE orders SET {', '.join(fields)} WHERE id = :order_id"
        bound_params['order_id'] = order_id
        
        with engine.begin() as conn:
            conn.execute(text(sql), bound_params)
            
        return jsonify({'message': '更新成功'})
    except Exception as e:
        print(f"Update error: {e}")
        return jsonify({'error': f"更新失败: {str(e)}"}), 500

@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """
    【删除数据】删除单条订单记录
    """
    try:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM orders WHERE id = :id"), {"id": order_id})
        return jsonify({'message': '删除成功'})
    except Exception as e:
        print(f"Delete error: {e}")
        return jsonify({'error': f"删除失败: {str(e)}"}), 500

@app.route('/api/orders/batch', methods=['DELETE'])
def batch_delete_orders():
    """
    【批量删除】根据 ID 列表删除多条记录
    """
    data = request.json
    ids = data.get('ids', [])
    if not ids:
        return jsonify({'message': '未选择任何记录'}), 400
        
    try:
        # 构建命名参数列表 :id0, :id1, ...
        param_names = [f"id{i}" for i in range(len(ids))]
        sql = f"DELETE FROM orders WHERE id IN ({', '.join([':' + n for n in param_names])})"
        bound_params = {n: id_val for n, id_val in zip(param_names, ids)}
        
        with engine.begin() as conn:
            conn.execute(text(sql), bound_params)
            
        return jsonify({'message': f'成功删除 {len(ids)} 条记录'})
    except Exception as e:
        print(f"Batch delete error: {e}")
        return jsonify({'error': f"批量删除失败: {str(e)}"}), 500

@app.route('/api/upload', methods=['POST'])
def upload_csv():
    """
    【批量导入】上传 CSV 并重载数据库
    ---
    tags:
      - 数据中心接口
    """
    if 'file' not in request.files:
        return jsonify({'error': '未找到文件部分'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400
    
    if file and file.filename.endswith('.csv'):
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        csv_path = os.path.join(data_dir, '天猫.csv') 
        
        try:
            file.save(csv_path)
            # 动态刷新同步模块并执行重载逻辑
            import db_init
            importlib.reload(db_init)
            db_init.ingest_csv_to_mysql()
            return jsonify({'message': '上传成功并同步数据库'})
        except Exception as e:
            return jsonify({'error': f"同步失败: {str(e)}"}), 500
    
    return jsonify({'error': '不支持的文件类型'}), 400

@app.route('/api/orders/clear', methods=['DELETE'])
def clear_all_orders():
    """
    【一键清空】清除数据库所有历史数据
    ---
    tags:
      - 数据中心接口
    """
    try:
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE orders"))
        return jsonify({'message': '数据库已清空'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =================================================================
# 主程序启动
# =================================================================
if __name__ == '__main__':
    # 开发环境启动模式，监听 5000 端口
    app.run(debug=True, port=5000)