import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import requests
from io import StringIO
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import altair as alt
from collections import Counter
import jieba

# --- 常量定义 ---
PERSISTENT_STORAGE_PATH = "/data"
DATA_FILE = os.path.join(PERSISTENT_STORAGE_PATH, "companies.parquet")
LAST_UPDATE_FILE = os.path.join(PERSISTENT_STORAGE_PATH, "last_update.txt")
UPDATE_INTERVAL_DAYS = 3

# --- 核心数据逻辑 ---
def fetch_data_from_web():
    data_url = "https://gist.githubusercontent.com/ai-side-projects/74884107a729e240c4974751ed23811e/raw/companies_data.csv"
    print("开始从 URL 抓取数据...")
    try:
        response = requests.get(data_url, timeout=30)
        response.raise_for_status()
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)
        print(f"抓取到 {len(df)} 条数据。")
        return df
    except requests.exceptions.RequestException as e:
        print(f"数据抓取失败: {e}")
        return None

def check_and_update_data():
    now = datetime.utcnow()
    if not os.path.exists(DATA_FILE) or not os.path.exists(LAST_UPDATE_FILE):
         print("首次运行或数据文件丢失，需要抓取数据。")
         df = fetch_data_from_web()
         if df is not None:
            df.to_parquet(DATA_FILE, index=False)
            with open(LAST_UPDATE_FILE, "w") as f:
                f.write(now.isoformat())
            return "FIRST_RUN", "首次运行，数据已成功下载！", df
         else:
            return "FAILED", "首次数据下载失败，请稍后刷新。", pd.DataFrame()

    with open(LAST_UPDATE_FILE, "r") as f:
        last_update_time = datetime.fromisoformat(f.read())

    if now - last_update_time > timedelta(days=UPDATE_INTERVAL_DAYS):
        print(f"数据已过期，需要更新。")
        df = fetch_data_from_web()
        if df is not None:
            df.to_parquet(DATA_FILE, index=False)
            with open(LAST_UPDATE_FILE, "w") as f:
                f.write(now.isoformat())
            return "UPDATED", "数据已成功更新！", df
        else:
            return "FAILED", "数据更新失败，使用旧数据。", pd.read_parquet(DATA_FILE)

    print("数据为最新。")
    df = pd.read_parquet(DATA_FILE)
    return "UP_TO_DATE", "数据为最新版本。", df

# --- UI 界面函数 ---
STOP_WORDS = {"公司", "有限", "责任", "技术", "科技", "发展", "的", "和", "等", "与", "及"}
def draw_heatmap(df):
    st.subheader("🗺 企业地理分布热力图")
    df_geo = df.dropna(subset=["纬度", "经度"])
    if df_geo.empty:
        st.warning("无地理数据可供显示。")
        return
    map_center = [df_geo["纬度"].mean(), df_geo["经度"].mean()]
    m = folium.Map(location=map_center, zoom_start=5)
    HeatMap(data=df_geo[["纬度", "经度"]].values, radius=12).add_to(m)
    st_folium(m, width=700, height=500)

def product_bar_chart(df):
    st.subheader("📊 主营产品关键词频次图")
    if df.empty:
        st.warning("无产品数据可供分析。")
        return
    texts = " ".join(df["主营产品"].astype(str).tolist())
    words = jieba.lcut(texts)
    words = [w for w in words if len(w) > 1 and w not in STOP_WORDS]
    top_words = Counter(words).most_common(15)
    if not top_words:
        st.info("未提取到有效关键词。")
        return
    bar_df = pd.DataFrame(top_words, columns=["关键词", "频次"])
    chart = alt.Chart(bar_df).mark_bar().encode(
        x=alt.X("频次:Q"),
        y=alt.Y("关键词:N", sort="-x"),
        tooltip=["关键词", "频次"]
    ).properties(title="主营产品高频词 Top 15")
    st.altair_chart(chart, use_container_width=True)

# --- 主程序 ---
def main():
    st.set_page_config(page_title="动态机器人客户情报平台", layout="wide")
    st.title("🤖 动态中国机器人制造业客户情报平台")
    st.caption("数据会定期自动更新")

    with st.spinner("正在初始化并检查数据版本..."):
        status, message, df = check_and_update_data()

    if status in ["FIRST_RUN", "UPDATED"]:
        st.success(message)
    elif status == "FAILED":
        st.error(message)

    if df.empty:
        st.warning("数据当前为空，请稍后刷新重试。")
        return

    # UI 界面渲染
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
