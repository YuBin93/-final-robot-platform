import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from collections import Counter
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import altair as alt
import jieba

# --- 常量和配置 ---
st.set_page_config(layout="wide")
STOP_WORDS = {"公司", "有限", "责任", "技术", "科技", "发展", "的", "和", "等", "与", "及"}
DATA_FILE = "companies_data.csv"

# --- 核心数据加载逻辑 (最可靠的版本) ---
@st.cache_data(ttl=3600) # 缓存1小时
def load_data():
    """直接从项目仓库中的本地CSV文件加载数据"""
    print(f"尝试从本地文件 '{DATA_FILE}' 读取数据...")
    try:
        # 使用 os.path.join 确保路径正确
        # os.getcwd() 获取当前工作目录
        full_path = os.path.join(os.getcwd(), DATA_FILE)
        print(f"完整文件路径是: {full_path}")
        
        df = pd.read_csv(full_path)
        print(f"成功从本地文件读取到 {len(df)} 条数据。")
        return df
    except FileNotFoundError:
        st.error(f"致命错误：数据文件 '{DATA_FILE}' 在服务器上丢失或未找到。请联系技术支持。")
        st.info(f"当前工作目录是: {os.getcwd()}")
        st.info(f"此目录下的文件有: {os.listdir(os.getcwd())}")
        return None
    except Exception as e:
        st.error(f"读取数据文件时发生未知错误: {e}")
        return None

# --- 可视化函数 ---
def draw_heatmap(df):
    st.subheader("🗺 企业地理分布热力图")
    df_geo = df.dropna(subset=["纬度", "经度"])
    if df_geo.empty:
        st.warning("在当前筛选条件下，没有可供显示的地理数据。")
        return
    map_center = [df_geo["纬度"].mean(), df_geo["经度"].mean()]
    m = folium.Map(location=map_center, zoom_start=5)
    HeatMap(data=df_geo[["纬度", "经度"]].values, radius=12).add_to(m)
    st_folium(m, width=700, height=500)

def product_bar_chart(df):
    st.subheader("📊 主营产品关键词频次图")
    if df.empty or "主营产品" not in df.columns:
        st.warning("在当前筛选条件下，没有可供分析的产品数据。")
        return
    texts = " ".join(df["主营产品"].astype(str).tolist())
    words = jieba.lcut(texts)
    words = [w for w in words if len(w) > 1 and w not in STOP_WORDS]
    if not words:
        st.info("未提取到有效的关键词。")
        return
    top_words = Counter(words).most_common(15)
    bar_df = pd.DataFrame(top_words, columns=["关键词", "频次"])
    chart = alt.Chart(bar_df).mark_bar().encode(
        x=alt.X("频次:Q"),
        y=alt.Y("关键词:N", sort="-x"),
        tooltip=["关键词", "频次"]
    ).properties(title="主营产品高频词 Top 15")
    st.altair_chart(chart, use_container_width=True)

# --- 主程序界面 ---
def main():
    st.title("🤖 动态中国机器人制造业客户情报平台")
    st.caption("数据源已内置，可稳定运行")

    df = load_data()

    if df is None:
        st.error("数据加载失败，应用无法继续。")
        return
    
    # --- 筛选器 ---
    st.sidebar.header("筛选条件")
    provinces = ["全部"] + sorted(df["省份"].unique().tolist())
    province = st.sidebar.selectbox("选择省份", options=provinces)
    keyword = st.sidebar.text_input("产品关键词（模糊搜索）")

    # --- 数据筛选逻辑 ---
    filtered_df = df.copy()
    if province != "全部":
        filtered_df = filtered_df[filtered_df["省份"] == province]
    if keyword:
        filtered_df = filtered_df[filtered_df["主营产品"].str.contains(keyword, na=False)]

    # --- 页面主体内容 ---
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
