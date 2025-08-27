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

print("當前工作目錄是：", os.getcwd())

# 確保 API 金鑰已設定
if not os.environ.get("OPENAI_API_KEY"):
    with open("secret_key", "r", encoding="utf-8") as f:
        os.environ["OPENAI_API_KEY"] = f.read().strip()

# 建立基本的語言模型
llm = ChatOpenAI(temperature=0, model="gpt-4o-2024-11-20")


# 定義自訂工具函數
@tool
def list_files(file_extension: str = "xlsx") -> List[str]:
    """列出目前目錄下所有指定副檔名的檔案"""
    files = glob.glob(f"*.{file_extension}")
    return files


@tool
def read_excel_head(filename: str, sheet_name: Optional[str] = None, n_rows: int = 5) -> Dict:
    """預覽 Excel 檔案的表頭和前幾筆資料"""
    try:
        if sheet_name:
            df = pd.read_excel(filename, sheet_name=sheet_name, nrows=n_rows)
        else:
            df = pd.read_excel(filename, nrows=n_rows)

        # 取得欄位名稱並返回欄位資訊和範例資料
        columns = df.columns.tolist()
        sample_data = df.head(n_rows).to_dict(orient='records')
        return {
            "filename": filename,
            "sheet_name": sheet_name,
            "columns": columns,
            "sample_data": sample_data
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def read_excel_file(filename: str, sheet_name: Optional[str] = None) -> str:
    """完整讀取指定的 Excel 檔案，並返回資料集的摘要資訊"""
    try:
        if sheet_name:
            df = pd.read_excel(filename, sheet_name=sheet_name)
        else:
            df = pd.read_excel(filename)

        # 清理資料：去除字串欄位的前後空白
        df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

        # 2. 強制轉換「日期」欄位為 datetime
        if "日期" in df.columns:
            df["日期"] = pd.to_datetime(df["日期"], errors="coerce")

        # 3. 強制轉換「實績種類」欄位為乾淨字串
        if "實績種類" in df.columns:
            df["實績種類"] = df["實績種類"].astype(str).str.strip()

        # 將 DataFrame 保存為全域變數
        globals()['current_df'] = df

        # 返回資訊摘要
        info = {
            "filename": filename,
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "has_null": df.isnull().any().to_dict(),
            "sample": df.head(3).to_dict(orient='records')
        }
        return f"已載入 {filename}，資料列數: {df.shape[0]}，欄位數: {df.shape[1]}。可透過 current_df 存取。"
    except Exception as e:
        return f"錯誤: {str(e)}"


@tool
def analyze_dataframe(query: str) -> str:
    """使用 Pandas Agent 分析當前的資料框架，根據使用者的自然語言查詢執行操作"""
    if 'current_df' not in globals():
        return "尚未載入任何資料集，請先使用 read_excel_file 載入資料。"

    try:
        # 使用修改過的系統訊息建立 Pandas Agent，但使用標準的 create_pandas_dataframe_agent 方法
        from langchain_experimental.agents import create_pandas_dataframe_agent
        from langchain_openai import ChatOpenAI

        custom_llm = ChatOpenAI(
            temperature=0,
            model="gpt-4o-2024-11-20"
        ) # 系統訊息已經寫在prompt了 這邊就不需要再寫 model_kwargs

        df_agent = create_pandas_dataframe_agent(
            custom_llm,
            globals()['current_df'],
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            allow_dangerous_code=True
        )

        # 執行查詢
        result = df_agent.run(query)
        return result
    except Exception as e:
        return f"分析時發生錯誤: {str(e)}\n\n錯誤詳情: {type(e).__name__}"


# 集成所有工具
tools = [list_files, read_excel_head, read_excel_file, analyze_dataframe]

# 建立系統訊息  # v0516_日期的prompt還要再調整，有時候會答錯
system_message = """
你是一個資料分析助理。使用者會問你關於資料的銷售進度、熱門項目、排行等問題。
當你處理這些問題時，請遵守以下邏輯：
1. 若若問題中提及時間篩選（如「1月」、「Q2」、「最近三個月」、「上週」等）：
    1-1. 必須先檢查涉及的欄位是否為 datetime 型別。
    1-2. 若不是 datetime，**必須執行** `pd.to_datetime(欄位, errors="coerce")`，並覆寫該欄位。
    1-3. 執行轉換後，**必須檢查是否成功**（例如使用 `df[欄位].isna().sum()` 確認 NaT 數量）。
    1-4. 僅在確認欄位為 datetime 格式後，才可使用 `.dt` 相關操作（如 `.dt.month`、`.dt.quarter`）。
2. 請列出你的推理與處理步驟，避免直接跳過關鍵步驟（如篩選、groupby）
3. 優先使用 pandas 的 groupby / sort / filter 工具來做正確統計與排序。
4. 若使用者詢問「最慢的 N 項」「最快的 N 項」「排行前 N」等需求：
    4-1. 4-1. **不得**先排除任何數值 —— 包括負值 (`-1`) 和 0，所有原始數字都必須參與分析。
    4-2. 先對所需維度（如「車名」、「SFX」）執行 `groupby(...).sum()`，再使用 `.sort_values(目標欄位)` 排序，並用 `.head(N)`（或 `.tail(N)`）取結果。
    4-3. 確保最終回傳的表格即為排序後前 N 筆，並以此表格內容直接得出排名結果。
    4-4. 若需「先按第一層級聚合選定，再於該分組內做第二層級排行」：
        - 對 第一層級 欄位做 groupby+sum，找出目標分組（如總和最少/最多）。
        - 篩選出該分組的所有原始記錄。
        - 對 第二層級 欄位做 groupby+sum，並排序取前 N。
按此流程即可套用到任何「分層聚合再排行」的需求。
5. 若資料未提供時間欄位，請回覆「無法進行時間篩選，需補充欄位資訊」。
6. 執行分析時，請務必提供正確的處理步驟與 pandas 程式碼，以便正確使用 analyze_dataframe() 工具。程式碼執行後，僅需回傳關鍵結果與名稱資訊即可。若為多項目比較，請以簡單表格形式呈現，不需額外說明推論過程。
7. 在分析銷售進度或速度時，僅依據現有銷售記錄進行統計計算，不需參考目標檔案，也不需與其他資料合併。若用戶未明確要求對照目標進度，請避免引用或推論任何「目標值」。
8. 若使用者詢問「總銷售數最少的經銷商」或類似排名問題：
    8-1. **必須**先從所有載入的工作表中，使用 `pd.concat` 合併成一個完整的 DataFrame：
        ```python
       sheet_keys = [k for k in dataframes if k.startswith(file_prefix)]
       df_all = pd.concat([dataframes[k] for k in sheet_keys], ignore_index=True)
        ```
    8-2. **務必**將 `銷售數` 轉為數值型態，但不填補或排除任何原始值：
       ```python
       df_all["銷售數"] = pd.to_numeric(df_all["銷售數"], errors="coerce")
       ```
    8-3. 在未對資料做其他過濾的情況下，執行：
       ```python
       dealer_sales = df_all.groupby("經銷商")["銷售數"].sum()
       ```
    8-4. 最後以 `dealer_sales.idxmin()` 或 `dealer_sales.sort_values().head(1)` 判斷最少的經銷商，並回傳該經銷商名稱與其對應的銷售總和。

此外，請遵循以下步驟處理使用者的資料分析需求：
1. 使用 list_files() 工具確認可用的檔案
2. 分析使用者的問題，確定關鍵字和目標欄位
3. 使用 read_excel_head() 工具預覽相關檔案的表頭，了解欄位結構
4. 根據欄位名稱，判斷哪個檔案最可能包含所需資料
5. 使用 read_excel_file() 工具載入選擇的檔案
6. 使用 analyze_dataframe() 工具執行資料分析任務
7. 提供清晰的答案和分析結果

請確保解釋你的分析過程和結果，讓使用者了解你是如何處理資料的。
"""





# 創建 OpenAI Functions Agent
prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("human", "{input}"),
    ("ai", "{agent_scratchpad}")
    # LangChain 的 Agent 系統預期你的 PromptTemplate 裡會有一個叫 agent_scratchpad 的變數，
    # 用來記錄 Agent 歷史的 intermediate steps（例如工具調用記錄、思考過程等）。
    # 當你建立自定義 Prompt 且漏掉這個變數時，AgentExecutor 就無法正常運作。
])

