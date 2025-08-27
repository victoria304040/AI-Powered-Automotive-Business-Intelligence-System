import os
import pandas as pd
import glob
from typing import List, Dict, Any, Optional
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain.tools.render import format_tool_to_openai_function

print("當前工作目錄：", os.getcwd())
print("該目錄下的 Excel 檔案列表：", glob.glob("*.xlsx"))


# ==================================== 1. 設定 ====================================
# 確保 API 金鑰已設定
if not os.environ.get("OPENAI_API_KEY"):
    with open("secret_key", "r", encoding="utf-8") as f:
        os.environ["OPENAI_API_KEY"] = f.read().strip()

llm = ChatOpenAI(temperature=0, model="gpt-4o-2024-11-20")

# 全域字典儲存多個 DataFrame
dataframes = {}


# ==================================== 2. 定義自訂工具函數 ====================================
@tool
def list_and_classify_files(file_extension: str = "xlsx") -> Dict[str, List[str]]:
    """
    回傳分類後的檔案列表：target / actual / unknown
    """
    files = glob.glob(f"*.{file_extension}")
    grouped = {"target": [], "actual": [], "unknown": []}

    for f in files:
        classification = classify_file_type.invoke({"filename": f}).get("classification", "unknown")
        grouped[classification].append(f)

    return grouped

@tool
def load_excel_file(filename: str, preview_rows: int = 5) -> Dict:
    """
    載入 Excel 所有工作表，資料儲存於全域變數 dataframes，key 為 filename::sheet。
    回傳每個工作表的欄位與前幾列預覽。
    """
    global dataframes
    try:
        xls = pd.ExcelFile(filename)
        preview = {}

        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            # 1. 去除所有 object 欄位的前後空白
            df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

            # 2. 強制轉換「日期」欄位
            if "日期" in df.columns:
                df["日期"] = pd.to_datetime(df["日期"], errors="coerce")

            # 3. 強制轉換「實績種類」欄位為純字串並 strip
            if "實績種類" in df.columns:
                df["實績種類"] = df["實績種類"].astype(str).str.strip()

            key = f"{filename}::{sheet}"
            dataframes[key] = df
            preview[key] = {
                "columns": df.columns.tolist(),
                "sample_data": df.head(preview_rows).to_dict(orient="records")
            }

        return {
            "filename": filename,
            "sheets_loaded": len(xls.sheet_names),
            "preview": preview
        }

    except Exception as e:
        return {"error": str(e)}

@tool
def classify_file_type(filename: str) -> Dict:
    """
      分類資料表為 target / actual，根據檔名與欄位內容回傳詳細說明。
      """
    target_keywords = ["目標", "target"]
    actual_keywords = ["統計", "實際", "actual", "實績"]

    try:
        xls = pd.ExcelFile(filename)
    except Exception as e:
        return {"filename": filename, "error": str(e)}

    for sheet in xls.sheet_names:
        try:
            df = pd.read_excel(xls, sheet_name=sheet, nrows=5)
            columns = set(df.columns.str.lower())

            if any(kw in filename.lower() or kw in sheet.lower() for kw in target_keywords):
                if columns & {"目標", "target", "銷售目標", "經銷商"}:
                    return {
                        "filename": filename,
                        "classification": "target",
                        "reason": f"於 sheet【{sheet}】發現目標相關欄位: {columns & {'目標', 'target', '銷售目標', '經銷商'}}"
                    }

            if any(kw in filename.lower() or kw in sheet.lower() for kw in actual_keywords):
                if columns & {"實際", "actual", "銷售", "銷售數", "實績"}:
                    return {
                        "filename": filename,
                        "classification": "actual",
                        "reason": f"於 sheet【{sheet}】發現實際相關欄位: {columns & {'實際', 'actual', '銷售', '銷售數'}}"
                    }

        except Exception:
            continue

    return {
        "filename": filename,
        "classification": "unknown",
        "reason": "無法根據檔案內容判斷類型"
    }

