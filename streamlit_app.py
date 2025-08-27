import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import io
import os
from datetime import datetime

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
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ff7f0e;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 初始化 session state
def init_session_state():
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = {}
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = []

init_session_state()

# 側邊欄導航
def sidebar_navigation():
    st.sidebar.markdown("## 🚗 HOTAI MOTOR")
    st.sidebar.markdown("### 銷售數據分析平台")
    
    page = st.sidebar.selectbox(
        "選擇功能",
        ["📤 資料上傳", "📊 資料檢視與編輯", "💬 智能問答", "ℹ️ 系統資訊"]
    )
    
    st.sidebar.markdown("---")
    
    # 顯示已上傳檔案
    if st.session_state.uploaded_data:
        st.sidebar.markdown("### 📁 已上傳檔案")
        for filename in st.session_state.uploaded_data.keys():
            st.sidebar.markdown(f"• {filename}")
    
    return page

# 檔案上傳功能
def file_upload_page():
    st.markdown('<div class="main-header">📤 資料上傳</div>', unsafe_allow_html=True)
    
    # 檔案上傳區域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="sub-header">上傳 Excel 或 CSV 檔案</div>', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "選擇檔案",
            type=['xlsx', 'xls', 'csv'],
            accept_multiple_files=True,
            help="支援 Excel (.xlsx, .xls) 和 CSV (.csv) 格式"
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in st.session_state.uploaded_data:
                    try:
                        # 讀取檔案
                        if uploaded_file.name.endswith('.csv'):
                            df = pd.read_csv(uploaded_file)
                            sheets_data = {"Sheet1": df}
                        else:
                            # 讀取 Excel 檔案的所有工作表
                            excel_file = pd.ExcelFile(uploaded_file)
                            sheets_data = {}
                            for sheet_name in excel_file.sheet_names:
                                sheets_data[sheet_name] = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                        
                        # 儲存到 session state
                        st.session_state.uploaded_data[uploaded_file.name] = {
                            'data': sheets_data,
                            'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'file_size': len(uploaded_file.getvalue())
                        }
                        
                        st.success(f"✅ 成功上傳檔案: {uploaded_file.name}")
                        
                    except Exception as e:
                        st.error(f"❌ 檔案上傳失敗: {uploaded_file.name}")
                        st.error(f"錯誤詳情: {str(e)}")
    
    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        **支援格式:**
        - Excel (.xlsx, .xls)
        - CSV (.csv)
        
        **檔案要求:**
        - 檔案大小 < 200MB
        - 包含表頭欄位
        - 資料格式正確
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 顯示已上傳檔案摘要
    if st.session_state.uploaded_data:
        st.markdown("---")
        st.markdown('<div class="sub-header">📋 檔案摘要</div>', unsafe_allow_html=True)
        
        for filename, file_info in st.session_state.uploaded_data.items():
            with st.expander(f"📄 {filename}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**上傳時間:** {file_info['upload_time']}")
                    st.write(f"**檔案大小:** {file_info['file_size']:,} bytes")
                
                with col2:
                    st.write(f"**工作表數量:** {len(file_info['data'])}")
                    for sheet_name, df in file_info['data'].items():
                        st.write(f"• {sheet_name}: {len(df)} 行")
                
                with col3:
                    if st.button(f"🗑️ 刪除", key=f"delete_{filename}"):
                        del st.session_state.uploaded_data[filename]
                        st.rerun()

