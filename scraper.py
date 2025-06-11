# scraper.py (最终方案 - 使用最底层的 requests 库与 Supabase API 交互)

import os
import pandas as pd
import requests
import json

# --- 从 GitHub Actions 的 Secrets 中获取密钥 ---
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# --- 准备与 Supabase API 交互所需的信息 ---
# 这是我们要操作的表的 API 地址
table_url = f"{url}/rest/v1/companies"
# 这是 API 请求所需的认证头
headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation" 
}

# --- 自动化爬虫逻辑 ---
def fetch_data_from_real_api():
    """从一个绝对可靠的、公开的网站API抓取数据"""
    api_url = "https://jsonplaceholder.typicode.com/users"
    print(f"正在从真正的网站API '{api_url}' 抓取数据...")
    try:
        response = requests.get(api_url)
        response.raise_for_status() 
        json_data = response.json()
        df = pd.DataFrame(json_data)
        print(f"成功从API抓取到 {len(df)} 条数据。")
        return df
    except Exception as e:
        print(f"从API抓取数据时发生致命错误: {e}")
        return pd.DataFrame()

# --- 数据库更新逻辑 ---
def update_database(df):
    """使用 requests 库将数据更新到 Supabase 数据库"""
    if df.empty:
        print("没有抓取到数据，跳过数据库更新。"); return

    print("准备将数据写入数据库...")
    df_to_insert = pd.DataFrame({
        'company_name': df['company'].apply(lambda x: x.get('name', 'N/A')),
        'province': df['address'].apply(lambda x: x.get('city', 'N/A')),
        'city': df['address'].apply(lambda x: x.get('street', 'N/A')),
        'main_product': df['company'].apply(lambda x: x.get('catchPhrase', 'N/A')),
        'phone': df['phone'], 'email': df['email'], 'website': df['website'].apply(lambda x: f"http://{x}"),
        'latitude': df['address'].apply(lambda x: x['geo']['lat']), 'longitude': df['address'].apply(lambda x: x['geo']['lng'])
    })
    records = df_to_insert.to_dict(orient="records")
    
    try:
        # 1. 清空旧数据：向表地址发送 DELETE 请求
        print("清空旧数据...")
        delete_response = requests.delete(f"{table_url}?id=gt.0", headers=headers)
        delete_response.raise_for_status()
        print("旧数据清空成功。")

        # 2. 插入新数据：向表地址发送 POST 请求
        print("开始插入新数据...")
        insert_response = requests.post(table_url, headers=headers, data=json.dumps(records))
        insert_response.raise_for_status()
        inserted_count = len(insert_response.json())
        print(f"成功插入 {inserted_count} 条新数据。")
        
    except requests.exceptions.RequestException as e:
        print(f"数据库操作失败: {e}")
        print(f"失败时的响应内容: {e.response.text if e.response else 'No response'}")

# --- 主执行函数 ---
if __name__ == "__main__":
    print("自动化生产线启动 (requests 最终版)...")
    api_df = fetch_data_from_real_api()
    update_database(api_df)
    print("本轮自动化生产任务完成。")