@tool
def compare_target_vs_actual(target_key: str, actual_key: str) -> Dict[str, Any]:
    """
    比對目標與實際資料，只用經銷商代碼 + 據點代碼做 join，
    若實績表中有名稱欄位（如 經銷商名稱、據點），則在合併後一併帶出。
    key 為 filename::sheet_name 格式。
    """
    import pandas as pd

    # 1. 檢查是否已載入
    if target_key not in dataframes or actual_key not in dataframes:
        return {"error": f"請確認這兩個 key 是否存在於 dataframes：{target_key}, {actual_key}"}

    df_target = dataframes[target_key].copy()
    df_actual = dataframes[actual_key].copy()

    # 2. 核心欄位
    dist_code_col    = "經銷商代碼"
    target_point_col = "據點代碼"
    actual_point_col = "營業所代碼"

    # 3. 確認必要欄位
    for col in (dist_code_col, target_point_col):
        if col not in df_target.columns:
            return {"error": f"目標表缺少必要欄位: {col}"}
    for col in (dist_code_col, actual_point_col):
        if col not in df_actual.columns:
            return {"error": f"實際表缺少必要欄位: {col}"}

    # 4. 找銷售欄位
    target_sales_col = next((c for c in df_target.columns if any(k in c for k in ["目標", "目標數", "目標銷售數"])), None)
    actual_sales_col = next((c for c in df_actual.columns if any(k in c for k in ["實績", "銷售", "受訂"])), None)
    if not target_sales_col or not actual_sales_col:
        return {"error": "缺少目標或實際銷售欄位"}

    df_target[target_sales_col] = pd.to_numeric(df_target[target_sales_col], errors="coerce")
    df_actual[actual_sales_col] = pd.to_numeric(df_actual[actual_sales_col], errors="coerce")


    # 5. group by 只用代碼去聚合
    df_t = (
        df_target
        .groupby([dist_code_col, target_point_col], as_index=False)[target_sales_col]
        .sum()
        .rename(columns={target_point_col: actual_point_col, target_sales_col: "target_sales"})
    )

    # 如果實績表有經銷商名稱、據點名稱，就在聚合時一起保留
    extra_cols = []
    if "經銷商名稱" in df_actual.columns:
        extra_cols.append("經銷商名稱")
    if "據點" in df_actual.columns:
        extra_cols.append("據點")

    df_a = (
        df_actual
        .groupby([dist_code_col, actual_point_col] + extra_cols, as_index=False)[actual_sales_col]
        .sum()
        .rename(columns={actual_sales_col: "actual_sales"})
    )

    # 6. 合併
    df_merge = pd.merge(
        df_t, df_a,
        on=[dist_code_col, actual_point_col],
        how="inner"
    )
    df_merge["達標"] = df_merge["actual_sales"] >= df_merge["target_sales"]

    # 7. 寫回全域
    merged_key = f"{target_key}_vs_{actual_key}"
    dataframes[merged_key] = df_merge

    # 8. summary
    total    = int(len(df_merge))
    achieved = int(df_merge["達標"].sum())
    rate     = achieved / total if total else 0.0

    return {
        "merged_key": merged_key,
        "summary": {
            "total_matches": total,
            "achieved": achieved,
            "achievement_rate": rate
        },
        "detail": df_merge.to_dict(orient="records")
    }



# 工具集合
tools = [list_and_classify_files, load_excel_file, classify_file_type, compare_target_vs_actual]

# ==================================== 3. 處理映射表：建立 Mapping 處理函數 ====================================
def generate_mapping_text(mapping_path: str) -> str:
    df = pd.read_excel(mapping_path, dtype=str)

    mapping_lines = []
    for _, row in df.iterrows():
        # 去除空白與標準化
        dealer_name = row["經銷商名稱"].strip()
        dealer_code = row["經銷商代碼"].strip()
        site_name = row["營業所名稱"].strip()
        site_code = row["營業所代碼"].strip()

        line = f"({dealer_name}, {site_name}) → ({dealer_code}, {site_code})"
        mapping_lines.append(line)

    mapping_str = "\n".join(mapping_lines)
    return f"映射資料如下：\n{mapping_str}"

# 讀取並轉換 mapping 資料
mapping_text = generate_mapping_text("Mapping Dataframe.xlsx")

