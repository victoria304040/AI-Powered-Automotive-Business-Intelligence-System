"""
LangChain 整合模組
完整複製 solution_combine.py 的 LangChain 實現到 Streamlit 應用
"""
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import streamlit as st
from .hotai_tools import get_all_tools, generate_mapping_text, BusinessCalculator, dataframes

# LangChain imports
try:
    from langchain_openai import ChatOpenAI
    from langchain.tools import tool
    from langchain.agents import AgentExecutor, create_openai_functions_agent
    from langchain.prompts import ChatPromptTemplate
    from langchain.tools.render import format_tool_to_openai_function
    from langchain.callbacks import get_openai_callback
    from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class StreamlitLangChainAgent:
    """Streamlit 整合的 LangChain Agent - 基於 solution_combine.py"""
    
    def __init__(self):
        self.llm = None
        self.agent_executor = None
        self.tools = []
        self.mapping_text = ""
        self.setup_agent()
    
    def setup_agent(self):
        """設置 LangChain Agent"""
        if not LANGCHAIN_AVAILABLE:
            st.error("❌ LangChain 套件未安裝，請檢查 requirements.txt")
            return
        
        # 檢查 API 金鑰
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            st.warning("⚠️ OpenAI API Key 未設定，無法使用 AI 問答功能")
            return
        
        try:
            # 初始化語言模型（與原程式保持一致）
            self.llm = ChatOpenAI(temperature=0, model="gpt-4.1")
            
            # 載入映射表（如果存在）
            self.load_mapping_data()
            
            # 設置工具
            self.setup_tools()
            
            # 創建 Agent
            if self.tools:
                self.create_agent()
                
        except Exception as e:
            st.error(f"❌ LangChain Agent 初始化失敗: {str(e)}")
    
    def load_mapping_data(self):
        """載入映射表資料"""
        try:
            # 檢查是否有映射表檔案
            mapping_files = ["Mapping Dataframe.xlsx", "mapping.xlsx", "經銷商對應表.xlsx"]
            for filename in mapping_files:
                if hasattr(st.session_state, 'uploaded_data') and filename in st.session_state.uploaded_data:
                    self.mapping_text = generate_mapping_text(filename)
                    break
            
            if not self.mapping_text:
                self.mapping_text = "映射表資料未載入，經銷商名稱查詢可能受限。"
        except Exception as e:
            self.mapping_text = f"映射表載入失敗: {str(e)}"
    
    def setup_tools(self):
        """設置分析工具 - 使用完整的 HOTAI 工具集"""
        # 取得所有 HOTAI 工具
        self.tools = get_all_tools()
        
        # 新增額外的業務計算工具
        @tool
        def calculate_business_metrics(metric_type: str, actual: float = 0, target: float = 1, 
                                     current: float = 0, previous: float = 1) -> str:
            """計算 HOTAI MOTOR 業務指標"""
            calc = BusinessCalculator()
            try:
                if metric_type in ["達成率", "achievement_rate"]:
                    rate = calc.calculate_achievement_rate(actual, target)
                    return f"達成率: {rate:.1f}% (實績 {actual} / 目標 {target})"
                elif metric_type in ["去年比", "yoy_growth"]:
                    growth = calc.calculate_yoy_growth(current, previous)
                    return f"去年比: {growth:.1f}% (今年 {current} / 去年 {previous})"
                elif metric_type in ["前月比", "mom_growth"]:
                    growth = calc.calculate_mom_growth(current, previous)
                    return f"前月比: {growth:.1f}% (本月 {current} / 上月 {previous})"
                elif metric_type in ["推進率", "progress_rate"]:
                    rate = calc.calculate_progress_rate(actual, target)
                    return f"推進率: {rate:.1f}% (目前 {actual} / 目標 {target})"
                else:
                    return f"不支援的指標類型: {metric_type}。支援的類型: 達成率, 去年比, 前月比, 推進率"
            except Exception as e:
                return f"指標計算失敗: {str(e)}"
        
        @tool
        def get_system_status() -> str:
            """取得系統狀態資訊"""
            status_info = []
            status_info.append(f"📊 已載入資料集: {len(dataframes)}")
            
            if hasattr(st.session_state, 'uploaded_data'):
                status_info.append(f"📁 已上傳檔案: {len(st.session_state.uploaded_data)}")
                for filename, file_info in st.session_state.uploaded_data.items():
                    sheet_count = len(file_info['data'])
                    total_rows = sum(len(df) for df in file_info['data'].values())
                    status_info.append(f"  • {filename}: {sheet_count} 工作表, {total_rows:,} 行")
            
            status_info.append(f"🔧 映射表狀態: {'已載入' if self.mapping_text and '失敗' not in self.mapping_text else '未載入'}")
            
            return "\n".join(status_info)
        
        # 加入額外工具
        self.tools.extend([calculate_business_metrics, get_system_status])
    
    def create_agent(self):
        """創建 LangChain Agent - 使用 solution_combine.py 的完整原始 system_message"""
        # 完整複製 solution_combine.py 中的 system_message
        system_message = f"""你是一個資料分析助理，能同時處理兩大類任務──「一般性資料探索與分析」以及「目標 vs. 實際 銷售達標比對」。請依照使用者問題，自動判斷並執行最合適的流程。

  # 運算與名詞定義
  **常見運算定義：**
  1. **去年比** = 今年實績台數 / 去年實績台數 × 100%  
     例：2024年3月100台，2025年3月150台 → 150/100×100%=150%
  2. **前月比** = 本月實績台數 / 上月實績台數 × 100%  
     例：2025年2月150台，2025年3月100台 → 100/150×100%=66.7%
  3. **去年同期比** = 今年同期台數 / 去年同期台數 × 100%  
     例：2024/3/1–25合計100台，2025/3/1–25合計150台 → 150/100×100%=150%
  4. **前月同期比** = 本月同期台數 / 上月同期台數 × 100%  
     例：2025/2/1–25合計150台，2025/3/1–25合計100台 → 100/150×100%=66.7%
  5. **推進率** = 實績台數 / 目標台數 × 100%（用於當月中進度）  
     例：5月目標100台，至今已賣89台 → 89/100×100%=89%
  6. **達成率** = 實績台數 / 目標台數 × 100%（用於已結束月份）  
     例：3月目標100台，實績92台 → 92/100×100%=92%
  7. **累計台數**：若無特別說明時間，預設為當年1/1至指定時間之累計。

  **常見名詞定義：**
  - **C CROSS** 簡稱 **CC**  
  - **Y CROSS** 簡稱 **YC**  
  - **HV** 與 **HEV** 同義，均指油電車  
  - **據點** = **營業所**  
  - **大盤** = **全體進度**
  - **代號** = **代碼**

  ## Excel 欄位說明
  - **經銷商目標 Excel**  
    - 檔名模式：`目標_YYYY上半年.xlsx`，sheet 名稱同  
    - 目標種類欄位：`目標種類`，其中 `1`＝受訂、`2`＝販賣  
    - 目標值欄位：`X月目標`、`Y月目標`… 或通用欄位 `目標數`
  - **MBIS 實績 Excel**  
    - 檔名模式：`實績_YYYY上半年.xlsx`，sheet 名稱同  
    - 實績種類欄位：`實績種類`，其中 `27`＝受訂、`3D`＝販賣  
    - 實績值欄位：`受訂數`（受訂）或 `銷售數`（販賣）  
    - **使用時統一稱作** `台數`，代表對應的實績值

## 欄位型態處理
```python
# 1. 日期欄位（DATE 型態）：強制轉為 datetime
df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
# 篩選時可用 Timestamp 或 dt.date 比對
filtered = df[df['日期'] == pd.Timestamp('2025-05-22')]
# 或者：
filtered = df[df['日期'].dt.date == pd.to_datetime('2025-05-22').date()]

# 字串型態比對強制規則
- 對於任何 CHAR(2) 類型的欄位（如 `實績種類`），**模型產生的程式碼**必須：
  1. 先執行 `df['實績種類'] = df['實績種類'].astype(str).str.strip()` 清理；
  2. **比對條件必須**使用字串形式，例如：
     ```python
     filtered = df[
         (df['實績種類'] == '27')   # 正確：用字串 '27'
     ]
     ```
  3. **絕對不得**寫成 `(df['實績種類'] == 27)` 或其他非字串方式。

# 一般性資料探索與分析流程
- 適用情境：使用者詢問排行（最慢／最快 N 項）、時間切片（如 1 月、Q2、最近三個月）、熱門項目、敘述性統計等。
- 工具順序：
  1. list_files()
  2. read_excel_head(filename, sheet_name, n_rows)
  3. read_excel_file(filename, sheet_name)
  4. analyze_dataframe(query)
- 共通規則：
  - 時間篩選必先檢查 datetime，若未轉型則執行上述「欄位型態處理」中的日期轉型步驟。
  - 強制 groupby：任何涉及統計、排行、計數或達標分析，模型必須先辨識「問題中提及的所有關鍵維度欄位」，並對這些欄位一起呼叫 `groupby(...)` 再做聚合；絕不可直接在原始 df 上用 `idxmax()`/`idxmin()` 或只對單一欄位做 groupby。
  - 保留原始值：排行需求須保留所有原始數值（含 -1、0），並同時 groupby 代碼與名稱，例如：
    ```python
    # 範例：1 月據點排行最快
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    jan = df[df['日期'].dt.month == 1]
    summary = jan.groupby(['據點代碼','據點'])['台數'].sum().reset_index()
    top_point = summary.loc[summary['台數'].idxmax()]
    ```
    請直接回傳 `summary` DataFrame 中的完整行，而非只回 tuple(key,value)。
  - 分層排行：
    1. 第一層級 groupby + sum → 找出目標分組
    2. 篩選該分組所有記錄
    3. 第二層級 groupby + sum → 排序取前 N



# 目標 vs. 實際 銷售達標比對流程
- 適用情境：使用者詢問「經銷商／營業所達標狀況」、「經銷商／營業所達標數」、「目標 vs. 實際 差異分析」等。
- 工具順序：
  1. list_and_classify_files()
  2. load_excel_file(filename)
  3. classify_file_type(filename)
  4. compare_target_vs_actual(target_key, actual_key)
- 共通規則：
  - 多 sheet 檔案由 load_excel_file 一次讀入所有 sheet，存於 dataframes["filename::sheet"]。
  - compare_target_vs_actual 執行後須把合併結果寫回 dataframes，並由工具輸出 summary 與 detail。
  - 所有數字結果必須從合併後的表格內容衍生，禁止憑空或二次計算。

# 回答要求
- 請先回報「已選擇：A. 一般分析流程」或「已選擇：B. 目標 vs. 實際流程」。
- 當使用者詢問「某經銷商達標數量」時：
    1. 先呼叫 compare_target_vs_actual(target_key, actual_key) 取得 merged_key。
    2. 再呼叫 summarize_performance_summary(merged_key, dealer_name) 取得該經銷商的 summary。
    3. 最終回傳的「總筆數／達標筆數／達標率」都取自 summarize_performance_summary 的結果，
        不可再次自行計算。
- 不須顯示關鍵 pandas 程式碼片段與運行結果。
- 最終回傳清晰的 Markdown 表格，以及**必須**使用 compare_target_vs_actual 回傳的 `summary` 欄位來填充「總筆數／達標筆數／達標率」，不允許模型另行計算。
- 若資料不足或欄位不符，請明確提出並請求補充。
- 若使用者輸入的是經銷商名稱與營業所名稱，請參照下列對應資訊查找對應的代碼：{self.mapping_text}
- **若結果只回傳了某個代碼（如據點代碼），務必再到原始 DataFrame 中以該代碼為 key，抓出對應的「據點名稱」或「營業所」欄位，一併回覆**。
- 在group by 代碼的時候，必須連同名稱一併納入再叫group by。
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", "{input}"),
            ("ai", "{agent_scratchpad}")
        ])
        
        try:
            # 轉換工具為 OpenAI Functions 格式（與原程式相同）
            functions = [format_tool_to_openai_function(tool) for tool in self.tools]
            
            # 創建 agent（使用與原程式相同的配置）
            agent = create_openai_functions_agent(self.llm, self.tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,  # 與原程式保持一致
                handle_parsing_errors=True
            )
            
        except Exception as e:
            st.error(f"Agent 創建失敗: {str(e)}")
    
    def query(self, question: str) -> Dict[str, Any]:
        """查詢 Agent - 修復版本適配現代 LangChain API"""
        if not self.agent_executor:
            return {
                "output": "❌ AI 助理未正確初始化，請檢查 OpenAI API Key 設定",
                "error": True,
                "cost": 0,
                "tokens": 0
            }
        
        try:
            with get_openai_callback() as cb:
                # 修復：使用正確的 LangChain API 調用方式
                response = self.agent_executor.invoke({"input": question})
            
            # 處理回應格式 - 支援多種可能的回應結構
            output_text = ""
            
            if isinstance(response, dict):
                # 標準字典回應 - 優先查找 output 欄位
                if "output" in response:
                    output_text = str(response["output"])
                elif "result" in response:
                    output_text = str(response["result"])  
                elif "answer" in response:
                    output_text = str(response["answer"])
                else:
                    # 如果沒有標準欄位，嘗試找到最相關的內容
                    possible_keys = ['text', 'content', 'response', 'message']
                    for key in possible_keys:
                        if key in response:
                            output_text = str(response[key])
                            break
                    
                    # 如果還是沒找到，將整個回應轉為字符串
                    if not output_text:
                        output_text = str(response)
            else:
                # 直接字符串回應
                output_text = str(response)
            
            # 準備回傳結果
            result = {
                "output": output_text,
                "cost": cb.total_cost,
                "tokens": cb.total_tokens,
                "successful_requests": cb.successful_requests,
                "error": False,
                "raw_response": response  # 保留原始回應用於 DEBUG
            }
            
            # 檢查是否有中間步驟資訊
            if isinstance(response, dict) and "intermediate_steps" in response:
                steps = response["intermediate_steps"]
                if steps and len(steps) > 0:
                    steps_info = []
                    for i, step in enumerate(steps):
                        try:
                            # 安全地提取步驟資訊
                            tool_name = getattr(step[0], 'tool', 'unknown_tool') if hasattr(step[0], 'tool') else 'step'
                            steps_info.append(f"步驟 {i+1}: {tool_name}")
                        except (AttributeError, IndexError):
                            steps_info.append(f"步驟 {i+1}: 處理中")
                    
                    result["steps_summary"] = f"執行了 {len(steps)} 個步驟: {', '.join(steps_info)}"
                else:
                    result["steps_summary"] = "完成單步處理"
            
            return result
            
        except Exception as e:
            error_msg = f"❌ 處理問題時發生錯誤: {str(e)}"
            
            # 提供更詳細的錯誤診斷
            if "API" in str(e).upper():
                error_msg += "\n\n可能原因：OpenAI API 問題，請檢查 API Key 和網路連線。"
            elif "tool" in str(e).lower():
                error_msg += "\n\n可能原因：分析工具執行錯誤，請檢查資料格式。"
            elif "parse" in str(e).lower():
                error_msg += "\n\n可能原因：回應解析錯誤，請簡化問題重新提問。"
            
            return {
                "output": error_msg,
                "error": True,
                "cost": 0,
                "tokens": 0,
                "raw_error": str(e)  # 保留原始錯誤用於 DEBUG
            }
    
    # 輔助分析方法（與原程式保持一致）
    def generate_summary(self, df: pd.DataFrame) -> str:
        """生成資料摘要"""
        summary = f"""
        📊 **資料摘要**
        - 總行數: {len(df):,}
        - 總欄數: {len(df.columns)}
        - 缺失值: {df.isnull().sum().sum():,}
        - 重複行: {df.duplicated().sum():,}
        - 數值欄位: {len(df.select_dtypes(include=['number']).columns)}
        - 文字欄位: {len(df.select_dtypes(include=['object']).columns)}
        - 記憶體使用: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB
        """
        return summary
    
    def generate_statistics(self, df: pd.DataFrame) -> str:
        """生成統計資訊"""
        numeric_df = df.select_dtypes(include=['number'])
        if numeric_df.empty:
            return "此資料集沒有數值欄位可進行統計分析"
        
        stats = numeric_df.describe()
        result = "📈 **數值欄位統計**\n\n"
        for col in stats.columns:
            result += f"**{col}**\n"
            result += f"  - 平均值: {stats.loc['mean', col]:.2f}\n"
            result += f"  - 標準差: {stats.loc['std', col]:.2f}\n"
            result += f"  - 最小值: {stats.loc['min', col]:.2f}\n"
            result += f"  - 最大值: {stats.loc['max', col]:.2f}\n\n"
        
        return result
    
    def list_columns(self, df: pd.DataFrame) -> str:
        """列出欄位資訊"""
        result = "📋 **資料欄位資訊**\n\n"
        for i, col in enumerate(df.columns, 1):
            dtype = str(df[col].dtype)
            non_null = df[col].count()
            unique = df[col].nunique()
            result += f"{i}. **{col}** ({dtype})\n"
            result += f"   - 非空值: {non_null:,}\n"
            result += f"   - 唯一值: {unique:,}\n\n"
        return result
    
    def analyze_missing_values(self, df: pd.DataFrame) -> str:
        """分析缺失值"""
        missing = df.isnull().sum()
        missing = missing[missing > 0].sort_values(ascending=False)
        
        if missing.empty:
            return "✅ 此資料集沒有缺失值"
        
        result = "🔍 **缺失值分析**\n\n"
        total_rows = len(df)
        
        for col, count in missing.items():
            percentage = (count / total_rows) * 100
            result += f"• **{col}**: {count:,} 個缺失值 ({percentage:.1f}%)\n"
        
        return result
    
    def general_analysis(self, df: pd.DataFrame, query: str) -> str:
        """一般性分析"""
        return f"收到查詢: 「{query}」\n\n目前資料包含 {len(df):,} 行 {len(df.columns)} 欄的資料。\n\n如需具體分析，請提供更明確的問題，例如:\n• 「顯示資料摘要」\n• 「計算統計資訊」\n• 「分析缺失值」"


# 全域 agent 實例
@st.cache_resource
def get_langchain_agent():
    """獲取快取的 LangChain Agent"""
    return StreamlitLangChainAgent()


def integrate_existing_tools():
    """
    整合現有的 solution_combine.py 工具
    這個函數可以用來導入和整合現有的分析工具
    """
    try:
        # 嘗試導入現有模組
        # 這裡可以根據實際需求修改導入路徑
        pass
    except ImportError as e:
        st.warning(f"無法導入現有分析工具: {str(e)}")
        return None


# 工具函數
def format_response(response: str) -> str:
    """格式化回應文字"""
    # 可以在這裡加入更多格式化邏輯
    return response


def validate_question(question: str) -> bool:
    """驗證問題格式"""
    if not question or len(question.strip()) < 3:
        return False
    return True