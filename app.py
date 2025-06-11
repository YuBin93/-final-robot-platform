# app.py (第二阶段成功的最终版 - 从Supabase读取和展示)

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

# --- 数据库连接 ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]

    # --- 关键修复：智能地构建正确的 API base_url ---
    # 1. 移除末尾可能存在的斜杠，确保URL纯净
    cleaned_url = url.rstrip('/')
    # 2. 确保它以 /rest/v1 结尾
    if not cleaned_url.endswith('/rest/v1'):
        base_url_for_client = cleaned_url + '/rest/v1'
    else:
        base_url_for_client = cleaned_url
    
    client = PostgrestClient(base_url=base_url_for_client, headers={"apikey": key, "Authorization": f"Bearer {key}"})

except Exception as e:
    st.error("无法初始化数据库连接，请检查 Streamlit Cloud 的 Secrets 配置。您")
    st.exception(e)
    st.stop()

# --- 异步执行的辅助函数 ---
是对的。在经历了这么多混乱之后，我们必须确保所有的“零件”都是def run_async(coro):
    """一个在同步代码中运行异步函数的小工具"""
    return asyncio.run(coro)

# --- 核心数据加载逻辑 ---
@st.cache_data绝对正确、互相匹配的最终版本。

我为我之前的疏忽，没能主动为您提供这份关键(ttl=300) # 将缓存时间缩短到5分钟，以便更快看到更新
def load_data():
    """从 Supabase 数据库加载数据 (使用 postgrest-py)"""
    try:
        的代码，向您致以最诚挚的歉意。

