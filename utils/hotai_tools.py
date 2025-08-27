"""
HOTAI MOTOR 專用分析工具
基於 solution1.py, solution3.py, solution_combine.py 的完整整合
"""
import os
import pandas as pd
import numpy as np
import glob
from typing import List, Dict, Any, Optional
import streamlit as st
from langchain.tools import tool

# 全域字典儲存多個 DataFrame（與原始程式保持一致）
dataframes = {}


# ========================================
# Solution1.py 工具 - 一般性資料分析
# ========================================

@tool
def list_files(file_extension: str = "xlsx") -> List[str]:
    """列出目前目錄下所有指定副檔名的檔案"""
    # 在 Streamlit 環境中，我們改為列出已上傳的檔案
    if hasattr(st.session_state, 'uploaded_data') and st.session_state.uploaded_data:
        files = [filename for filename in st.session_state.uploaded_data.keys() 
                if filename.endswith(f'.{file_extension}')]
        return files
    return []


@tool
def read_excel_head(filename: str, sheet_name: Optional[str] = None, n_rows: int = 5) -> Dict:
    """預覽 Excel 檔案的表頭和前幾筆資料"""
    try:
        # 從 Streamlit session state 讀取
        if hasattr(st.session_state, 'uploaded_data') and filename in st.session_state.uploaded_data:
            file_info = st.session_state.uploaded_data[filename]
            
            if sheet_name:
                if sheet_name in file_info['data']:
                    df = file_info['data'][sheet_name].head(n_rows)
                else:
                    return {"error": f"找不到工作表: {sheet_name}"}
            else:
                # 取第一個工作表
                first_sheet = list(file_info['data'].keys())[0]
                df = file_info['data'][first_sheet].head(n_rows)
                sheet_name = first_sheet
            
            columns = df.columns.tolist()
            sample_data = df.to_dict(orient='records')
            
            return {
                "filename": filename,
                "sheet_name": sheet_name,
                "columns": columns,
                "sample_data": sample_data,
                "total_rows": len(file_info['data'][sheet_name]) if sheet_name in file_info['data'] else 0
            }
        else:
            return {"error": f"找不到檔案: {filename}"}
            
    except Exception as e:
        return {"error": f"讀取失敗: {str(e)}"}


@tool
def read_excel_file(filename: str, sheet_name: Optional[str] = None) -> str:
    """完整讀取指定的 Excel 檔案，並返回資料集的摘要資訊"""
    try:
        if hasattr(st.session_state, 'uploaded_data') and filename in st.session_state.uploaded_data:
            file_info = st.session_state.uploaded_data[filename]
            
            if sheet_name:
                if sheet_name in file_info['data']:
                    df = file_info['data'][sheet_name].copy()
                    
                    # 資料清理（依據 solution1.py 邏輯）
                    # 1. 清理資料：去除字串欄位的前後空白
                    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
                    
                    # 2. 強制轉換「日期」欄位為 datetime
                    if "日期" in df.columns:
                        df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
                    
                    # 3. 強制轉換「實績種類」欄位為乾淨字串
                    if "實績種類" in df.columns:
                        df["實績種類"] = df["實績種類"].astype(str).str.strip()
                    
                    # 儲存到全域 dataframes（使用 current_df 作為主要資料）
                    key = f"{filename}::{sheet_name}"
                    dataframes[key] = df
                    dataframes['current_df'] = df  # solution1.py 相容性
                    
                    return f"已載入 {filename}::{sheet_name}，資料列數: {df.shape[0]}，欄位數: {df.shape[1]}。可透過 current_df 存取。"
                else:
                    return f"❌ 找不到工作表: {sheet_name}"
            else:
                # 載入所有工作表
                loaded_sheets = []
                for sheet_name, df in file_info['data'].items():
                    # 資料清理
                    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
                    if "日期" in df.columns:
                        df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
                    if "實績種類" in df.columns:
                        df["實績種類"] = df["實績種類"].astype(str).str.strip()
                    
                    key = f"{filename}::{sheet_name}"
                    dataframes[key] = df.copy()
                    loaded_sheets.append(f"{sheet_name}({len(df)}行)")
                
                # 設定第一個工作表為 current_df
                first_sheet_name = list(file_info['data'].keys())[0]
                dataframes['current_df'] = dataframes[f"{filename}::{first_sheet_name}"]
                
                return f"✅ 成功載入 {filename} 的所有工作表: {', '.join(loaded_sheets)}"
        else:
            return f"❌ 找不到檔案: {filename}"
            
    except Exception as e:
        return f"❌ 載入失敗: {str(e)}"


