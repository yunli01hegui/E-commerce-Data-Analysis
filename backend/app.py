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
import json

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
    description: 深度统计全站品类结构、价格带分布、爆款排行及多渠道表现.
    """
    try:
        df = get_df()
        if df.empty: 
            return jsonify({
                'categoryData': [], 'productRanking': [], 
                'priceRangeData': [], 'categoryEfficiency': [], 'stats': {}
            })
        
        # 1. 品类统计
        category_data = df.groupby('category').agg(
            value=('amount', 'sum'),
            count=('user_id', 'count')
        ).reset_index().rename(columns={'category': 'name'}).sort_values('value', ascending=False)
        category_data_list = category_data.to_dict('records')

        # 2. 爆款排行
        product_ranking = df.groupby(['product_name', 'category']).agg(
            sales=('quantity', 'sum'),
            revenue=('amount', 'sum'),
            orders=('user_id', 'count')
        ).reset_index().sort_values('revenue', ascending=False)
        
        product_ranking_list = product_ranking.head(50).to_dict('records')
        for p in product_ranking_list:
            p['key'] = f"{p['product_name']}-{p['category']}"
            p['name'] = p.pop('product_name')

        # 3. 动态价格区间分布算法
        max_p = df['price'].max()
        if max_p <= 500:
            bins = [0, 50, 100, 200, 300, float('inf')]
            labels = ['0-50', '50-100', '100-200', '200-300', '300+']
        elif max_p <= 2000:
            bins = [0, 100, 300, 500, 1000, float('inf')]
            labels = ['0-100', '100-300', '300-500', '500-1000', '1000+']
        else:
            step = max_p / 5
            bins = [0, step, step*2, step*3, step*4, float('inf')]
            labels = [f"0-{int(step)}", f"{int(step)}-{int(step*2)}", f"{int(step*2)}-{int(step*3)}", f"{int(step*3)}-{int(step*4)}", f"{int(step*4)}+"]
        
        df['price_range'] = pd.cut(df['price'], bins=bins, labels=labels, right=False)
        price_range_df = df.groupby('price_range', observed=False).size().reset_index(name='count')
        
        # 【修复点】：在 DataFrame 还是 'price_range' 列名时进行计算
        if not price_range_df.empty:
            main_range_val = price_range_df.loc[price_range_df['count'].idxmax(), 'price_range']
            main_price_range = f"¥{main_range_val}"
        else:
            main_price_range = "暂无数据"

        # 转换为列表，并将列名重命名为 range 适配前端
        price_range_data_list = price_range_df.rename(columns={'price_range': 'range'}).to_dict('records')

        # 4. 品类效能分析
        category_eff = df.groupby('category').agg(
            revenue=('amount', 'sum'),
            volume=('quantity', 'sum'),
            order_count=('user_id', 'count'),
            unique_buyers=('user_id', 'nunique')
        ).reset_index()
        
        total_rev_sum = category_eff['revenue'].sum()
        total_vol_sum = category_eff['volume'].sum()
        
        category_eff['rev_ratio'] = (category_eff['revenue'] / total_rev_sum * 100).round(1)
        category_eff['vol_ratio'] = (category_eff['volume'] / total_vol_sum * 100).round(1)
        category_eff['avg_unit_price'] = (category_eff['revenue'] / category_eff['volume']).round(2)
        category_eff['upt'] = (category_eff['volume'] / category_eff['order_count']).round(2)
        
        category_eff_list = category_eff.sort_values('revenue', ascending=False).to_dict('records')

        # 5. 核心指标统计
        total_products = df['product_id'].nunique()
        total_revenue = float(df['amount'].sum())
        total_quantity = int(df['quantity'].sum())
        total_orders = df['user_id'].count()
        aov = total_revenue / total_orders if total_orders > 0 else 0
        
        days_range = (df['purchase_time'].max() - df['purchase_time'].min()).days + 1
        velocity = total_quantity / days_range if days_range > 0 else 0

        category_eff_sorted = category_eff.sort_values('revenue', ascending=False)
        top3_rev = category_eff_sorted.head(3)['revenue'].sum()
        concentration = (top3_rev / total_rev_sum * 100).round(1) if total_rev_sum > 0 else 0
        
        return jsonify({
            'categoryData': category_data_list,
            'productRanking': product_ranking_list,
            'priceRangeData': price_range_data_list,
            'categoryEfficiency': category_eff_list,
            'stats': {
                'sales_amount': f"¥{total_revenue:,.0f}",
                'avg_order_value': f"¥{aov:.2f}",
                'sku_count': f"{total_products:,}",
                'daily_velocity': f"{velocity:.1f} 件/日",
                'top_concentration': f"{concentration}%",
                'order_total': f"{total_orders:,}",
                'main_price_range': main_price_range
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in product_analysis: {e}")
        return jsonify({'error': str(e)})
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
    description: 计算月度趋势、每日趋势、周权重分布、24小时热力及关键 KPI。
    responses:
      200:
        description: 成功返回趋势图数据及 KPI
    """
    try:
        df = get_df()
        if df.empty: return jsonify({
            'monthlyData': [], 'dailyData': [], 
            'dayOfWeekData': [], 'hourlyData': [], 
            'kpi': {}
        })
        
        # 1. 月度趋势
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

        # 2. 每日趋势
        daily = df.groupby(df['purchase_time'].dt.date).agg(
            sales=('amount', 'sum'),
            orders=('user_id', 'count')
        ).sort_index().reset_index()
        
        daily['date'] = daily['purchase_time'].apply(lambda x: x.strftime('%Y-%m-%d'))
        daily_data = daily[['date', 'sales', 'orders']].to_dict('records')

        # 3. 周权重分布 (Day of Week)
        # 0=Monday, 6=Sunday
        df['day_of_week'] = df['purchase_time'].dt.dayofweek
        day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        dow_stats = df.groupby('day_of_week').agg(
            sales=('amount', 'sum')
        ).reindex(range(7), fill_value=0).reset_index()
        
        day_of_week_data = []
        for _, row in dow_stats.iterrows():
            day_of_week_data.append({
                'name': day_names[int(row['day_of_week'])],
                'sales': float(row['sales'])
            })

        # 4. 24小时成交热点 (Hourly)
        df['hour'] = df['purchase_time'].dt.hour
        hourly_stats = df.groupby('hour').agg(
            orders=('user_id', 'count')
        ).reindex(range(24), fill_value=0).reset_index()
        
        hourly_data = []
        for _, row in hourly_stats.iterrows():
            hourly_data.append({
                'hour': int(row['hour']),
                'orders': int(row['orders'])
            })

        # 5. 计算全局 KPI 指标
        total_sales_val = float(df['amount'].sum())
        total_orders_val = int(len(df))
        avg_price_val = float(total_sales_val / total_orders_val) if total_orders_val > 0 else 0.0
        
        # 峰值与均值
        peak_day_sales = float(daily['sales'].max()) if not daily.empty else 0.0
        days_count = (df['purchase_time'].max() - df['purchase_time'].min()).days + 1
        avg_daily_orders = float(total_orders_val / days_count) if days_count > 0 else 0.0

        # 环比增长率
        if not monthly_stats.empty:
            sorted_stats = monthly_stats.sort_values('month_key')
            latest_row = sorted_stats.iloc[-1]
            curr_sales = float(latest_row['sales'])
            
            latest_date = pd.to_datetime(latest_row['month_key'] + '-01')
            prev_month_date = latest_date - pd.Timedelta(days=1)
            last_month_key = prev_month_date.strftime('%Y-%m')
            
            prev_sales = float(monthly_stats[monthly_stats['month_key'] == last_month_key]['sales'].sum())
            growth_rate = float(((curr_sales - prev_sales) / prev_sales * 100)) if prev_sales > 0 else 0.0
        else:
            growth_rate = 0.0

        return jsonify({
            'monthlyData': monthly_data,
            'dailyData': daily_data,
            'dayOfWeekData': day_of_week_data,
            'hourlyData': hourly_data,
            'kpi': {
                'totalSales': f"¥{total_sales_val:,.0f}",
                'totalOrders': f"{total_orders_val:,}",
                'avgPrice': f"¥{avg_price_val:.2f}",
                'peakDaySales': f"¥{peak_day_sales:,.0f}",
                'avgDailyOrders': f"{avg_daily_orders:.1f} 单",
                'growthRate': round(growth_rate, 1)
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in sales_trend: {e}")
        return jsonify({
            'monthlyData': [], 'dailyData': [], 
            'dayOfWeekData': [], 'hourlyData': [], 
            'kpi': {}
        })

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

        # 4. 自动生成业务洞察 (Insights)
        insights = []
        if not range_stats.empty:
            # 核心消费群体：总消费最高的
            core_row = range_stats.loc[range_stats['totalAmount'].idxmax()]
            insights.append({
                'title': '核心消费群体',
                'content': f"{core_row['age_range']}用户总消费最高，是平台的主力消费群体，最偏好{core_row['topCategory']}。",
                'type': 'core'
            })
            
            # 增长潜力：18-25岁或用户数最多的
            potential_row = range_stats.loc[range_stats['count'].idxmax()]
            insights.append({
                'title': '增长潜力',
                'content': f"{potential_row['age_range']}群体用户基数大，购买频次活跃，是未来重点培育对象。",
                'type': 'potential'
            })
            
            # 高价值用户：客单价最高的
            high_value_row = range_stats.loc[range_stats['avgAmount'].idxmax()]
            insights.append({
                'title': '高价值用户',
                'content': f"{high_value_row['age_range']}用户平均客单价(¥{high_value_row['avgAmount']:.0f})最高，购买力强，适合高端推荐。",
                'type': 'high_value'
            })

        return jsonify({
            'ageRangeStats': range_stats_list,
            'ageDistribution': age_dist.to_dict('records'),
            'categoryByAge': cat_by_age_list,
            'insights': insights
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

        # 参考日期：使用当前系统时间，确保“距今天数”反映真实情况
        ref_date = datetime.now()
        
        # 1. 计算 RFM 基础指标
        # Recency (R): 客户最近一次购买距今的天数。天数越少，客户越活跃。
        # Frequency (F): 客户在统计期内的购买总次数。次数越多，忠诚度越高。
        # Monetary (M): 客户在统计期内的总消费金额。金额越大，贡献度越高。
        rfm = df.groupby(['user_id', 'user_name']).agg(
            recency=('purchase_time', lambda x: (ref_date - x.max()).days),
            frequency=('user_id', 'count'),
            monetary=('amount', 'sum')
        ).reset_index()

        # 2. 评分逻辑 (1-5分，五分位数)
        # pd.qcut (Quantile-based discretization): 将数据按照分位数划分为5个区间。
        # R_score: 距今天数越短分越高 (labels=[5, 4, 3, 2, 1])。
        # F_score & M_score: 频率和金额越高分越高 (labels=[1, 2, 3, 4, 5])。
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
        # rfm_score: 综合评分，即 R、F、M 三项评分之和，用于衡量客户的综合价值。
        rfm['rfm_score'] = rfm['R_score'] + rfm['F_score'] + rfm['M_score']

        # 3. 客户分群 (Segmentation Rules)
        # 根据 R/F/M 各维度的得分高低，将客户划分为 8 个不同的精细化运营群体。
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
            totalAmount=('monetary', 'sum'),
            avgRFM=('rfm_score', 'mean')
        ).reset_index().sort_values('totalAmount', ascending=False)
        seg_stats['totalAmount'] = seg_stats['totalAmount'].astype(float)
        seg_stats['avgRFM'] = seg_stats['avgRFM'].round(1)        
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

        # 格式化表格数据以匹配前端字段名，并按综合价值评分 (rfm_score) 降序排列。
        rfm_table = rfm.rename(columns={
            'user_id': 'userId',
            'user_name': 'userName',
            'R_score': 'R',
            'F_score': 'F',
            'M_score': 'M'
        }).sort_values('rfm_score', ascending=False)

        return jsonify({            'segmentStats': seg_stats.to_dict('records'),
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

    # 1. 建立用户-品类偏好矩阵 (User-Item Preference Matrix)
    # 行表示用户 (User)，列表示品类 (Category)，值表示该用户在该品类上的累计消费金额。
    # 这种表示法可以将用户的消费行为转化为高维向量，从而进行相似度比较。
    user_item_matrix = df.pivot_table(index='user_id', columns='category', values='amount', aggfunc='sum').fillna(0)
    
    if user_id not in user_item_matrix.index:
        return jsonify([])

    # 2. 计算余弦相似度 (Cosine Similarity)
    # 逻辑：通过计算两个向量夹角的余弦值来衡量用户间的品类偏好相似度。
    # 余弦值越接近 1，表示两个用户的消费结构越相似。
    user_vector = user_item_matrix.loc[user_id].values.reshape(1, -1)
    similarities = {}
    for other_user in user_item_matrix.index:
        if other_user == user_id: continue
        other_vector = user_item_matrix.loc[other_user].values.reshape(1, -1)
        # 余弦公式：(A · B) / (||A|| * ||B||)
        # 1e-9 为平滑项，防止分母为零。
        sim = np.dot(user_vector, other_vector.T) / (np.linalg.norm(user_vector) * np.linalg.norm(other_vector) + 1e-9)
        similarities[other_user] = sim[0][0]

    # 3. 提取前 10 位最相似的“邻居” (Top-N Nearest Neighbors)
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
                # 加权推荐分 (Weighted Recommendation Score): 
                # 推荐分 = Σ (相似度分值 * 该邻居对该商品的购买权重)
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

        # 1. 构建月度购物篮集合 (Monthly Basket Analysis)
        # 逻辑：将同一用户在同一自然月内的所有购买行为视为一个“购物篮”。
        # 这种方法可以挖掘出用户在特定时间窗口内的跨品类购买规律。
        user_month_cat_groups = df.groupby(['user_id', 'year_month'])['category'].apply(set).tolist()
        
        pairs = {}
        for items in user_month_cat_groups:
            items_list = sorted(list(items))
            if len(items_list) < 2: continue # 只有在一个月中购买了两种及以上品类才构成关联规则的基础
            for i in range(len(items_list)):
                for j in range(i + 1, len(items_list)):
                    # 生成品类两两配对，统计其共同出现的频次
                    pair = tuple(sorted([items_list[i], items_list[j]]))
                    pairs[pair] = pairs.get(pair, 0) + 1
        
        # 2. 如果品类级关联较少，则降级进行商品名级关联分析 (Fallback to Product-level)
        if not pairs:
            user_month_prod_groups = df.groupby(['user_id', 'year_month'])['product_name'].apply(set).tolist()
            for items in user_month_prod_groups:
                items_list = sorted(list(items))
                if len(items_list) < 2: continue
                for i in range(len(items_list)):
                    for j in range(i + 1, len(items_list)):
                        pair = tuple(sorted([items_list[i], items_list[j]]))
                        pairs[pair] = pairs.get(pair, 0) + 1

        # 3. 排序并计算指标 (Support Calculation)
        sorted_pairs = sorted(pairs.items(), key=lambda x: x[1], reverse=True)[:4]
        
        result = []
        total_monthly_baskets = len(user_month_cat_groups)
        for (item1, item2), count in sorted_pairs:
            # 支持度 (Support): 指该关联对 (A, B) 在所有购物篮中出现的概率。
            # 公式：(包含 A 和 B 的购物篮数量) / (总购物篮数量)
            # 支持度越高，说明该组合的关联普遍性越强。
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

# -----------------------------------------------------------------
# AI 逻辑配置 (DeepSeek)
# -----------------------------------------------------------------
DEEPSEEK_API_KEY = 'deepseek api key'
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'

def call_deepseek_ai(prompt):
    """调用 DeepSeek API 的通用函数"""
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == 'YOUR_DEEPSEEK_API_KEY_HERE':
        print("Error: DEEPSEEK_API_KEY is not configured.")
        return None
        
    import requests
    import json
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位专业的电商数据分析师。请生成完整、结构严密的 Markdown 报告。确保报告内容详实且必须有完整的结尾。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 5000  # 增加 token 限制，防止长报告截断
    }
    
    try:
        print(f"Sending request to DeepSeek API...")
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=60)
        print(f"DeepSeek API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"DeepSeek API Error Response: {response.text}")
            return None
    except Exception as e:
        print(f"DeepSeek API Network Error: {e}")
        return None

# -----------------------------------------------------------------
# 数据版本与 AI 缓存管理
# -----------------------------------------------------------------
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'ai_cache.json')

def get_db_version():
    """获取当前数据库的实时全内容校验和（检测全表任何字段的细微修改）"""
    try:
        with engine.connect() as conn:
            # CHECKSUM TABLE 是 MySQL 的原生命令，它会对表中所有行和列的数据计算一个 CRC 校验值
            # 哪怕只是修改了用户姓名的一个字或年龄的一个数字，该值都会立即改变
            res = conn.execute(text("CHECKSUM TABLE orders")).fetchone()
            # res[0] 是表名，res[1] 是 Checksum 数值
            return str(res[1])
    except Exception as e:
        # 如果由于权限或环境问题导致 Checksum 失败，使用多维度组合指纹作为兜底
        print(f"Checksum detection failed: {e}, using fallback fingerprint.")
        try:
            with engine.connect() as conn:
                # 统计记录数、最大ID、金额总和、年龄总和（涵盖了数值变动）
                res = conn.execute(text("SELECT COUNT(*), MAX(id), SUM(amount), SUM(age) FROM orders")).fetchone()
                return f"{res[0]}_{res[1]}_{res[2]}_{res[3]}"
        except:
            return str(datetime.now().timestamp())

def get_cached_report(report_type, current_version):
    """从本地 JSON 文件读取缓存的报告"""
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
            entry = cache.get(report_type)
            if entry and entry.get('version') == current_version:
                return entry.get('content')
    except:
        pass
    return None

def save_report_to_cache(report_type, content, version):
    """将生成的报告存入本地 JSON 缓存"""
    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        except:
            pass
    
    cache[report_type] = {
        'content': content,
        'version': version,
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

@app.route('/api/ai/analysis-report/<report_type>', methods=['GET'])
def get_ai_custom_report(report_type):
    """
    【AI 全站全量数据智能审计接口】
    基于全量订单数据提取深度商业指纹，驱动 DeepSeek 生成专业报告。
    """
    try:
        force_update = request.args.get('force', 'false').lower() == 'true'
        current_version = get_db_version()
        
        # 1. 缓存层校验
        if not force_update:
            cached_entry = get_cached_report(report_type, current_version)
            if cached_entry:
                return jsonify({
                    'report': cached_entry, 
                    'cached': True, 
                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

        df = get_df()
        if df.empty: return jsonify({'report': '数据库当前无有效订单，请先导入数据后再试。'})

        # ---------------------------------------------------------
        # 【全量数据特征增强预处理】
        # ---------------------------------------------------------
        # A. 业绩与效率指标
        total_sales = float(df['amount'].sum())
        total_orders = int(len(df))
        total_users = int(df['user_id'].nunique())
        total_qty = int(df['quantity'].sum())
        avg_price = total_sales / total_orders if total_orders > 0 else 0
        ipt = total_qty / total_orders if total_orders > 0 else 0  # 笔单件 (Items Per Ticket)
        
        # B. 客户忠诚度 (复购分析)
        user_order_counts = df.groupby('user_id').size()
        repeat_user_count = int((user_order_counts > 1).sum())
        repeat_rate = (repeat_user_count / total_users * 100) if total_users > 0 else 0
        
        # C. 品类与定价指纹
        top_cats = df.groupby('category')['amount'].sum().nlargest(5).to_dict()
        top_products = df.groupby('product_name')['amount'].sum().nlargest(10).index.tolist()
        price_median = float(df['price'].median())
        
        # D. 人口学全景
        gender_dist = df['gender'].value_counts(normalize=True).to_dict()
        age_bins = [0, 18, 25, 35, 45, 55, 65, 120]
        age_labels = ['18岁以下', '18-25', '26-35', '36-45', '46-55', '56-65', '66+']
        df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels, include_lowest=True)
        age_dist = df['age_group'].value_counts().to_dict()
        top_cities = df.groupby('city')['amount'].sum().nlargest(5).to_dict()
        
        # E. 时域消费节律
        peak_hours = df['purchase_time'].dt.hour.value_counts().head(3).index.tolist()
        top_day = df['purchase_time'].dt.day_name().value_counts().idxmax()

        # ---------------------------------------------------------
        # 【全量数据驱动的定制化提示词】
        # ---------------------------------------------------------
        if report_type == 'analysis':
            prompt = f"""
            你是一位首席商业增长官。请基于全站 {total_orders} 笔全量数据生成《电商数据深度分析报告》。
            [全量数据指纹] GMV ¥{total_sales:,.2f}，活跃用户 {total_users}，复购率 {repeat_rate:.1f}%，笔单件 {ipt:.2f}，中位数价格 ¥{price_median}，前五城市 {top_cities}，核心品类 {top_cats}。
            
            [报告结构需求]
            # 电商数据深度分析报告
            ## 一、总体业绩评估
            结合 GMV、复购率({repeat_rate:.1f}%) 和笔单件({ipt:.2f}) 分析平台目前的生命周期阶段与增长质量。
            ## 二、用户画像多维解析
            利用地域分布和年龄段特征，深度刻画三类典型高价值用户的“消费标签”。
            ## 三、品类趋势与毛利拉动
            分析核心品类 {list(top_cats.keys())[0]} 的统治地位及对长尾商品的带动效应。针对中位数价格提出定价优化策略。
            ## 四、全链路增长建议
            给出关于精准获客、存量促活、以及品类扩张的3条实战级战略建议。
            """
        elif report_type == 'behavior':
            prompt = f"""
            你是一位资深行为心理学家。请基于全量用户行为轨迹生成《用户消费行为与决策模型报告》。
            [行为特征矩阵] 复购率 {repeat_rate:.1f}%，最强成交日 {top_day}，高峰时段 {peak_hours}点，核心年龄段 {max(age_dist, key=age_dist.get)}，性别分布 {gender_dist}。
            
            [报告结构需求]
            # 用户行为深度分析报告
            ## 一、价值矩阵与忠诚度分析
            深度剖析复购率背后用户的品牌忠诚度。为何用户在 {list(top_cats.keys())[0]} 品类产生高频心智？
            ## 二、消费决策路径与心理
            分析 {top_day} 和 {peak_hours}点 背后隐藏的用户场景（如：职场补偿、深夜独处等心理动机）。
            ## 三、品类偏好与欲望图谱
            结合性别与年龄，分析不同群体在 ¥{price_median}(中位数) 价格锚点下的决策门槛。
            ## 四、私域留存方案
            基于现有周消费节律，设计一套能够提升 LTV 的“心理助推”增长方案。
            """
        else: # recommendation
            prompt = f"""
            你是一位首席 AI 算法科学家。请基于全站全量数据架构撰写《AI 智能推荐系统迭代方案》。
            [算法输入全景] 样本规模 {total_orders} 笔流水，特征包含复购周期、笔单件 {ipt:.2f}、地域权重 {list(top_cities.keys())} 及 7 个年龄段分布。
            
            [报告结构需求]
            # 智能推荐系统优化方案
            ## 一、现有推荐算法效能评估
            分析当前高集中度品类 ({list(top_cats.keys())[0]}) 带来的“推荐茧房”风险。
            ## 二、特征工程与模型增强
            说明如何将复购特征和地域 Embedding 引入 CTR 预估模型，以提升点击率。
            ## 三、长尾分发与多样性策略
            针对非爆款商品设计一套基于强化学习的流量探测机制。
            ## 四、算法演进路线图
            给出从现有模型到大模型(LLM)驱动的多任务学习系统的三步走升级方案。
            """

        # 3. AI 调用与缓存存储
        full_prompt = f"### 严禁出现日期字样，严格按照 Markdown 格式输出 ###\n{prompt}"
        report_content = call_deepseek_ai(full_prompt)
        
        if not report_content:
            return jsonify({'error': 'AI 报告生成失败', 'message': 'API 调用受限或 Key 配置错误'}), 403
            
        save_report_to_cache(report_type, report_content, current_version)
        return jsonify({
            'report': report_content, 
            'cached': False,
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/analysis-report', methods=['GET'])
def get_ai_analysis_report_legacy():
    # 兼容旧版调用，默认返回全站分析
    return get_ai_custom_report('analysis')

if __name__ == '__main__':
    # 开发环境启动模式，监听 5000 端口
    # 使用 host='0.0.0.0' 以确保在各种网络环境下都能被前端正常访问
    app.run(debug=True, host='0.0.0.0', port=5000)