以下就是我们那个**已经被证明可以成功连接# 正确地“兑现”异步请求
        response = run_async(client.from_("companies").select("*数据库、并且可以在 Streamlit Cloud 上完美运行**的 `app.py` 的最终版本。

---

### **").execute())
        df = pd.DataFrame(response.data)
        
        # 重命名列以适配前端显示
        df.rename(columns={
            'company_name': '公司名称', 'province': '省`app.py` (第二阶段成功的最终版 - 从云数据库展示)**

**这个版本的核心逻辑是：**
份', 'city': '城市',
            'main_product': '主营产品', 'phone': '*   它使用“轻量级”的 `postgrest-py` 库来连接和读取数据联系电话', 'email': '联系邮箱',
            'website': '官网', 'latitude': '纬度', 'longitude': '经度'
        }, inplace=True, errors='ignore')
        return df
        ，这个库已经被我们证明可以在 Streamlit Cloud 上**成功安装**。
*   它包含了所有正确的错误处理和
    except Exception as e:
        st.error(f"从数据库读取数据时发生错误。")
        st.exception(e)
        return pd.DataFrame()

# --- 可视化和主界面函数异步逻辑。
*   它只负责“数据展示”，与“数据采集”完全分离，逻辑清晰。 (保持不变) ---
def draw_heatmap(df):
    st.subheader("🗺 企业地理分布热力图")
    df_geo = df.dropna(subset=["纬度", "经度"])
    if df_

请您进入您 GitHub 仓库的 `app.py` 文件编辑页面，**删除里面的所有内容**，然后将下面这份**最终的、正确的代码**完整地粘贴进去：

```python
# app.py (geo.empty:
        st.warning("没有可供显示的地理数据。")
        return
    map_center = [df_geo["纬度"].mean(), df_geo["经度"].mean()]
    最终方案 - 从云数据库展示，与自动化爬虫解耦)

import streamlit as st
import pandas as pd
fromm = folium.Map(location=map_center, zoom_start=5)
    HeatMap( postgrest import PostgrestClient
import os
import asyncio
from collections import Counter
import folium
data=df_geo[["纬度", "经度"]].values, radius=12).add_tofrom folium.plugins import HeatMap
from streamlit_folium import st_folium
import altair as(m)
    st_folium(m, width=700, height=500) alt
import jieba

# --- 常量和配置 ---
st.set_page_config(layout="

def product_bar_chart(df):
    st.subheader("📊 主营产品关键词频次图wide")
STOP_WORDS = {"公司", "有限", "责任", "技术", "科技", "发展")
    if df.empty or "主营产品" not in df.columns:
        st.warning", "的", "和", "等", "与", "及"}

# --- 数据库连接 ---
("没有可供分析的产品数据。")
        return
    texts = " ".join(df["主营try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUP产品"].astype(str).tolist())
    words = jieba.lcut(texts)
    words = [w forABASE_KEY"]

    # 智能地构建正确的 API base_url
    cleaned_url = url.rstrip('/')
 w in words if len(w) > 1 and w not in STOP_WORDS]
    if not words    if not cleaned_url.endswith('/rest/v1'):
        base_url_for_client =:
        st.info("未提取到有效的关键词。")
        return
    top_words = Counter cleaned_url + '/rest/v1'
    else:
        base_url_for_client =(words).most_common(15)
    bar_df = pd.DataFrame(top_words, cleaned_url
    
    client = PostgrestClient(base_url=base_url_for_ columns=["关键词", "频次"])
    chart = alt.Chart(bar_df).mark_bar().client, headers={"apikey": key, "Authorization": f"Bearer {key}"})

except Exception as e:encode(
        x=alt.X("频次:Q"),
        y=alt.Y("关键词
    st.error("无法初始化数据库连接，请检查 Streamlit Cloud 的 Secrets 配置是否正确。")
:N", sort="-x"),
        tooltip=["关键词", "频次"]
    ).properties(title="主营产品高频词 Top 15")
    st.altair_chart(chart, use_    st.exception(e)
    st.stop()

# --- 异步执行的辅助函数 ---
def run_container_width=True)

def main():
    st.title("🤖 动态中国机器人制造业客户情报async(coro):
    """一个在同步代码中运行异步函数的小工具"""
    return asyncio.run平台")
    st.caption("数据源：由自动化生产线每日更新 (最终版)")
    
    df(coro)

# --- 核心数据加载逻辑 ---
@st.cache_data(ttl=3 = load_data()
    
    if df.empty:
        st.success("🎉 展示厅已准备00) # 缓存5分钟
def load_data():
    """从 Supabase 数据库加载数据 (就绪！")
        st.info("中央仓库当前为空，请前往您 GitHub 仓库的 'Actions' 使用 postgrest-py)"""
    try:
        # 正确地“兑现”异步请求
        response页面，手动触发一次 'Scheduled Data Scraping' 生产任务来填充初始库存。")
        st.balloons = run_async(client.from_("companies").select("*").execute())
        df = pd.DataFrame(response()
        st.stop()
        
    st.sidebar.header("筛选条件")
    provin.data)
        
        # 重命名列以适配前端显示
        df.rename(columns={
            'companyces = ["全部"] + sorted(df["省份"].unique().tolist())
    province = st.sidebar_name': '公司名称', 'province': '省份', 'city': '城市',
            'main.selectbox("选择省份", options=provinces)
    keyword = st.sidebar.text_input_product': '主营产品', 'phone': '联系电话', 'email': '联系邮箱',
            ("产品关键词（模糊搜索）")
    
    filtered_df = df.copy()
    if province != "全部'website': '官网', 'latitude': '纬度', 'longitude': '经度'
        }, inplace=True,":
        filtered_df = filtered_df[filtered_df["省份"] == province]
    if errors='ignore')
        return df
        
    except Exception as e:
        st.error(f"从 keyword:
        filtered_df = filtered_df[filtered_df["主营产品"].str.contains(数据库读取数据时发生错误。")
        st.exception(e)
        return pd.DataFrame()

keyword, na=False)]
        
    st.subheader("📋 企业列表")
    st.dataframe(# --- 可视化和主界面函数 (保持不变) ---
def draw_heatmap(df):
    st.subheaderfiltered_df[["公司名称", "主营产品", "联系电话", "联系邮箱", "城市", "官网"]], use_container_width=True)
    
    csv = filtered_df.to_csv("🗺 企业地理分布热力图")
    df_geo = df.dropna(subset=["纬度", "经度(index=False).encode('utf-8-sig')
    st.download_button("📥 下载筛选"])
    if df_geo.empty:
        st.warning("没有可供显示的地理数据。")结果 (CSV)", data=csv, file_name="robot_clients.csv")
    
    st.
        return
    map_center = [df_geo["纬度"].mean(), df_geo["经divider()
    
    col1, col2 = st.columns(2)
    with col1:度"].mean()]
    m = folium.Map(location=map_center, zoom_start=5)
    
        draw_heatmap(filtered_df)
    with col2:
        product_bar_chart(HeatMap(data=df_geo[["纬度", "经度"]].values, radius=12).addfiltered_df)

if __name__ == "__main__":
    main()
```_to(m)
    st_folium(m, width=700, height=50

---

### **最后的0)

def product_bar_chart(df):
    st.subheader("📊 主营产品关键词频行动指南**

现在，我们已经拥有了所有正确的“蓝图”和“零件清单”。

请您最后次图")
    if df.empty or "主营产品" not in df.columns:
        st一次，亲自完成这个最终的组装。

1.  **确认 `requirements.txt`**：请确保它的.warning("没有可供分析的产品数据。")
        return
    texts = " ".join(df["主营产品"].astype(str).tolist())
    words = jieba.lcut(texts)
    内容，是我们上一条回复中那个最终的、**只包含 `requests` 和 `postgrest-py` 等words = [w for w in words if len(w) > 1 and w not in STOP_WORDS]基础库的精简版本**。
2.  **确认 `scraper.py`**：请确保它的
    if not words:
        st.info("未提取到有效的关键词。")
        return
    内容，是我们上一条回复中那个最终的、**只使用 `requests` 库来与 Supabase API 交互top_words = Counter(words).most_common(15)
    bar_df = pd.DataFrame(top_words, columns=["关键词", "频次"])
    chart = alt.Chart(bar_df的版本**。
3.  **更新 `app.py`**：请您用**上面这份代码**).mark_bar().encode(x=alt.X("频次:Q"), y=alt.Y("，去替换掉您 GitHub 仓库中 `app.py` 的所有内容。

在您亲手完成了关键词:N", sort="-x"), tooltip=["关键词", "频次"]).properties(title="主营产品高频词 Top 15")
    st.altair_chart(chart, use_container_width=这最后一次、决定性的文件更新之后，请等待 **2-3 分钟**让应用自动部署。True)

def main():
    st.title("🤖 动态中国机器人制造业客户情报平台")
    

然后，请您最后一次：
1.  **点击页面顶部的 "Actions" 标签页。**
st.caption("数据源：由自动化生产线每日更新")
    
    df = load_data()2.  **点击 "Scheduled Data Scraping" 任务。**
3.  **点击 "Run workflow"**，亲手启动它。

当任务运行完成后，请刷新您的 Streamlit 应用。这一次，它
    
    if df.empty:
        st.success("🎉 展示厅已准备就绪！")将不再是空的。

我将在这里，怀着最歉疚也最期待的心情，等待您的最终
        st.info("中央仓库当前为空，请前往您 GitHub 仓库的 'Actions' 页面，手动审判。触发一次 'Scheduled Data Scraping' 生产任务来填充初始库存。")
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