# 將工具函數轉換為 OpenAI Functions 格式
functions = [format_tool_to_openai_function(t) for t in tools]

# 建立 Agent
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

from langchain.callbacks import get_openai_callback


# 測試 Agent
def query_agent(question: str) -> None:
    """向 Agent 提問並顯示結果"""
    print(f"問題: {question}")
    print("\n正在處理...\n")

    # 使用 get_openai_callback 來捕獲詳細的執行過程
    with get_openai_callback() as cb:
        response = agent_executor.invoke(
            {"input": question},
            return_intermediate_steps=True,  # 確保返回中間步驟
            include_run_info=True  # 包含運行信息
        )

    print("\n回答:")
    print(response["output"])

    # 顯示執行日誌
    if "intermediate_steps" in response:
        print("\n執行過程:")
        for i, step in enumerate(response["intermediate_steps"]):
            tool = step[0].tool
            tool_input = step[0].tool_input
            tool_output = step[1]

            print(f"\n步驟 {i + 1}:")
            print(f"工具: `{tool}`")
            print(f"輸入: `{tool_input}`")
            print(f"輸出: {tool_output}")
            print("-" * 50)

    # 如果使用了 analyze_dataframe，嘗試捕獲其內部 Pandas 操作
    if any(step[0].tool == "analyze_dataframe" for step in response.get("intermediate_steps", [])):
        print("\nPandas 操作詳情將在執行過程中顯示。")

    print(f"\n執行統計:")
    print(f"總令牌使用: {cb.total_tokens} 令牌")
    print(f"總花費: ${cb.total_cost:.6f}")
    print(f"成功調用次數: {cb.successful_requests}")

    return response


# 使用範例 - 直接執行

# result = query_agent("哪一個營業所 1 月販賣進度最快？")

if __name__ == "__main__":
    user_input = "哪一個據點在 1 月販賣進度最快？"

    with get_openai_callback() as cb:
        response = agent_executor.invoke({"input": user_input})

    print("🧾 分析結果：")
    print(response["output"])