@tool
def analyze_dataframe(query: str) -> str:
    """使用 Pandas Agent 分析當前的資料框架，根據使用者的自然語言查詢執行操作"""
    if 'current_df' not in dataframes:
        return "尚未載入任何資料集，請先使用 read_excel_file 載入資料。"

    try:
        df = dataframes['current_df']
        
        # 執行資料清理（確保資料型態正確）
        if "日期" in df.columns:
            df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
        
        if "實績種類" in df.columns:
            df["實績種類"] = df["實績種類"].astype(str).str.strip()
        
        # 更新 dataframes
        dataframes['current_df'] = df

        # 使用 LangChain Pandas Agent 進行分析（和 solution1.py 完全一致）
        from langchain_experimental.agents import create_pandas_dataframe_agent
        from langchain_openai import ChatOpenAI
        from langchain.agents.agent_types import AgentType

        custom_llm = ChatOpenAI(
            temperature=0,
            model="gpt-4o-2024-11-20"
        )

        df_agent = create_pandas_dataframe_agent(
            custom_llm,
            df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            allow_dangerous_code=True
        )

        # 執行查詢
        result = df_agent.run(query)
        return result
        
    except Exception as e:
        return f"分析時發生錯誤: {str(e)}

錯誤詳情: {type(e).__name__}"

# ========================================
# Solution3.py 工具 - 目標 vs 實際分析
# ========================================

@tool
def list_and_classify_files(file_extension: str = "xlsx") -> Dict[str, List[str]]:
    """回傳分類後的檔案列表：target / actual / unknown"""
    files = list_files(file_extension)
    grouped = {"target": [], "actual": [], "unknown": []}
    
    for filename in files:
        classification_result = classify_file_type(filename)
        classification = classification_result.get("classification", "unknown")
        grouped[classification].append(filename)
    
    return grouped


@tool
def load_excel_file(filename: str, preview_rows: int = 5) -> Dict:
    """載入 Excel 所有工作表，資料儲存於全域變數 dataframes，key 為 filename::sheet"""
    try:
        if hasattr(st.session_state, 'uploaded_data') and filename in st.session_state.uploaded_data:
            file_info = st.session_state.uploaded_data[filename]
            preview = {}
            
            for sheet_name, df in file_info['data'].items():
                # 資料清理（依據 solution3.py 邏輯）
                # 1. 去除所有 object 欄位的前後空白
                df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
                
                # 2. 強制轉換「日期」欄位
                if "日期" in df.columns:
                    df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
                
                # 3. 強制轉換「實績種類」欄位為純字串並 strip
                if "實績種類" in df.columns:
                    df["實績種類"] = df["實績種類"].astype(str).str.strip()
                
                key = f"{filename}::{sheet_name}"
                dataframes[key] = df
                preview[key] = {
                    "columns": df.columns.tolist(),
                    "sample_data": df.head(preview_rows).to_dict(orient="records"),
                    "rows": len(df),
                    "columns_count": len(df.columns)
                }
            
            return {
                "filename": filename,
                "sheets_loaded": len(file_info['data']),
                "preview": preview
            }
        else:
            return {"error": f"找不到檔案: {filename}"}
            
    except Exception as e:
        return {"error": f"載入失敗: {str(e)}"}


