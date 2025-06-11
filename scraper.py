import os
import pandas as pd
from supabase import create_client, Client
import asyncio

# --- 数据库连接 ---
# 从 GitHub Actions 的 Secrets 中获取密钥
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# --- 爬虫逻辑 ---
def fetch_data_from_source():
    """从我们指定的稳定URL抓取数据"""
    data_url = "https://gist.githubusercontent.com/ai-side-projects/74884107a729e240c4974751ed23811e/raw/companies_data.csv"
    print(f"正在从 {data_url} 抓取数据...")
    df = pd.read_csv(data_url)
    print(f"成功抓取到 {len(df)} 条数据。")
    return df

# --- 数据库更新逻辑 ---
def update_database(df):
    """将数据更新到 Supabase 数据库"""
    if df.empty:
        print("没有抓取到数据，跳过数据库更新。")
        return

    print("准备写入数据库...")
    # Supabase Python 客户端 v1 的列名需要与数据库列名完全匹配
    df_to_insert = df.rename(columns={
        '公司名称': 'company_name', '省份': 'province', '城市': 'city',
        '主营产品': 'main_product', '联系电话': 'phone', '联系邮箱': 'email',
        '官网': 'website', '纬度': 'latitude', '经度': 'longitude'
    })
    
    records = df_to_insert.to_dict(orient="records")

    # 为了确保数据最新，我们采用“先清空再插入”的策略
    print("清空旧数据...")
    # 注意：supabase-py v1 的 delete 是同步的
    supabase.table("companies").delete().gt("id", 0).execute()

    print("开始插入新数据...")
    _, error = supabase.table("companies").insert(records).execute()

    if error:
        print(f"数据库插入失败: {error}")
    else:
        # v1 的 insert 返回元组，第二个元素是错误
        print(f"成功插入 {len(records)} 条新数据。")

# --- 主执行函数 ---
if __name__ == "__main__":
    print("自动化数据采集任务开始...")
    crawled_df = fetch_data_from_source()
    update_database(crawled_df)
    print("自动化数据采集任务执行完毕。")
