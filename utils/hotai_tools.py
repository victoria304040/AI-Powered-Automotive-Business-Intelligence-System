"""
HOTAI MOTOR 專用分析工具
從 solution1.py 和 solution3.py 整合的工具函數
"""
import os
import pandas as pd
import glob
from typing import List, Dict, Any, Optional
import streamlit as st
from langchain.tools import tool


# 全域字典儲存多個 DataFrame（與原始程式保持一致）
dataframes = {}


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
        if filename in st.session_state.uploaded_data:
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
    """完整讀取 Excel 檔案並載入到全域 dataframes 字典"""
    try:
        if filename in st.session_state.uploaded_data:
            file_info = st.session_state.uploaded_data[filename]
            
            if sheet_name:
                if sheet_name in file_info['data']:
                    df = file_info['data'][sheet_name].copy()
                    # 儲存到全域 dataframes
                    dataframes[f"{filename}::{sheet_name}"] = df
                    return f"✅ 成功載入 {filename} 的 {sheet_name} 工作表，共 {len(df)} 行 {len(df.columns)} 欄"
                else:
                    return f"❌ 找不到工作表: {sheet_name}"
            else:
                # 載入所有工作表
                loaded_sheets = []
                for sheet_name, df in file_info['data'].items():
                    dataframes[f"{filename}::{sheet_name}"] = df.copy()
                    loaded_sheets.append(f"{sheet_name}({len(df)}行)")
                
                return f"✅ 成功載入 {filename} 的所有工作表: {', '.join(loaded_sheets)}"
        else:
            return f"❌ 找不到檔案: {filename}"
            
    except Exception as e:
        return f"❌ 載入失敗: {str(e)}"


@tool
def analyze_dataframe(query: str) -> str:
    """分析載入的資料框"""
    if not dataframes:
        return "❌ 沒有載入的資料可供分析，請先使用 read_excel_file 載入資料"
    
    try:
        # 取得最近載入的資料框
        latest_key = list(dataframes.keys())[-1]
        df = dataframes[latest_key]
        
        # 清理日期欄位
        date_columns = ['日期', 'Date', '時間', 'Timestamp']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # 清理字串欄位（依據原程式邏輯）
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            df[col] = df[col].astype(str).str.strip()
        
        # 分析邏輯（根據查詢內容）
        result_parts = []
        result_parts.append(f"📊 **分析資料**: {latest_key}")
        result_parts.append(f"📈 **資料規模**: {len(df):,} 行 × {len(df.columns)} 欄")
        
        # 基本統計
        if any(keyword in query for keyword in ['統計', '摘要', '概況']):
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                result_parts.append("📊 **數值欄位統計**:")
                for col in numeric_cols[:3]:  # 限制顯示前3個數值欄位
                    stats = df[col].describe()
                    result_parts.append(f"  • {col}: 平均 {stats['mean']:.1f}, 標準差 {stats['std']:.1f}")
        
        # 欄位資訊
        if any(keyword in query for keyword in ['欄位', 'columns', '結構']):
            result_parts.append("📋 **欄位資訊**:")
            for i, col in enumerate(df.columns[:10], 1):  # 限制顯示前10個欄位
                non_null = df[col].count()
                result_parts.append(f"  {i}. {col} ({df[col].dtype}, {non_null:,} 非空值)")
        
        return "\n".join(result_parts)
        
    except Exception as e:
        return f"❌ 分析過程發生錯誤: {str(e)}"


@tool
def list_and_classify_files(file_extension: str = "xlsx") -> Dict[str, List[str]]:
    """分類已上傳的檔案：target / actual / unknown"""
    files = list_files(file_extension)
    grouped = {"target": [], "actual": [], "unknown": []}
    
    for filename in files:
        if "目標" in filename or "target" in filename.lower():
            grouped["target"].append(filename)
        elif "實績" in filename or "actual" in filename.lower() or "MBIS" in filename:
            grouped["actual"].append(filename)
        else:
            grouped["unknown"].append(filename)
    
    return grouped


