import streamlit as st
import os

st.set_page_config(layout="wide")
st.title("🕵️ 服务器内部文件侦测")

st.info("这个页面旨在帮助我们理解服务器的文件结构。")

try:
    # 获取当前的工作目录
    current_directory = os.getcwd()
    st.header("当前工作目录 (app.py 所在的位置):")
    st.code(current_directory, language="bash")

    # 列出当前目录下的所有文件和文件夹
    st.header("在当前目录下找到的文件和文件夹:")
    files_in_current_dir = os.listdir(current_directory)
    st.code("\n".join(files_in_current_dir), language="bash")

    # 检查我们的数据文件是否在这里
    if "companies_data.csv" in files_in_current_dir:
        st.success("🎉 好消息！'companies_data.csv' 文件就在这里！")
    else:
        st.error("❌ 坏消息！'companies_data.csv' 文件不在这里。这正是问题所在！")

except Exception as e:
    st.error("在侦测文件时发生了意想不到的错误。")
    st.exception(e)
