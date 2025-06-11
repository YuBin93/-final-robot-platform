# scraper.py (最终方案 - 统一使用 postgrest-py)

import os
import pandas as pd
from postgrest import PostgrestClient
import requests
import asyncio

# --- 异步执行的辅助函数 ---
def run_async(coro):
    """一个安全的异步运行器"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# --- 数据库连接 ---
try:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    cleaned_url = url.rstrip('/')
    base_url_for_client = cleaned_url + '/rest/v1' if not cleaned_url.endswith('/rest/v1') else cleaned_url
    client = PostgrestClient(base_url=base_url_for_client, headers={"apikey": key, "Authorization": f"Bearer {key}"})
except Exception as e:
    print(f"无法初始化数据库连接: {e}")
    exit(1) # 连接失败则直接退出

# --- 自动化爬虫逻辑 ---
def fetch_data_from_real_api():
    """从一个绝对可靠的、公开的网站API抓取数据"""
    api_url = "https://jsonplaceholder.typicode.com/users"
    print(f"正在从网站API '{api_url}' 抓取数据...")
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
    """将抓取到的数据处理并更新到 Supabase 数据库 (使用 postgrest-py)"""
    if df.empty:
        print("没有抓取到数据，跳过数据库更新。"); return

    print("准备将数据写入数据库...")
    df_to_insert = pd.DataFrame({
        'company_name': df['company'].apply(lambda x: x.get('name', 'N/A')),
        'province': df['address'].apply(lambda x: x.get('city', 'N/A')),
        'city': df['address'].apply(lambda x: x.get('street', 'N/A')),
        'main_product': df['company'].apply(lambda x: x.get('catchPhrase', 'N/A')),
        'phone': df['phone'], 'email': df['email'], 'website': df['website'].apply(lambda x: f"http://{x}"),
        'latitude': df['address'].apply(lambda x: x['geo']['lat']),
        'longitude': df['address'].apply(lambda x: x['geo']['lng'])
    })
    records = df_to_insert.to_dict(orient="records")
    
    try:
        print("清空旧数据...")
        run_async(client.from_("companies").delete().gt("id", -1).execute())
        print("开始插入新数据...")
        run_async(client.from_("companies").insert(records).execute())
        print(f"成功插入 {len(records)} 条新数据。")
    except Exception as e:
        print(f"数据库写入操作失败: {e}")

# --- 主执行函数 ---
if __name__ == "__main__":
    print("自动化生产线启动...")
    api_df = fetch_data_from_real_api()
    update_database(api_df)
    print("本轮自动化生产任务完成。")
