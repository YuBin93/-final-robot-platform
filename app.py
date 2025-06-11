# app.py (最终方案 - 统一使用 postgrest-py)

import streamlit as st
import pandas as pd
from postgrest import PostgrestClient
import os
import asyncio
from collections import Counter
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import altair as alt
import jieba

# --- 常量和配置 ---
st.set_page_config(layout="wide")
STOP_WORDS = {"公司", "有限", "责任", "技术", "科技", "发展", "的", "和", "等", "与", "及"}
ADMIN_PASSWORD = "password123" 

# --- 数据库连接 ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    cleaned_url = url.rstrip('/')
    if not cleaned_url.endswith('/rest/v1'):
        base_url_for_client = cleaned_url + '/rest/v1'
    else:
        base_url_for_client = cleaned_url
    client = PostgrestClient(base_url=base_url_for_client, headers={"apikey": key, "Authorization": f"Bearer {key}"})
except Exception as e:
    st.error("无法初始化数据库连接，请检查 Streamlit Cloud 的 Secrets 配置。")
    st.exception(e)
    st.stop()

# --- 异步执行的辅助函数 ---
def run_async(coro):
    return asyncio.run(coro)

# --- 数据抓取与更新逻辑 ---
def run_scraper():
    """使用 postgrest-py 来完成爬虫和数据库更新"""
    try:
        with st.spinner("正在从数据源抓取最新数据..."):
            data_url = "https://gist.githubusercontent.com/ai-side-projects/74884107a729e240c4974751ed23811e/raw/companies_data.csv"
            df = pd.read_csv(data_url)
        
        with st.spinner(f"抓取到 {len(df)} 条数据。正在写入数据库..."):
            df_to_insert = df.rename(columns={
                '公司名称': 'company_name', '省份': 'province', '城市': 'city',
                '主营产品': 'main_product', '联系电话': 'phone', '联系邮箱': 'email',
                '官网': 'website', '纬度': 'latitude', '经度': 'longitude'
            })
            records = df_to_insert.to_dict(orient="records")
            
            # --- 关键修复：使用 postgrest-py 来执行数据库写入操作 ---
            run_async(client.from_("companies").delete().gt("id", 0).execute())
            run_async(client.from_("companies").insert(records).execute())
            
        st.success(f"数据更新成功！共写入 {len(records)} 条新记录。请刷新页面查看最新数据。")
        st.cache_data.clear()
        
    except Exception as e:
        st.error("数据更新过程中发生错误。")
        st.exception(e)

# --- 核心数据加载逻辑 ---
@st.cache_data(ttl=600)
def load_data():
    """从 Supabase 数据库加载数据"""
    try:
        response = run_async(client.from_("companies").select("*").execute())
        df = pd.DataFrame(response.data)
        df.rename(columns={
            'company_name': '公司名称', 'province': '省份', 'city': '城市',
            'main_product': '主营产品', 'phone': '联系电话', 'email': '联系邮箱',
            'website': '官网', 'latitude': '纬度', 'longitude': '经度'
        }, inplace=True, errors='ignore')
        return df
    except Exception as e:
        st.error(f"从数据库读取数据时发生错误。")
        st.exception(e)
        return pd.DataFrame()

# --- 可视化和主界面函数 ---
def draw_heatmap(df):
    st.subheader("🗺 企业地理分布热力图"); df_geo = df.dropna(subset=["纬度", "经度"]); map_center = [df_geo["纬度"].mean(), df_geo["经度"].mean()]; m = folium.Map(location=map_center, zoom_start=5); HeatMap(data=df_geo[["纬度", "经度"]].values, radius=12).add_to(m); st_folium(m, width=700, height=500)

def product_bar_chart(df):
    st.subheader("📊 主营产品关键词频次图"); texts = " ".join(df["主营产品"].astype(str).tolist()); words = jieba.lcut(texts); words = [w for w in words if len(w) > 1 and w not in STOP_WORDS]; top_words = Counter(words).most_common(15); bar_df = pd.DataFrame(top_words, columns=["关键词", "频次"]); chart = alt.Chart(bar_df).mark_bar().encode(x=alt.X("频次:Q"), y=alt.Y("关键词:N", sort="-x"), tooltip=["关键词", "频次"]).properties(title="主营产品高频词 Top 15"); st.altair_chart(chart, use_container_width=True)

def main():
    st.title("🤖 动态中国机器人制造业客户情报平台")
    st.caption("数据源：Supabase 实时云数据库 (最终版)")
    
    st.sidebar.subheader("⚙️ 管理员操作")
    password = st.sidebar.text_input("请输入管理员密码", type="password")
    if password == ADMIN_PASSWORD:
        if st.sidebar.button("立即更新数据"): run_scraper()
    elif password: st.sidebar.error("密码错误")

    df = load_data()
    
    if df.empty:
        st.warning("ℹ️ 数据库当前为空。请在左侧管理员操作区输入密码，并点击“立即更新数据”来填充初始数据。")
        st.stop()
            
    st.sidebar.divider()
    st.sidebar.header("筛选条件"); provinces = ["全部"] + sorted(df["省份"].unique().tolist()); province = st.sidebar.selectbox("选择省份", options=provinces); keyword = st.sidebar.text_input("产品关键词（模糊搜索）"); filtered_df = df.copy()
    if province != "全部": filtered_df = filtered_df[filtered_df["省份"] == province]
    if keyword: filtered_df = filtered_df[filtered_df["主营产品"].str.contains(keyword, na=False)]
    st.subheader("📋 企业列表"); st.dataframe(filtered_df[["公司名称", "主营产品", "联系电话", "联系邮箱", "城市", "官网"]], use_container_width=True)
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig'); st.download_button("📥 下载筛选结果 (CSV)", data=csv, file_name="robot_clients.csv"); st.divider()
    col1, col2 = st.columns(2)
    with col1: draw_heatmap(filtered_df)
    with col2: product_bar_chart(filtered_df)

if __name__ == "__main__":
    main()
