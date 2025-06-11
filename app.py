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

st.set_page_config(layout="wide")
STOP_WORDS = {"公司", "有限", "责任", "技术", "科技", "发展", "的", "和", "等", "与", "及"}

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

def run_async(coro):
    return asyncio.run(coro)

@st.cache_data(ttl=300)
def load_data():
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

def draw_heatmap(df):
    st.subheader("🗺 企业地理分布热力图")
    df_geo = df.dropna(subset=["纬度", "经度"])
    if df_geo.empty:
        st.warning("没有可供显示的地理数据。")
        return
    map_center = [df_geo["纬度"].mean(), df_geo["经度"].mean()]
    m = folium.Map(location=map_center, zoom_start=5)
    HeatMap(data=df_geo[["纬度", "经度"]].values, radius=12).add_to(m)
    st_folium(m, width=700, height=500)

def product_bar_chart(df):
    st.subheader("📊 主营产品关键词频次图")
    if df.empty or "主营产品" not in df.columns:
        st.warning("没有可供分析的产品数据。")
        return
    texts = " ".join(df["主营产品"].astype(str).tolist())
    words = jieba.lcut(texts)
    words = [w for w in words if len(w) > 1 and w not in STOP_WORDS]
    if not words:
        st.info("未提取到有效的关键词。")
        return
    top_words = Counter(words).most_common(15)
    bar_df = pd.DataFrame(top_words, columns=["关键词", "频次"])
    chart = alt.Chart(bar_df).mark_bar().encode(x=alt.X("频次:Q"), y=alt.Y("关键词:N", sort="-x"), tooltip=["关键词", "频次"]).properties(title="主营产品高频词 Top 15")
    st.altair_chart(chart, use_container_width=True)

def main():
    st.title("🤖 动态中国机器人制造业客户情报平台")
    st.caption("数据源：由自动化生产线每日更新")
    
    df = load_data()
    
    if df.empty:
        st.success("🎉 展示厅已准备就绪！")
        st.info("中央仓库当前为空，请前往您 GitHub 仓库的 'Actions' 页面，手动触发一次 'Scheduled Data Scraping' 生产任务来填充初始库存。")
        st.balloons()
        st.stop()
        
    st.sidebar.header("筛选条件")
    provinces = ["全部"] + sorted(df["省份"].unique().tolist())
    province = st.sidebar.selectbox("选择省份", options=provinces)
    keyword = st.sidebar.text_input("产品关键词（模糊搜索）")
    
    filtered_df = df.copy()
    if province != "全部":
        filtered_df = filtered_df[filtered_df["省份"] == province]
    if keyword:
        filtered_df = filtered_df[filtered_df["主营产品"].str.contains(keyword, na=False)]
        
    st.subheader("📋 企业列表")
    st.dataframe(filtered_df[["公司名称", "主营产品", "联系电话", "联系邮箱", "城市", "官网"]], use_container_width=True)
    
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下载筛选结果 (CSV)", data=csv, file_name="robot_clients.csv")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        draw_heatmap(filtered_df)
    with col2:
        product_bar_chart(filtered_df)

if __name__ == "__main__":
    main()