@tool
def classify_file_type(filename: str) -> Dict:
    """分類資料表為 target / actual，根據檔名與欄位內容回傳詳細說明"""
    target_keywords = ["目標", "target"]
    actual_keywords = ["統計", "實際", "actual", "實績"]
    
    try:
        if hasattr(st.session_state, 'uploaded_data') and filename in st.session_state.uploaded_data:
            file_info = st.session_state.uploaded_data[filename]
            
            for sheet_name, df in file_info['data'].items():
                columns = set(df.columns.str.lower())
                
                if any(kw in filename.lower() or kw in sheet_name.lower() for kw in target_keywords):
                    if columns & {"目標", "target", "銷售目標", "經銷商"}:
                        return {
                            "filename": filename,
                            "classification": "target",
                            "reason": f"於 sheet【{sheet_name}】發現目標相關欄位: {columns & {'目標', 'target', '銷售目標', '經銷商'}}"
                        }
                
                if any(kw in filename.lower() or kw in sheet_name.lower() for kw in actual_keywords):
                    if columns & {"實際", "actual", "銷售", "銷售數", "實績"}:
                        return {
                            "filename": filename,
                            "classification": "actual",
                            "reason": f"於 sheet【{sheet_name}】發現實際相關欄位: {columns & {'實際', 'actual', '銷售', '銷售數', '實績'}}"
                        }
            
            return {
                "filename": filename,
                "classification": "unknown",
                "reason": "無法根據檔案內容判斷類型"
            }
        else:
            return {"filename": filename, "error": f"檔案不存在: {filename}"}
            
    except Exception as e:
        return {"filename": filename, "error": str(e)}


@tool
def compare_target_vs_actual(target_key: str, actual_key: str) -> Dict[str, Any]:
    """
    比對目標與實際資料，只用經銷商代碼 + 據點代碼做 join，
    若實績表中有名稱欄位（如 經銷商名稱、據點），則在合併後一併帶出。
    key 為 filename::sheet_name 格式。
    """
    try:
        # 1. 檢查是否已載入
        if target_key not in dataframes or actual_key not in dataframes:
            return {"error": f"請確認這兩個 key 是否存在於 dataframes：{target_key}, {actual_key}"}
        
        df_target = dataframes[target_key].copy()
        df_actual = dataframes[actual_key].copy()
        
        # 2. 核心欄位（依據 solution3.py 邏輯）
        dist_code_col = "經銷商代碼"
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
        
        # 5. group by 只用代碼去聚合（依據 solution3.py 邏輯）
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
        merged_key = f"merged_{target_key.split('::')[0]}_{actual_key.split('::')[0]}"
        dataframes[merged_key] = df_merge
        
        # 8. summary
        total = int(len(df_merge))
        achieved = int(df_merge["達標"].sum())
        rate = achieved / total if total else 0.0
        
        return {
            "merged_key": merged_key,
            "target_file": target_key,
            "actual_file": actual_key,
            "merge_columns": [dist_code_col, actual_point_col],
            "target_sales_column": target_sales_col,
            "actual_sales_column": actual_sales_col,
            "total_records": total,
            "achieved_records": achieved,
            "achievement_rate": round(rate * 100, 1),
            "summary": f"總筆數: {total}, 達成筆數: {achieved}, 達成率: {rate*100:.1f}%",
            "detail": df_merge.to_dict(orient="records")
        }
        
    except Exception as e:
        return {"error": f"比較過程發生錯誤: {str(e)}"}


