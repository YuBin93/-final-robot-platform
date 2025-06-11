# scraper.py (最终方案 - 从可靠的公共API自动爬取)

import os
import pandas as pd
from supabase import create_client, Client
import requests # 我们将使用 requests 库来访问真正的网站API

# --- 数据库连接 ---
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# --- 自动化爬虫逻辑 ---
def fetch_data_from_real_api():
    """从一个绝对可靠的、公开的网站API抓取数据"""
    # 这是一个专为开发者测试使用的、非常稳定的公共API
    api_url = "https://jsonplaceholder.typicode.com/users"
    print(f"正在从真正的网站API '{api_url}' 抓取数据...")
    
    try:
        response = requests.get(api_url)
        # 如果请求失败 (比如404, 500等)，这行代码会报错，确保我们不会处理错误的数据
        response.raise_for_status() 
        
        # 将网站返回的JSON数据直接转换为Python的列表字典格式
        json_data = response.json()
        
        # 将数据转换为Pandas DataFrame，方便处理
        df = pd.DataFrame(json_data)
        
        print(f"成功从API抓取到 {len(df)} 条数据。")
        return df
        
    except Exception as e:
        print(f"从API抓取数据时发生致命错误: {e}")
        return pd.DataFrame() # 返回空DataFrame以避免后续错误

# --- 数据库更新逻辑 ---
def update_database(df):
    """将抓取到的数据处理并更新到 Supabase 数据库"""
    if df.empty:
        print("没有抓取到数据，跳过数据库更新。")
        return

    print("准备将数据写入数据库...")
    # 为了匹配我们的数据库表结构，我们需要对从API抓取的数据进行重命名和挑选
    # 这是一个真实场景中非常常见的操作：数据清洗和转换 (ETL)
    df_to_insert = pd.DataFrame({
        'company_name': df['company'].apply(lambda x: x.get('name', 'N/A')),
        'province': df['address'].apply(lambda x: x.get('city', 'N/A')), # 用city模拟省份
        'city': df['address'].apply(lambda x: x.get('street', 'N/A')), # 用street模拟城市
        'main_product': df['company'].apply(lambda x: x.get('catchPhrase', 'N/A')),
        'phone': df['phone'],
        'email': df['email'],
        'website': df['website'].apply(lambda x: f"http://{x}"), # 确保网址格式正确
        'latitude': df['address'].apply(lambda x: x['geo']['lat']),
        'longitude': df['address'].apply(lambda x: x['geo']['lng'])
    })
    
    records = df_to_insert.to_dict(orient="records")
    
    print("清空旧数据...")
    supabase.table("companies").delete().gt("id", -1).execute() # 使用-1确保清空所有

    print("开始插入新数据...")
    data, error = supabase.table("companies").insert(records).execute()

    if error and error[1]: # 检查是否存在错误
        print(f"数据库插入失败: {error[1]}")
    else:
        # v1版本的supabase-py在成功时data[1]是数据列表
        print(f"成功插入 {len(data[1]) if data else 0} 条新数据。")

# --- 主执行函数 ---
if __name__ == "__main__":
    print("自动化生产线启动...")
    api_df = fetch_data_from_real_api()
    update_database(api_df)
    print("本轮自动化生产任务完成。")
