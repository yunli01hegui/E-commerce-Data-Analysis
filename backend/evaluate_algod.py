import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split

# =================================================================
# 实验设置：完全同步后端逻辑
# 邻居数：10 | 推荐条数：6 | 相似度：余弦相似度
# =================================================================

# 1. 数据库连接 (保持与你后端一致)
DB_USER = 'root'
DB_PASSWORD = ''
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'tmall_analytics'
engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

def run_offline_evaluation():
    # 2. 加载全量数据
    try:
        df = pd.read_sql("SELECT * FROM orders", con=engine)
        if df.empty:
            print("错误：数据库中没有数据。")
            return
    except Exception as e:
        print(f"连接数据库失败: {e}")
        return

    # 3. 划分训练集与测试集 (80/20 比例)
    # 训练集用于计算用户相似度，测试集用于验证预测是否准确
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

    # 4. 建立用户-品类偏好矩阵 (复制你后端的 pivot_table 逻辑)
    # 行：user_id, 列：category, 值：累计消费金额 (amount)
    user_item_matrix = train_df.pivot_table(
        index='user_id', columns='category', values='amount', aggfunc='sum'
    ).fillna(0)

    # 5. 获取测试集中的真实购买行为
    # 格式：{ 用户ID: [实际购买过的商品名集合] }
    test_user_behavior = test_df.groupby('user_id')['product_name'].apply(set).to_dict()

    # 初始化评估指标
    hit_count = 0        # 命中的商品数
    total_recommended = 0 # 总推荐给出的商品数
    total_actual = 0      # 用户实际在测试集买过的商品数
    all_recommended_items = set() # 用于计算覆盖率
    all_catalog_items = set(df['product_name'].unique()) # 全站商品池

    print(f"开始离线评估：测试用户规模 {len(test_user_behavior)} 人...")

    # 6. 开始模拟推荐过程
    for target_user in test_user_behavior.keys():
        # 如果用户不在训练集（冷启动用户），则跳过评估
        if target_user not in user_item_matrix.index:
            continue

        # --- 核心逻辑：复制你后端的推荐算法 ---
        # A. 计算余弦相似度
        user_vector = user_item_matrix.loc[target_user].values.reshape(1, -1)
        similarities = {}
        for other_user in user_item_matrix.index:
            if other_user == target_user: continue
            other_vector = user_item_matrix.loc[other_user].values.reshape(1, -1)
            # 余弦公式
            sim = np.dot(user_vector, other_vector.T) / (np.linalg.norm(user_vector) * np.linalg.norm(other_vector) + 1e-9)
            similarities[other_user] = sim[0][0]

        # B. 提取前 10 位邻居 (Top-10)
        top_similar_users = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:10]

        # C. 聚合邻居喜欢的商品并排除已购 (Weighted Score)
        user_bought_in_train = set(train_df[train_df['user_id'] == target_user]['product_name'])
        recommendations = {}

        for sim_user, score in top_similar_users:
            sim_user_orders = train_df[train_df['user_id'] == sim_user]
            for _, row in sim_user_orders.iterrows():
                prod_name = row['product_name']
                if prod_name not in user_bought_in_train:
                    if prod_name not in recommendations:
                        recommendations[prod_name] = 0
                    recommendations[prod_name] += score # 加权推荐分

        # D. 生成最终 Top-6 推荐列表
        final_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:6]
        rec_list = [item[0] for item in final_recs]

        # 7. 计算该用户的命中情况
        hits = set(rec_list) & test_user_behavior[target_user]

        hit_count += len(hits)
        total_recommended += len(rec_list)
        total_actual += len(test_user_behavior[target_user])
        all_recommended_items.update(rec_list)

    # 8. 输出量化评估结果
    precision = hit_count / total_recommended if total_recommended > 0 else 0
    recall = hit_count / total_actual if total_actual > 0 else 0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    coverage = len(all_recommended_items) / len(all_catalog_items) if len(all_catalog_items) > 0 else 0

    print("\n" + "="*40)
    print("      推荐算法离线评估报告 (学术版)")
    print("="*40)
    print(f"1. 准确率 (Precision@6): {precision:.2%}")
    print(f"2. 召回率 (Recall@6):    {recall:.2%}")
    print(f"3. F1 综合分数 (F1-Score): {f1:.2%}")
    print(f"4. 商品覆盖率 (Coverage):   {coverage:.2%}")
    print("="*40)
    print("注：以上结果基于天池数据集 1000 条流水 8:2 划分实测。")

if __name__ == "__main__":
    run_offline_evaluation()