@tool
def summarize_performance_summary(merged_key: str, dealer_name: Optional[str] = None) -> Dict:
    """總結績效摘要（針對特定經銷商）"""
    try:
        if merged_key not in dataframes:
            return {"error": f"合併資料 {merged_key} 不存在，請先執行 compare_target_vs_actual"}
        
        df = dataframes[merged_key]
        
        if dealer_name:
            # 篩選特定經銷商
            dealer_conditions = [
                df['經銷商名稱'].str.contains(dealer_name, case=False, na=False) if '經銷商名稱' in df.columns else pd.Series([False] * len(df)),
                df['據點'].str.contains(dealer_name, case=False, na=False) if '據點' in df.columns else pd.Series([False] * len(df)),
                df['營業所'].str.contains(dealer_name, case=False, na=False) if '營業所' in df.columns else pd.Series([False] * len(df))
            ]
            
            dealer_mask = pd.concat(dealer_conditions, axis=1).any(axis=1)
            filtered_df = df[dealer_mask]
            
            if len(filtered_df) == 0:
                return {"error": f"找不到經銷商 '{dealer_name}' 的資料"}
            
            df = filtered_df
        
        # 計算統計數據
        total_records = len(df)
        achieved_records = len(df[df['達標'] == True])
        achievement_rate = (achieved_records / total_records * 100) if total_records > 0 else 0
        
        # 計算數值總計
        target_sales_sum = df['target_sales'].sum() if 'target_sales' in df.columns else 0
        actual_sales_sum = df['actual_sales'].sum() if 'actual_sales' in df.columns else 0
        overall_achievement = (actual_sales_sum / target_sales_sum * 100) if target_sales_sum > 0 else 0
        
        summary = {
            "dealer_name": dealer_name or "全部經銷商",
            "total_records": total_records,
            "achieved_records": achieved_records,
            "achievement_rate": round(achievement_rate, 1),
            "total_target": target_sales_sum,
            "total_actual": actual_sales_sum,
            "overall_achievement": round(overall_achievement, 1),
            "summary_text": f"總筆數: {total_records}, 達成筆數: {achieved_records}, 達成率: {achievement_rate:.1f}%"
        }
        
        return summary
        
    except Exception as e:
        return {"error": f"總結結果時發生錯誤: {str(e)}"}


# ========================================
# 映射表處理（來自 solution3.py）
# ========================================

def generate_mapping_text(mapping_file: str) -> str:
    """生成映射表文字"""
    try:
        # 在 Streamlit 環境中從 session state 讀取
        if hasattr(st.session_state, 'uploaded_data') and mapping_file in st.session_state.uploaded_data:
            file_info = st.session_state.uploaded_data[mapping_file]
            first_sheet = list(file_info['data'].keys())[0]
            df = file_info['data'][first_sheet]
            
            mapping_lines = []
            for _, row in df.iterrows():
                # 依據 solution3.py 的邏輯處理
                if len(row) >= 4:  # 假設有經銷商名稱、經銷商代碼、營業所名稱、營業所代碼
                    dealer_name = str(row.iloc[0]).strip()
                    dealer_code = str(row.iloc[1]).strip()  
                    site_name = str(row.iloc[2]).strip()
                    site_code = str(row.iloc[3]).strip()
                    
                    line = f"({dealer_name}, {site_name}) → ({dealer_code}, {site_code})"
                    mapping_lines.append(line)
            
            mapping_str = "\n".join(mapping_lines)
            return f"映射資料如下：\n{mapping_str}"
        else:
            return "映射表檔案未找到或未上傳"
    except Exception as e:
        return f"映射表載入失敗: {str(e)}"


# ========================================
# 業務計算器類
# ========================================

class BusinessCalculator:
    """業務指標計算器"""
    
    @staticmethod
    def calculate_achievement_rate(actual: float, target: float) -> float:
        """計算達成率 = 實績 / 目標 × 100%"""
        if target == 0:
            return 0.0
        return round((actual / target) * 100, 1)
    
    @staticmethod
    def calculate_yoy_growth(current_year: float, last_year: float) -> float:
        """計算去年比 = 今年 / 去年 × 100%"""
        if last_year == 0:
            return 0.0
        return round((current_year / last_year) * 100, 1)
    
    @staticmethod
    def calculate_mom_growth(current_month: float, last_month: float) -> float:
        """計算前月比 = 本月 / 上月 × 100%"""
        if last_month == 0:
            return 0.0
        return round((current_month / last_month) * 100, 1)
    
    @staticmethod
    def calculate_progress_rate(current: float, target: float) -> float:
        """計算推進率 = 目前進度 / 目標 × 100%"""
        if target == 0:
            return 0.0
        return round((current / target) * 100, 1)


# ========================================
# 取得所有工具的函數（供 LangChain 使用）
# ========================================

def get_all_tools():
    """返回所有可用的分析工具（整合 solution1.py 和 solution3.py）"""
    return [
        # Solution1.py 工具
        list_files,
        read_excel_head,
        read_excel_file,
        analyze_dataframe,
        # Solution3.py 工具  
        list_and_classify_files,
        load_excel_file,
        classify_file_type,
        compare_target_vs_actual,
        summarize_performance_summary
    ]