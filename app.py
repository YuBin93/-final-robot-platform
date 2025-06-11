# app.py (最终诊断版 - Secrets 检测工具)

import streamlit as st

st.set_page_config(layout="wide")
st.title("🕵️ Streamlit Secrets 诊断工具")
st.info("本工具用于检测应用是否能正确从环境中读取您配置的密钥。")

# 检查 st.secrets 是否被正确加载
if not st.secrets:
    st.error("致命错误：Streamlit 的 st.secrets 对象为空！应用没有加载任何密钥。")
else:
    st.success("好消息：st.secrets 对象已成功加载。")

    # --- 检查 SUPABASE_URL ---
    st.header("1. 检查 SUPABASE_URL")
    if "SUPABASE_URL" in st.secrets:
        url = st.secrets["SUPABASE_URL"]
        st.success("✅ 成功找到了 'SUPABASE_URL'。")
        st.write("它读取到的值是：")
        st.code(url, language="bash") # URL是公开信息，可以直接显示
    else:
        st.error("❌ 失败：在 st.secrets 中没有找到名为 'SUPABASE_URL' 的密钥。请检查名称拼写。")

    # --- 安全地检查 SUPABASE_KEY ---
    st.header("2. 检查 SUPABASE_KEY")
    if "SUPABASE_KEY" in st.secrets:
        key = st.secrets["SUPABASE_KEY"]
        st.success("✅ 成功找到了 'SUPABASE_KEY'。")
        
        # 为了安全，我们绝不显示完整的密钥
        st.write("为了您的安全，密钥的完整内容不会被显示。以下是它的诊断信息：")
        key_type = type(key).__name__
        key_length = len(key)
        key_start = key[:5] if key_length > 5 else key
        
        st.code(f"""
类型 (Type): {key_type}
长度 (Length): {key_length}
开头的几个字符: {key_start}...
        """, language="bash")
        
        if key_length < 50:
            st.warning("警告：这个密钥的长度看起来有点短，请确认您复制的是完整的 service_role key。")
            
    else:
        st.error("❌ 失败：在 st.secrets 中没有找到名为 'SUPABASE_KEY' 的密钥。请检查名称拼写。")
