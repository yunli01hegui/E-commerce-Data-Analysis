import pandas as pd
from sqlalchemy import create_engine, text
import os

# =================================================================
# 数据库初始化与数据导入脚本 (Database Initialization & Data Ingestion)
# 功能：
# 1. 自动创建 MySQL 数据库。
# 2. 读取 CSV 文件（天猫、淘宝等不同来源）。
# 3. 智能映射中文列名至标准数据库字段。
# 4. 数据清洗与预处理。
# 5. 全量同步数据至 MySQL 并重建索引。
# =================================================================

# -----------------------------------------------------------------
# 数据库配置信息
# -----------------------------------------------------------------
DB_USER = 'root'
DB_PASSWORD = ''  # ⚠️ 请在此处填写您的 MySQL 密码
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'tmall_analytics'

def init_database():
    """
    【初始化数据库环境】
    逻辑：
    1. 连接到 MySQL 服务器（不指定数据库名）。
    2. 如果目标数据库 'tmall_analytics' 不存在，则执行创建。
    3. 使用 utf8mb4 编码以完美支持中文字符。
    """
    # 基础连接字符串（用于创建数据库）
    conn_str = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}'
    engine = create_engine(conn_str)
    
    with engine.connect() as conn:
        print(f"正在检查/创建数据库: {DB_NAME}...")
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4"))
        conn.execute(text("COMMIT"))
    
    print(f"数据库 '{DB_NAME}' 已就绪。")

def ingest_csv_to_mysql():
    """
    【CSV 智能导入核心逻辑】
    包含：编码自动识别、模糊列名匹配、数据清洗、物理存储同步。
    """
    # 连接到具体业务数据库的引擎
    conn_str = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    engine = create_engine(conn_str)
    
    # 获取 CSV 文件路径（默认为 backend/data/天猫.csv）
    csv_path = os.path.join(os.path.dirname(__file__), 'data', '天猫.csv')
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"致命错误：未在路径 {csv_path} 找到 CSV 数据文件。")

    print(f"开始处理数据文件: {csv_path}...")
    
    # 1. 多编码尝试读取：解决 Excel 导出的 GBK 乱码问题
    df = None
    for enc in ['utf-8-sig', 'gbk', 'gb18030', 'utf-8', 'latin1']:
        try:
            df = pd.read_csv(csv_path, encoding=enc)
            print(f"成功使用 {enc} 编码读取文件。")
            break
        except Exception:
            continue
            
    if df is None:
        raise ValueError("无法解析 CSV 文件。请检查文件编码或格式是否正确。")

    # 2. 智能模糊映射规则：适配淘宝、天猫、京东等不同平台的导出表头
    mapping_rules = {
        'user_id': ['用户ID', '买家ID', '买家会员名', 'User ID', 'userId', 'UID'],
        'user_name': ['用户姓名', '姓名', '收货人姓名', '买家姓名', 'User Name', 'userName'],
        'product_id': ['商品ID', '宝贝ID', 'Product ID', 'productId', 'PID'],
        'product_name': ['商品名称', '宝贝名称', '标题', 'Product Name', 'productName'],
        'category': ['商品类别', '宝贝类别', '品类', 'Category', 'category'],
        'price': ['单价', '商品单价', 'Price', 'price'],
        'purchase_time': ['购买时间', '订单创建时间', '订单时间', 'Time', 'purchaseTime'],
        'quantity': ['购买数量', '数量', 'Quantity', 'quantity', 'count'],
        'amount': ['消费金额', '总金额', '实收金额', '应付金额', 'Amount', 'amount', 'total_price'],
        'city': ['用户城市', '收货城市', '城市', 'City', 'city'],
        'gender': ['用户性别', '性别', 'Gender', 'gender', 'Sex'],
        'age': ['用户年龄', '年龄', 'Age', 'age']
    }

    # 执行列名替换
    final_mapping = {}
    for standard_key, aliases in mapping_rules.items():
        for alias in aliases:
            if alias in df.columns:
                final_mapping[alias] = standard_key
                break
    
    df = df.rename(columns=final_mapping)
    print(f"字段映射完成。当前有效列: {df.columns.tolist()}")

    # 3. 数据清洗与格式化
    # 转换日期格式
    if 'purchase_time' in df.columns:
        df['purchase_time'] = pd.to_datetime(df['purchase_time'], errors='coerce')
    
    # 强制数值类型转换
    numeric_cols = ['price', 'quantity', 'amount', 'age']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 4. 关键数据完整性检查：剔除核心字段缺失的行
    required = ['user_id', 'product_id', 'amount']
    existing_required = [c for c in required if c in df.columns]
    df = df.dropna(subset=existing_required)
    
    print(f"清洗完成。待入库行数: {len(df)}")
    
    if len(df) == 0:
        raise ValueError("清洗后有效数据为 0，请检查 CSV 内容及表头是否符合规范。")

    # 5. 物理入库同步
    # 使用事务块确保操作的原子性
    try:
        with engine.begin() as conn:
            # 检查表是否存在
            result = conn.execute(text("SHOW TABLES LIKE 'orders'"))
            table_exists = result.fetchone() is not None
            
            if not table_exists:
                print("正在初始化 MySQL 数据库 (初始化模式)...")
                # 如果表不存在，使用 replace 创建新表
                df.to_sql('orders', con=conn, if_exists='replace', index=False)
                # 关键操作：在同步后的表中重新添加自增主键 ID 字段，作为 CRUD 操作的唯一标识
                print("正在创建自增主键 ID 索引...")
                conn.execute(text("ALTER TABLE orders ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST"))
            else:
                print("正在同步至 MySQL 数据库 (追加模式)...")
                # 如果表已存在，使用 append 追加数据
                # 注意：由于 to_sql('append') 不支持添加列，所以我们假设表结构已就绪
                df.to_sql('orders', con=conn, if_exists='append', index=False)
        
        print("✨ 数据同步成功！系统已就绪。")
    except Exception as e:
        print(f"入库失败: {e}")
        raise e

if __name__ == '__main__':
    # 程序执行入口
    try:
        init_database()         # 步骤1：初始化库
        ingest_csv_to_mysql()   # 步骤2：同步数据
    except Exception as e:
        print(f"\n❌ 执行失败！错误信息: {e}")
        print("\n[排查建议]:")
        print("1. 请确保本地 MySQL 服务已启动（默认端口 3306）。")
        print("2. 请检查 backend/db_init.py 中的 DB_PASSWORD 是否正确。")
        print("3. 请确保 backend/data/ 目录下存在有效的 .csv 数据文件。")