@tool
def load_excel_file(filename: str, preview_rows: int = 5) -> Dict:
    """載入 Excel 所有工作表到全域 dataframes"""
    try:
        if filename in st.session_state.uploaded_data:
            file_info = st.session_state.uploaded_data[filename]
            result = {"filename": filename, "sheets": {}}
            
            for sheet_name, df in file_info['data'].items():
                # 載入到全域 dataframes
                key = f"{filename}::{sheet_name}"
                dataframes[key] = df.copy()
                
                # 準備預覽資訊
                result["sheets"][sheet_name] = {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": df.columns.tolist(),
                    "preview": df.head(preview_rows).to_dict(orient='records')
                }
            
            return result
        else:
            return {"error": f"找不到檔案: {filename}"}
            
    except Exception as e:
        return {"error": f"載入失敗: {str(e)}"}


@tool
def classify_file_type(filename: str) -> Dict[str, str]:
    """分類檔案類型"""
    if "目標" in filename or "target" in filename.lower():
        return {"filename": filename, "classification": "target", "description": "目標資料檔案"}
    elif "實績" in filename or "actual" in filename.lower() or "MBIS" in filename:
        return {"filename": filename, "classification": "actual", "description": "實績資料檔案"}
    else:
        return {"filename": filename, "classification": "unknown", "description": "未知類型檔案"}


@tool
def compare_target_vs_actual(target_key: str, actual_key: str) -> Dict:
    """比較目標與實際資料"""
    try:
        if target_key not in dataframes or actual_key not in dataframes:
            return {"error": "指定的資料鍵值不存在於 dataframes 中"}
        
        target_df = dataframes[target_key]
        actual_df = dataframes[actual_key]
        
        # 這裡實現比較邏輯（簡化版）
        result = {
            "target_file": target_key,
            "actual_file": actual_key,
            "target_records": len(target_df),
            "actual_records": len(actual_df),
            "summary": f"目標資料 {len(target_df)} 筆，實績資料 {len(actual_df)} 筆"
        }
        
        # 如果有共同欄位，可以進行更詳細的比較
        common_columns = set(target_df.columns) & set(actual_df.columns)
        if common_columns:
            result["common_columns"] = list(common_columns)
            result["comparison_feasible"] = True
        else:
            result["comparison_feasible"] = False
        
        return result
        
    except Exception as e:
        return {"error": f"比較過程發生錯誤: {str(e)}"}


def generate_mapping_text(mapping_file: str) -> str:
    """生成映射表文字（從 solution3 移植）"""
    try:
        # 在 Streamlit 環境中從 session state 讀取
        if mapping_file in st.session_state.uploaded_data:
            file_info = st.session_state.uploaded_data[mapping_file]
            first_sheet = list(file_info['data'].keys())[0]
            df = file_info['data'][first_sheet]
            
            mapping_text = "經銷商與營業所對應資訊:\n"
            for _, row in df.iterrows():
                mapping_text += f"- {row.iloc[0]}: {row.iloc[1]}\n"
            
            return mapping_text
        else:
            return "映射表檔案未找到"
            
    except Exception as e:
        return f"映射表讀取失敗: {str(e)}"


# 工具集合（對應原程式的 tools 列表）
def get_all_tools():
    """取得所有工具的列表"""
    return [
        list_files,
        read_excel_head,
        read_excel_file,
        analyze_dataframe,
        list_and_classify_files,
        load_excel_file,
        classify_file_type,
        compare_target_vs_actual,
    ]


# 業務邏輯計算函數
class BusinessCalculator:
    """業務計算器（對應原程式的計算邏輯）"""
    
    @staticmethod
    def calculate_achievement_rate(actual: float, target: float) -> float:
        """達成率 = 實績台數 / 目標台數 × 100%"""
        if target == 0:
            return 0.0
        return (actual / target) * 100
    
    @staticmethod
    def calculate_yoy_growth(current: float, previous: float) -> float:
        """去年比 = 今年實績台數 / 去年實績台數 × 100%"""
        if previous == 0:
            return 0.0
        return (current / previous) * 100
    
    @staticmethod
    def calculate_mom_growth(current: float, previous: float) -> float:
        """前月比 = 本月實績台數 / 上月實績台數 × 100%"""
        if previous == 0:
            return 0.0
        return (current / previous) * 100
    
    @staticmethod
    def calculate_progress_rate(actual: float, target: float) -> float:
        """推進率（用於當月中進度）"""
        return BusinessCalculator.calculate_achievement_rate(actual, target)