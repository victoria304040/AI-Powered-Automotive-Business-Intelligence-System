import streamlit as st
import pandas as pd
import os
from typing import Dict, List, Optional
import io
from datetime import datetime

# 確保 API Key 可用於 LangChain 程式碼
def setup_api_key():
    """設定 OpenAI API Key 供 LangChain 使用"""
    if not os.environ.get("OPENAI_API_KEY"):
        # 優先使用 Streamlit Cloud secrets
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
        # 其次使用本地 secret_key 檔案
        elif os.path.exists("secret_key"):
            with open("secret_key", "r", encoding="utf-8") as f:
                os.environ["OPENAI_API_KEY"] = f.read().strip()

# 設定 API Key
setup_api_key()

# 導入您現有的 LangChain 程式碼（不做任何修改）
from solution_combine import query_agent, dataframes

# 頁面配置
st.set_page_config(
    page_title="HOTAI MOTOR 銷售數據分析平台",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 初始化 session state
def init_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []

init_session_state()

# 側邊欄導航
def sidebar_navigation():
    st.sidebar.markdown("## 🚗 HOTAI MOTOR")
    st.sidebar.markdown("### 銷售數據分析平台")
    
    page = st.sidebar.selectbox(
        "選擇功能",
        ["📤 資料上傳", "📊 資料檢視", "💬 智能問答"]
    )
    
    st.sidebar.markdown("---")
    
    # 顯示目前目錄的檔案狀態
    st.sidebar.markdown("### 📁 檔案狀態")
    
    # 檢查必要檔案
    required_files = [
        "MBIS實績_2025上半年.xlsx",
        "經銷商目標_2025上半年.xlsx", 
        "Mapping Dataframe.xlsx"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            st.sidebar.markdown(f"✅ {file}")
        else:
            st.sidebar.markdown(f"❌ {file}")
    
    # 顯示已載入的 dataframes 狀態
    if dataframes:
        st.sidebar.markdown("### 📊 已載入資料")
        for key in dataframes.keys():
            df = dataframes[key]
            st.sidebar.markdown(f"• {key}: {len(df)} 行")
    
    return page

# 檔案上傳功能
def file_upload_page():
    st.markdown('<div class="main-header">📤 資料上傳</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <h4>📋 使用說明</h4>
    <p>本系統需要以下三個 Excel 檔案才能正常運作：</p>
    <ul>
        <li><strong>MBIS實績_2025上半年.xlsx</strong> - 實際銷售資料</li>
        <li><strong>經銷商目標_2025上半年.xlsx</strong> - 銷售目標資料</li>
        <li><strong>Mapping Dataframe.xlsx</strong> - 經銷商對應表</li>
    </ul>
    <p>您可以上傳檔案或使用現有目錄中的檔案。</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 檔案上傳區域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📤 檔案上傳")
        
        # 檔案上傳器
        uploaded_files = st.file_uploader(
            "選擇 Excel 檔案",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            help="請上傳：MBIS實績_2025上半年.xlsx、經銷商目標_2025上半年.xlsx、Mapping Dataframe.xlsx"
        )
        
        # 處理上傳的檔案
        if uploaded_files:
            st.markdown("### 📋 上傳檔案處理")
            for uploaded_file in uploaded_files:
                try:
                    # 保存檔案到目錄
                    file_path = uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    st.success(f"✅ 已保存檔案：{uploaded_file.name}")
                    
                    # 顯示檔案基本資訊
                    file_size = len(uploaded_file.getbuffer())
                    st.info(f"📁 檔案大小：{file_size:,} bytes")
                    
                except Exception as e:
                    st.error(f"❌ 保存檔案失敗：{uploaded_file.name} - {str(e)}")
        
        st.markdown("---")
        
        st.markdown("### 📁 目前檔案狀態")
        
        # 檢查並顯示檔案狀態
        required_files = {
            "MBIS實績_2025上半年.xlsx": "實際銷售資料",
            "經銷商目標_2025上半年.xlsx": "銷售目標資料", 
            "Mapping Dataframe.xlsx": "經銷商對應表"
        }
        
        all_files_exist = True
        for filename, description in required_files.items():
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                st.markdown(f"✅ **{filename}** ({description}) - {file_size:,} bytes")
            else:
                st.markdown(f"❌ **{filename}** ({description}) - 檔案不存在")
                all_files_exist = False
        
        if all_files_exist:
            st.markdown("""
            <div class="success-box">
            ✅ <strong>所有必要檔案已準備就緒！</strong><br>
            您可以前往「智能問答」頁面開始使用分析功能。
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ 請上傳或確保所有必要檔案都存在")
    
    with col2:
        st.markdown("""
        <div class="info-box">
        <h4>💡 檔案要求</h4>
        <ul>
            <li>支援格式：.xlsx, .xls</li>
            <li>檔案大小：< 200MB</li>
            <li>編碼：UTF-8</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h4>🔧 系統整合</h4>
        <p>上傳的檔案會自動保存到程式目錄，您現有的 LangChain 程式碼會自動讀取這些檔案。</p>
        </div>
        """, unsafe_allow_html=True)

# 資料檢視功能
def data_view_page():
    st.markdown('<div class="main-header">📊 資料檢視</div>', unsafe_allow_html=True)
    
    # 顯示目前已載入的 dataframes
    if not dataframes:
        st.info("📝 尚未載入任何資料。請先在「智能問答」中提問以載入資料，或確保必要檔案存在於目錄中。")
        return
    
    st.markdown("### 📋 已載入的資料集")
    
    # 讓用戶選擇要檢視的資料集
    if dataframes:
        selected_key = st.selectbox(
            "選擇要檢視的資料集",
            list(dataframes.keys())
        )
        
        if selected_key:
            df = dataframes[selected_key]
            
            # 資料基本資訊
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("總行數", len(df))
            with col2:
                st.metric("總欄數", len(df.columns))
            with col3:
                st.metric("缺失值", df.isnull().sum().sum())
            with col4:
                st.metric("重複行", df.duplicated().sum())
            
            # 資料預覽
            st.markdown(f"### 📋 {selected_key} - 資料預覽")
            
            # 顯示行數選擇
            preview_rows = st.slider("顯示行數", 5, min(100, len(df)), 20)
            st.dataframe(df.head(preview_rows), use_container_width=True)
            
            # 欄位資訊
            st.markdown("### 📊 欄位資訊")
            col_info = pd.DataFrame({
                '欄位名稱': df.columns,
                '資料類型': df.dtypes.astype(str),
                '非空值數量': df.count(),
                '唯一值數量': df.nunique(),
                '範例值': [str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else 'N/A' for col in df.columns]
            })
            st.dataframe(col_info, use_container_width=True)

# 智能問答功能
def qa_interface_page():
    st.markdown('<div class="main-header">💬 智能問答</div>', unsafe_allow_html=True)
    
    # 檢查 API Key 是否設定（支援 Streamlit Cloud 和本地環境）
    api_key_available = False
    
    # 檢查 Streamlit secrets（雲端環境）
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        api_key_available = True
        api_source = "Streamlit Cloud Secrets"
    # 檢查環境變數
    elif os.environ.get("OPENAI_API_KEY"):
        api_key_available = True
        api_source = "環境變數"
    # 檢查本地 secret_key 檔案
    elif os.path.exists("secret_key"):
        api_key_available = True
        api_source = "本地 secret_key 檔案"
    
    if not api_key_available:
        st.error("""
        ❌ **未找到 OpenAI API Key**
        
        請設定 API Key：
        - **Streamlit Cloud**：在 App settings → Advanced settings → Secrets 中設定 `OPENAI_API_KEY`
        - **本地開發**：建立 `secret_key` 檔案或設定環境變數 `OPENAI_API_KEY`
        """)
        return
    else:
        st.success(f"✅ API Key 已設定 (來源: {api_source})")
    
    # 聊天介面
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.markdown("""
        <div class="info-box">
        <h4>🔧 可用功能</h4>
        <ul>
            <li>一般資料探索分析</li>
            <li>目標 vs. 實際比對</li>
            <li>銷售進度查詢</li>
            <li>排行統計分析</li>
            <li>經銷商達標分析</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 範例查詢
        st.markdown("### 💡 查詢範例")
        example_queries = [
            "請提供5/22 TOYOTA各車種的販賣台數",
            "哪一個據點在 1 月販賣進度最快？",
            "經銷商達標狀況分析",
            "哪個車款販售得最少？"
        ]
        
        for query in example_queries:
            if st.button(f"📝 {query}", key=f"example_{hash(query)}"):
                st.session_state.example_query = query
        
        # 清除聊天記錄
        if st.button("🗑️ 清除聊天記錄"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col1:
        # 顯示聊天歷史
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # 處理範例查詢
        if 'example_query' in st.session_state:
            prompt = st.session_state.example_query
            del st.session_state.example_query
            
            # 添加用戶消息
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # 生成回應
            with st.chat_message("assistant"):
                with st.spinner("正在分析..."):
                    try:
                        # 呼叫您現有的 query_agent 函數（完全不修改）
                        response = query_agent(prompt)
                        
                        # 顯示結果
                        if response and "output" in response:
                            result = response["output"]
                            st.markdown(result)
                            
                            # 顯示 DEBUG 資訊
                            display_debug_info(response, prompt)
                            
                            # 添加助手回應到聊天記錄
                            st.session_state.chat_history.append({"role": "assistant", "content": result})
                        else:
                            error_msg = "❌ 無法取得分析結果"
                            st.error(error_msg)
                            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                            
                    except Exception as e:
                        error_msg = f"❌ 處理查詢時發生錯誤: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
        
        # 用戶輸入
        if prompt := st.chat_input("請輸入您的問題..."):
            # 添加用戶消息
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # 生成回應
            with st.chat_message("assistant"):
                with st.spinner("正在分析..."):
                    try:
                        # 呼叫您現有的 query_agent 函數（完全不修改）
                        response = query_agent(prompt)
                        
                        # 顯示結果
                        if response and "output" in response:
                            result = response["output"]
                            st.markdown(result)
                            
                            # 顯示 DEBUG 資訊
                            display_debug_info(response, prompt)
                            
                            # 添加助手回應到聊天記錄
                            st.session_state.chat_history.append({"role": "assistant", "content": result})
                        else:
                            error_msg = "❌ 無法取得分析結果"
                            st.error(error_msg)
                            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                            
                    except Exception as e:
                        error_msg = f"❌ 處理查詢時發生錯誤: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

# DEBUG INFO 顯示函數
def display_debug_info(response: dict, prompt: str):
    """顯示 LangChain 執行的詳細 DEBUG 資訊"""
    import json
    
    st.markdown("---")
    st.markdown("## **🔍 DEBUG INFO**")
    
    # 1. Tool Invocations (工具調用記錄)
    with st.expander("🔧 Tool Invocations", expanded=False):
        if "intermediate_steps" in response and response["intermediate_steps"]:
            st.markdown("### LangChain 工具調用記錄")
            for i, step in enumerate(response["intermediate_steps"]):
                try:
                    tool_name = step[0].tool
                    tool_input = step[0].tool_input
                    tool_output = step[1]
                    
                    st.markdown(f"**步驟 {i+1}:**")
                    st.code(f"Invoking: {tool_name}", language="text")
                    st.markdown(f"**輸入:** `{tool_input}`")
                    st.markdown("**輸出:**")
                    st.code(str(tool_output), language="text")
                    st.markdown("---")
                except Exception as e:
                    st.error(f"解析步驟 {i+1} 時發生錯誤: {str(e)}")
        else:
            st.info("此次查詢沒有工具調用記錄")
    
    # 2. Python Query (Python 執行查詢)
    with st.expander("🐍 Python Query", expanded=False):
        if "intermediate_steps" in response and response["intermediate_steps"]:
            python_queries = []
            for i, step in enumerate(response["intermediate_steps"]):
                try:
                    tool_name = step[0].tool
                    tool_input = step[0].tool_input
                    
                    # 查找 python_repl_ast 或相關的 Python 執行
                    if "python" in tool_name.lower() or "repl" in tool_name.lower():
                        python_queries.append(f"步驟 {i+1} - {tool_name}:")
                        python_queries.append(str(tool_input))
                        python_queries.append("---")
                    elif isinstance(tool_input, dict) and 'query' in str(tool_input).lower():
                        python_queries.append(f"步驟 {i+1} - {tool_name} 查詢:")
                        python_queries.append(str(tool_input))
                        python_queries.append("---")
                except:
                    continue
            
            if python_queries:
                st.markdown("### Python 執行內容")
                for query in python_queries:
                    if query == "---":
                        st.markdown("---")
                    elif "步驟" in query:
                        st.markdown(f"**{query}**")
                    else:
                        st.code(query, language="python")
            else:
                st.info("此次查詢沒有找到 Python 執行內容")
        else:
            st.info("沒有中間步驟記錄")
    
    # 3. Raw Response (LangChain 原始回傳)
    with st.expander("📄 Raw Response", expanded=False):
        st.markdown("### LangChain 完整原始回應")
        try:
            if isinstance(response, dict):
                st.code(json.dumps(response, indent=2, ensure_ascii=False), language="json")
            else:
                st.code(str(response), language="text")
        except Exception as e:
            st.error(f"顯示原始回應時發生錯誤: {str(e)}")
            st.code(str(response), language="text")
    
    # 4. 額外資訊
    with st.expander("📊 執行統計", expanded=False):
        st.markdown("### 查詢資訊")
        st.markdown(f"**原始查詢:** `{prompt}`")
        
        if hasattr(response, 'get'):
            # 如果有統計資訊
            if 'usage' in response:
                st.json(response['usage'])
            
            # 顯示回應的所有 key
            st.markdown("**回應結構:**")
            st.code(f"回應類型: {type(response)}")
            if isinstance(response, dict):
                st.code(f"回應欄位: {list(response.keys())}")

# 主要應用程式
def main():
    # 頁面導航
    current_page = sidebar_navigation()
    
    # 根據選擇顯示對應頁面
    if current_page == "📤 資料上傳":
        file_upload_page()
    elif current_page == "📊 資料檢視":
        data_view_page()
    elif current_page == "💬 智能問答":
        qa_interface_page()

if __name__ == "__main__":
    main()