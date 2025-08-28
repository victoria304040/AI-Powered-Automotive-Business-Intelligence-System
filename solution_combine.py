import os
import pandas as pd
import glob
from typing import List, Dict, Any, Optional
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage
from langchain.tools.render import format_tool_to_openai_function
from langchain.callbacks import get_openai_callback
from solution1 import list_files, read_excel_head, read_excel_file, analyze_dataframe
from solution3 import list_and_classify_files, load_excel_file, classify_file_type, compare_target_vs_actual, generate_mapping_text

# 確保 API 金鑰已設定
if not os.environ.get("OPENAI_API_KEY"):
    with open("secret_key", "r", encoding="utf-8") as f:
        os.environ["OPENAI_API_KEY"] = f.read().strip()

# 建立基本的語言模型
llm = ChatOpenAI(temperature=0, model="gpt-4.1")

# 全域字典儲存多個 DataFrame
dataframes = {}

# 新增映射表查詢工具
@tool
def get_dealer_mapping(query_code: str) -> str:
    """查詢經銷商或營業所的映射資訊
    
    Args:
        query_code: 要查詢的代碼，可以是經銷商代碼或營業所代碼
        
    Returns:
        str: 對應的映射資訊，包含經銷商名稱和營業所名稱
    """
    try:
        import pandas as pd
        df = pd.read_excel("Mapping Dataframe.xlsx", dtype=str)
        
        # 清理查詢代碼
        query_code = str(query_code).strip()
        
        # 搜尋代碼 - 同時搜尋經銷商代碼和營業所代碼
        dealer_match = df[df['經銷商代碼'].str.strip() == query_code]
        site_match = df[df['營業所代碼'].str.strip() == query_code]
        
        results = []
        
        if len(dealer_match) > 0:
            # 找到經銷商代碼匹配
            for _, row in dealer_match.iterrows():
                dealer_name = row['經銷商名稱'].strip()
                site_name = row['營業所名稱'].strip() 
                site_code = row['營業所代碼'].strip()
                results.append(f"經銷商 {query_code} ({dealer_name}) - 營業所 {site_code} ({site_name})")
        
        if len(site_match) > 0:
            # 找到營業所代碼匹配
            for _, row in site_match.iterrows():
                dealer_name = row['經銷商名稱'].strip()
                dealer_code = row['經銷商代碼'].strip()
                site_name = row['營業所名稱'].strip()
                results.append(f"營業所 {query_code} ({site_name}) - 屬於經銷商 {dealer_code} ({dealer_name})")
        
        if results:
            return "找到以下映射資訊:\n" + "\n".join(results)
        else:
            return f"找不到代碼 '{query_code}' 的對應資訊。請確認代碼是否正確。"
            
    except Exception as e:
        return f"查詢映射資料時發生錯誤: {str(e)}"

# 工具集合
tools = [
    list_files,
    read_excel_head,
    read_excel_file,
    analyze_dataframe,
    list_and_classify_files,
    load_excel_file,
    classify_file_type,
    compare_target_vs_actual,
    get_dealer_mapping,  # 新增映射表查詢工具
]

# 映射表處理
mapping_text = generate_mapping_text("Mapping Dataframe.xlsx")


system_message = f"""
你是一個資料分析助理，能同時處理兩大類任務──「一般性資料探索與分析」以及「目標 vs. 實際 銷售達標比對」。請依照使用者問題，自動判斷並執行最合適的流程。

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
- 若使用者輸入的是經銷商名稱與營業所名稱，請參照下列對應資訊查找對應的代碼：{mapping_text}
- **若結果只回傳了某個代碼（如據點代碼），務必再到原始 DataFrame 中以該代碼為 key，抓出對應的「據點名稱」或「營業所」欄位，一併回覆**。
- 在group by 代碼的時候，必須連同名稱一並納入再去group by。
"""


# 1. 建立 PromptTemplate（共用於兩種流程）
prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("human", "{input}"),
    ("ai", "{agent_scratchpad}")
])

# 2. 轉換所有工具為 OpenAI Functions 格式
functions = [format_tool_to_openai_function(t) for t in tools]

# 3. 建立 AgentExecutor
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# 4. 定義 query_agent 函式，供互動與除錯使用
def query_agent(question: str) -> dict:
    """向 Agent 提問並顯示中間步驟與結果"""
    print(f"問題: {question}\n正在處理...\n")
    with get_openai_callback() as cb:
        response = agent_executor.invoke(
            {"input": question},
            return_intermediate_steps=True,
            include_run_info=True
        )
    # 輸出回答
    print("回答:")
    print(response["output"])
    # 輸出中間步驟
    if "intermediate_steps" in response:
        print("\n執行過程:")
        for i, step in enumerate(response["intermediate_steps"]):
            tool_name = step[0].tool
            tool_input = step[0].tool_input
            tool_output = step[1]
            print(f"步驟 {i+1}: 工具=`{tool_name}` 輸入={tool_input} 輸出={tool_output}")
    # 輸出使用統計
    print(f"\n總令牌: {cb.total_tokens}  總花費: ${cb.total_cost:.6f}  請求次數: {cb.successful_requests}")
    return response

# 5. 範例：在 __main__ 中呼叫 query_agent
if __name__ == "__main__":
    user_input = "請提供5/22 TOYOTA各車種的販賣台數"
    response = query_agent(user_input)