import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- Supabase 数据库连接 ---
# 这些密钥将从 Streamlit Cloud 的 Secrets 中自动读取
try:
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    st.error("无法从 Streamlit Secrets 中读取数据库密钥，请确保已正确配置。")
    st.stop() # 如果没有密钥，则停止应用

# --- 核心数据加载逻辑 ---
@st.cache_data(ttl=600) # 从数据库加载，缓存10分钟
def load_data_from_db():
    """从 Supabase 数据库加载数据"""
    try:
        response = supabase.table("companies").select("*").execute()
        df = pd.DataFrame(response.data)
        
        # 将数据库的英文列名，重命名为我们需要的中文列名
        df.rename(columns={
            'company_name': '公司名称', 'province': '省份', 'city': '城市',
            'main_product': '主营产品', 'phone': '联系电话', 'email': '联系邮箱',
            'website': '官网', 'latitude': '纬度', 'longitude': '经度'
        }, inplace=True, errors='ignore')
        return df
    except Exception as e:
        st.error(f"从数据库加载数据时发生错误: {e}")
        return None

# --- 可视化和主程序界面 (与之前相同) ---
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import altair as alt
from collections import Counter
import jieba

st.set_page_config(layout="wide")
STOP_WORDS = {"公司", "有限", "责任", "技术", "科技", "发展", "的", "和", "等", "与", "及"}

def draw_heatmap(df):
    st.subheader("🗺 企业地理分布热力图")
    # ... (此处省略与之前版本完全相同的绘图代码) ...
def product_bar_chart(df):
    st.subheader("📊 主营产品关键词频次图")
    # ... (此处省略与之前版本完全相同的绘图代码) ...

def main():
    st.title("🤖 动态中国机器人制造业客户情报平台")
    st.caption("数据源：Supabase 云数据库")

    df = load_data_from_db()

    if df is None:
        st.error("数据加载失败，应用无法继续。")
        return

    if df.empty:
        st.success("🎉 应用已成功连接到数据库！")
        st.info("数据库当前为空，暂无数据显示。请等待后台爬虫任务写入数据。")
        st.stop()

    # --- 后续的筛选和显示逻辑 (与之前版本完全相同) ---
    st.sidebar.header("筛选条件")
    # ... (省略) ...

if __name__ == "__main__":
    main()
