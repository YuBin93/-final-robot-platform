import streamlit as st
import pandas as pd
import os
from collections import Counter
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import altair as alt
import jieba
from io import StringIO

# --- 关键修复：将CSV数据直接嵌入为多行字符串 ---
# 这使得应用完全自给自足，不再需要外部文件
csv_data = """公司名称,省份,城市,主营产品,联系电话,联系邮箱,官网,纬度,经度
机器人科技有限公司,广东,深圳,工业机器人、自动化解决方案,13800138000,contact@robot-tech.com,http://robot-tech.com,22.54,114.05
智能未来公司,上海,上海,服务机器人、人工智能软件,13900139000,info@smart-future.com,http://smart-future.com,31.23,121.47
北京精密制造,北京,北京,高精度机械臂、传感器,13700137000,sales@bj-precision.com,http://bj-precision.com,39.90,116.40
江苏自动化设备有限公司,江苏,南京,PLC控制器、传送带系统,13600136000,support@js-auto.com,http://js-auto.com,32.06,118.78
浙江智能装备集团,浙江,杭州,AGV小车、仓储机器人,13500135000,market@zj-smart.com,http://zj-smart.com,30.27,120.15
山东重工机器人,山东,济南,焊接机器人、重载机械臂,13400134000,hr@sd-heavy.com,http://sd-heavy.com,36.67,117.00
四川云端智能,四川,成都,云机器人平台、远程操作系统,13300133000,service@sc-cloud.com,http://sc-cloud.com,30.66,104.06
福建海洋机器人有限公司,福建,厦门,水下机器人、海洋探测设备,13200132000,sea@fj-ocean.com,http://fj-ocean.com,24.48,118.08
湖南智能制造研究院,湖南,长沙,机器人教育、AI算法研究,13100131000,edu@hn-ai.com,http://hn-ai.com,28.20,112.98
辽宁机器人创新中心,辽宁,沈阳,特种机器人、工业设计,13000130000,innovate@ln-robot.com,http://ln-robot.com,41.80,123.43
重庆机器人自动化,重庆,重庆,汽车制造自动化线,15900159000,auto@cq-robot.com,http://cq-robot.com,29.56,106.55
天津港口自动化,天津,天津,港口自动化龙门吊、AGV,15800158000,port@tj-auto.com,http://tj-auto.com,39.08,117.20
安徽核心零部件,安徽,合肥,伺服电机、减速器,15700157000,core@ah-parts.com,http://ah-parts.com,31.86,117.28
河北智能焊接,河北,石家庄,激光焊接机器人,15600156000,weld@hb-smart.com,http://hb-smart.com,38.04,114.50
陕西航空制造机器人,陕西,西安,航空零部件精密装配,15500155000,aero@sx-robot.com,http://sx-robot.com,34.27,108.95
"""

# --- 常量和配置 ---
st.set_page_config(layout="wide")
STOP_WORDS = {"公司", "有限", "责任", "技术", "科技", "发展", "的", "和", "等", "与", "及"}

# --- 核心数据加载逻辑 (最终版) ---
@st.cache_data(ttl=3600)
def load_data():
    """直接从代码内置的字符串数据加载，绝对可靠"""
    try:
        # 使用 io.StringIO 将字符串模拟成一个文件，让 pandas 读取
        df = pd.read_csv(StringIO(csv_data))
        return df
    except Exception as e:
        st.error(f"从内置数据加载时发生未知错误: {e}")
        return None

# --- 可视化函数 (保持不变) ---
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

# --- 主程序界面 (保持不变) ---
def main():
    st.title("🤖 中国机器人制造业客户情报平台")
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