# 資料檢視與編輯功能
def data_view_edit_page():
    st.markdown('<div class="main-header">📊 資料檢視與編輯</div>', unsafe_allow_html=True)
    
    if not st.session_state.uploaded_data:
        st.warning("⚠️ 請先在「資料上傳」頁面上傳檔案")
        return
    
    # 檔案和工作表選擇
    col1, col2 = st.columns([1, 1])
    
    with col1:
        selected_file = st.selectbox(
            "選擇檔案",
            list(st.session_state.uploaded_data.keys())
        )
    
    with col2:
        if selected_file:
            available_sheets = list(st.session_state.uploaded_data[selected_file]['data'].keys())
            selected_sheet = st.selectbox(
                "選擇工作表",
                available_sheets
            )
    
    if selected_file and selected_sheet:
        df = st.session_state.uploaded_data[selected_file]['data'][selected_sheet].copy()
        st.session_state.current_data = df
        
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
        
        # 資料預覽和編輯
        st.markdown("---")
        
        tabs = st.tabs(["📋 資料預覽", "✏️ 資料編輯", "📈 基本統計", "🔍 資料篩選"])
        
        with tabs[0]:  # 資料預覽
            st.markdown('<div class="sub-header">資料預覽</div>', unsafe_allow_html=True)
            
            # 顯示前幾行
            preview_rows = st.slider("顯示行數", 5, min(50, len(df)), 10)
            st.dataframe(df.head(preview_rows), use_container_width=True)
            
            # 欄位資訊
            st.markdown("### 欄位資訊")
            col_info = pd.DataFrame({
                '欄位名稱': df.columns,
                '資料類型': df.dtypes.astype(str),
                '非空值數量': df.count(),
                '唯一值數量': df.nunique(),
                '範例值': [str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else 'N/A' for col in df.columns]
            })
            st.dataframe(col_info, use_container_width=True)
        
        with tabs[1]:  # 資料編輯
            st.markdown('<div class="sub-header">資料編輯</div>', unsafe_allow_html=True)
            
            # 簡單的資料編輯功能
            if st.checkbox("啟用編輯模式"):
                st.warning("⚠️ 編輯模式：請謹慎修改資料")
                
                # 編輯特定儲存格
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    edit_row = st.number_input("行號 (0開始)", 0, len(df)-1, 0)
                with col2:
                    edit_col = st.selectbox("選擇欄位", df.columns)
                with col3:
                    new_value = st.text_input("新值", value=str(df.iloc[edit_row][edit_col]))
                
                if st.button("更新數值"):
                    try:
                        # 嘗試保持原始資料類型
                        if pd.api.types.is_numeric_dtype(df[edit_col]):
                            df.iloc[edit_row, df.columns.get_loc(edit_col)] = float(new_value)
                        else:
                            df.iloc[edit_row, df.columns.get_loc(edit_col)] = new_value
                        
                        # 更新 session state
                        st.session_state.uploaded_data[selected_file]['data'][selected_sheet] = df
                        st.success("✅ 資料已更新")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 更新失敗: {str(e)}")
                
                # 顯示編輯後的資料預覽
                st.markdown("### 編輯後預覽")
                st.dataframe(df.head(20), use_container_width=True)
        
        with tabs[2]:  # 基本統計
            st.markdown('<div class="sub-header">基本統計</div>', unsafe_allow_html=True)
            
            # 數值欄位統計
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if not numeric_cols.empty:
                st.markdown("#### 數值欄位統計")
                st.dataframe(df[numeric_cols].describe(), use_container_width=True)
            
            # 類別欄位統計
            categorical_cols = df.select_dtypes(include=['object']).columns
            if not categorical_cols.empty:
                st.markdown("#### 類別欄位統計")
                selected_cat_col = st.selectbox("選擇類別欄位", categorical_cols)
                if selected_cat_col:
                    value_counts = df[selected_cat_col].value_counts()
                    st.bar_chart(value_counts)
                    st.write("數值分布:")
                    st.dataframe(value_counts.to_frame(), use_container_width=True)
        
        with tabs[3]:  # 資料篩選
            st.markdown('<div class="sub-header">資料篩選</div>', unsafe_allow_html=True)
            
            # 簡單篩選功能
            filter_col = st.selectbox("選擇篩選欄位", df.columns)
            
            if filter_col:
                col_type = df[filter_col].dtype
                
                if pd.api.types.is_numeric_dtype(df[filter_col]):
                    min_val = float(df[filter_col].min())
                    max_val = float(df[filter_col].max())
                    range_vals = st.slider(
                        f"{filter_col} 範圍",
                        min_val, max_val, (min_val, max_val)
                    )
                    filtered_df = df[(df[filter_col] >= range_vals[0]) & (df[filter_col] <= range_vals[1])]
                else:
                    unique_vals = df[filter_col].unique()
                    selected_vals = st.multiselect(
                        f"選擇 {filter_col} 的值",
                        unique_vals,
                        default=unique_vals[:min(5, len(unique_vals))]
                    )
                    filtered_df = df[df[filter_col].isin(selected_vals)]
                
                st.markdown(f"### 篩選結果 ({len(filtered_df)} 行)")
                st.dataframe(filtered_df, use_container_width=True)
                
                # 下載篩選結果
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 下載篩選結果 (CSV)",
                    data=csv,
                    file_name=f"filtered_{selected_file}_{selected_sheet}.csv",
                    mime="text/csv"
                )