# ==================================== 4. 建立系統訊息 ====================================
system_message = f"""
你是資料分析助理，會處理兩類 Excel 檔案：目標檔案（target）和實際檔案（actual）。
每個檔案會透過 classify_file_type 工具標示類型，回傳 JSON 格式包含 filename、classification（"target"、"actual"、"unknown"）、reason。
請注意以下欄位名稱在不同資料表中具有相同意義：
- 「據點」≈「營業所」

請根據以下規則配對檔案：
- 先比對檔名經銷商、經銷商代碼等資訊
- 同一經銷商與經銷商代碼的目標與實際檔案配對
- 無法配對則告知缺少哪方
- 配對後呼叫 compare_target_vs_actual(target_filename, actual_filename) 進行銷售達標分析

判斷依據與工具結果請逐步說明。

時間欄位處理流程：
1. 若問題涉及時間篩選，先確認欄位是否 datetime 型別
2. 非 datetime 執行 pd.to_datetime(欄位, errors="coerce") 並覆寫
3. 轉換後檢查 NaT 數量，超過 10% 需回報資料問題並停止時間分析
4. 確認為 datetime 後，方可使用 .dt 屬性操作

資料分析流程：
1. 確認成功讀取 DataFrame，且欄位存在且格式正確
2. 缺欄位或資料不足，回覆需補充資料，避免分析工具調用
3. 確認後才呼叫 analyze_dataframe() 進行分析

合併與配對規則：
1. 確認兩份資料皆已載入且結構明確，缺一則回覆「資料不足，請提供完整資料」
2. 配對只依「經銷商代碼」與「據點代碼」兩個欄位做精確 merge  
3. 合併完成後，若實績表中有 `經銷商名稱` 或 `據點` 欄，請直接一併輸出，不作為 join key
4. 配對完成進行銷售達標對比分析

分析工具使用原則：
- 優先使用 pandas groupby、sort、filter 做統計與排序
- 銷售進度分析只基於現有紀錄
- 回傳關鍵數據與簡單表格，附主要篩選條件與程式碼，避免過度解釋與大量原始資料

執行分析步驟：
1. list_files() 確認可用檔案
2. 分析問題判斷關鍵字與目標欄位
3. read_excel_head() 預覽相關檔案表頭
4. 載入最可能包含資料的檔案
5. 確認資料完整且格式正確
6. 預覽表頭，以經銷商類欄位配對合併
7. compare_target_vs_actual() 分析銷售達標狀況
8. 回傳結果與關鍵步驟程式碼。

回答規則：
- 使用者問的經銷商名稱與營業所名稱就是此次資料查詢的唯一標準，且結果必須只包含該經銷商/營業所的資料。
- 若經銷商名稱變更，必須完整更新並重置資料上下文，不得帶入之前的經銷商資料。
- 若使用者輸入的是經銷商名稱與營業所名稱，請參照下列對應資訊查找對應的代碼：{mapping_text}
- 如果使用者問『完整列出所有據點』，請完整輸出用戶指定的經銷商下的所有據點資料，Markdown表格格式。
- 如果問『某據點達標狀況』，只回答該據點達標狀況。
- 如果問『某經銷商達標數量』，請從該經銷商完整的所有據點資料中，計算並回覆達標據點數、總據點數與達標率，所有據點必須完整列出，且不得用模糊字眼（如：其他據點）或省略號替代。
- 在輸出 Markdown 明細表後，所有「總據點數」、「達標據點數」與「達標率」**必須**完全依照下列方式從表格文字中解析，**不得**使用任何額外計算或隱性推斷：
    1. **總據點數**：直接數表格中標題列以下、每一行資料的行數（即 Markdown 列數減去標題和分隔線）。
    2. **達標據點數**：逐行檢查「達標」欄，**只有**等於字串 `True` 的那幾行才計入，其他一律不計。
    3. **達標率**：以「達標據點數／總據點數」計算，並顯示為百分比（保留一位小數）。
    4. **嚴禁**重複或另行運算、導入 DataFrame 物件、或憑印象回推；所有 summary 數字都必須和上方 Markdown 表格的文字完全一致。
- 其他情況，請依上下文盡量準確回覆。
- 若無要求，不須顯示據點名稱，回答時皆以代碼提供。
"""

# 四、流程控制與避免無限循環：
# 1. 在互動過程中，避免重複詢問相同的問題或補充資料要求。
# 2. 若使用者多次未提供完整資料，應回覆「因資料不足，無法繼續分析，請提供完整資料後再行查詢」並終止後續自動請求。
# 3. 回答時請條理清晰，描述處理步驟與程式碼邏輯，方便使用者理解與驗證。
# 請務必確保回答時條理清楚，有理有據，並避免重複或無限迴圈的互動行為。
# 請在分析過程中顯示如何判斷「經銷商」欄位（包含模糊比對過程與欄位名稱篩選依據），以利使用者確認系統理解正確。
# 若資料不足或問題不明，請先說明並請求補充，避免盲目分析。
# 這樣的回答模式能確保分析準確、互動有效。

# ==================================== 5. Agent ====================================
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

# ==================================== 使用範例  ====================================
if __name__ == "__main__":
    user_input = "哪個車款販售得最少？"

    with get_openai_callback() as cb:
        response = agent_executor.invoke({"input": user_input})

    print("🧾 分析結果：")
    print(response["output"])