# 智能問答功能
def qa_interface_page():
    st.markdown('<div class="main-header">💬 智能問答</div>', unsafe_allow_html=True)
    
    if not st.session_state.uploaded_data:
        st.warning("⚠️ 請先在「資料上傳」頁面上傳檔案")
        return
    
    # LangChain 設定檢查
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("❌ 未設定 OpenAI API Key。請在 Streamlit Cloud 設定環境變數 OPENAI_API_KEY")
        st.info("💡 如何設定環境變數：App settings → Advanced settings → Secrets")
        return
    
    # 聊天介面
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        **可用功能:**
        - 資料摘要分析
        - 統計計算
        - 趨勢分析
        - 比較分析
        - 自定義查詢
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 清除聊天記錄
        if st.button("🗑️ 清除聊天記錄"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col1:
        # 顯示聊天歷史
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
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
                        # 這裡將整合您的 LangChain 程式碼
                        response = generate_response(prompt)
                        st.markdown(response)
                        
                        # 添加助手回應
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                        
                    except Exception as e:
                        error_msg = f"❌ 處理問題時發生錯誤: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

# 整合 LangChain 的回應生成函數
def generate_response(prompt: str) -> str:
    """
    整合 HOTAI MOTOR LangChain 分析功能的回應生成函數
    """
    try:
        # 匯入 LangChain 整合模組
        from utils.langchain_integration import get_langchain_agent
        
        # 獲取 LangChain agent
        agent = get_langchain_agent()
        
        # 使用 agent 處理查詢
        response = agent.query(prompt)
        
        # 準備回傳結果
        output = response["output"]
        
        # 如果有執行步驟資訊，可以選擇性顯示
        if "steps_summary" in response and response["steps_summary"]:
            output += f"\n\n---\n*{response['steps_summary']}*"
        
        # 如果有成本資訊，可以選擇性顯示
        if response.get("cost", 0) > 0:
            output += f"\n\n💰 *API 成本: ${response['cost']:.4f} | Token: {response.get('tokens', 0)}*"
        
        return output
        
    except ImportError as e:
        return f"❌ LangChain 模組載入失敗: {str(e)}\n\n請確認已安裝所有必要套件。"
    
    except Exception as e:
        # 備用的簡單回應邏輯
        if not st.session_state.uploaded_data:
            return "請先上傳資料檔案，然後再進行問答。"
        
        # 簡化版分析（當 LangChain 不可用時）
        if st.session_state.current_data is not None:
            df = st.session_state.current_data
            
            if "摘要" in prompt or "總結" in prompt:
                return f"""
📊 **資料摘要**
- 總行數: {len(df):,}
- 總欄數: {len(df.columns)}
- 缺失值: {df.isnull().sum().sum()}
- 數值欄位: {len(df.select_dtypes(include=[np.number]).columns)}
- 文字欄位: {len(df.select_dtypes(include=['object']).columns)}

⚠️ 注意: 目前使用簡化版分析功能。完整的 AI 分析需要正確設定 OpenAI API Key。
                """
            
            elif "欄位" in prompt or "columns" in prompt.lower():
                cols_info = "📋 **資料欄位:**\n"
                for i, col in enumerate(df.columns, 1):
                    cols_info += f"{i}. {col} ({df[col].dtype})\n"
                cols_info += "\n⚠️ 注意: 目前使用簡化版功能。"
                return cols_info
        
        return f"❌ 處理查詢時發生錯誤: {str(e)}\n\n請檢查:\n1. OpenAI API Key 是否正確設定\n2. 網路連線是否正常\n3. 上傳的資料格式是否正確"

# 系統資訊頁面
def system_info_page():
    st.markdown('<div class="main-header">ℹ️ 系統資訊</div>', unsafe_allow_html=True)
    
    # 系統狀態
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="sub-header">🔧 系統狀態</div>', unsafe_allow_html=True)
        
        # 環境檢查
        env_status = []
        env_status.append(("Python", "✅" if True else "❌"))
        env_status.append(("Streamlit", "✅" if True else "❌"))
        env_status.append(("Pandas", "✅" if True else "❌"))
        env_status.append(("OpenAI API", "✅" if os.environ.get("OPENAI_API_KEY") else "❌"))
        
        for component, status in env_status:
            st.write(f"{status} {component}")
    
    with col2:
        st.markdown('<div class="sub-header">📊 使用統計</div>', unsafe_allow_html=True)
        st.metric("已上傳檔案", len(st.session_state.uploaded_data))
        st.metric("聊天記錄", len(st.session_state.chat_history))
        
        # 資料使用量統計
        total_rows = sum(
            sum(len(sheet_data) for sheet_data in file_info['data'].values())
            for file_info in st.session_state.uploaded_data.values()
        )
        st.metric("總資料行數", f"{total_rows:,}")
    
    st.markdown("---")
    
    # 功能說明
    st.markdown('<div class="sub-header">📖 功能說明</div>', unsafe_allow_html=True)
    
    features = {
        "📤 資料上傳": "支援 Excel 和 CSV 檔案上傳，自動解析多個工作表",
        "📊 資料檢視與編輯": "提供資料預覽、基本編輯、統計分析和篩選功能",
        "💬 智能問答": "整合 LangChain 和 OpenAI，提供自然語言數據分析",
        "🔧 部署支援": "完全支援 Streamlit Cloud 部署，包含環境變數管理"
    }
    
    for feature, description in features.items():
        st.write(f"**{feature}**: {description}")
    
    st.markdown("---")
    
    # 版本資訊
    st.markdown('<div class="sub-header">🔖 版本資訊</div>', unsafe_allow_html=True)
    st.write("• **版本**: 1.0.0")
    st.write("• **更新日期**: 2025-08-26")
    st.write("• **支援**: HOTAI MOTOR 銷售數據分析")

# 主要應用程式
def main():
    # 頁面導航
    current_page = sidebar_navigation()
    
    # 根據選擇顯示對應頁面
    if current_page == "📤 資料上傳":
        file_upload_page()
    elif current_page == "📊 資料檢視與編輯":
        data_view_edit_page()
    elif current_page == "💬 智能問答":
        qa_interface_page()
    elif current_page == "ℹ️ 系統資訊":
        system_info_page()

if __name__ == "__main__":
    main()