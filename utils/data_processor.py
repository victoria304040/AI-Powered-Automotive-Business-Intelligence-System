"""
資料處理工具模組
整合現有的 LangChain 分析功能
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import os
from datetime import datetime


class DataProcessor:
    """資料處理器類別"""
    
    def __init__(self):
        self.data_cache = {}
        self.processing_history = []
    
    def load_data(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """載入資料檔案"""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # 記錄處理歷史
            self.processing_history.append({
                'action': 'load_data',
                'file': file_path,
                'sheet': sheet_name,
                'timestamp': datetime.now(),
                'rows': len(df),
                'columns': len(df.columns)
            })
            
            return df
            
        except Exception as e:
            raise Exception(f"資料載入失敗: {str(e)}")
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """清理資料"""
        cleaned_df = df.copy()
        
        # 處理日期欄位
        date_columns = ['日期', 'date', '時間', 'timestamp']
        for col in date_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
        
        # 處理字串欄位
        string_columns = cleaned_df.select_dtypes(include=['object']).columns
        for col in string_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
        
        # 記錄處理歷史
        self.processing_history.append({
            'action': 'clean_data',
            'timestamp': datetime.now(),
            'original_rows': len(df),
            'cleaned_rows': len(cleaned_df)
        })
        
        return cleaned_df
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """取得資料摘要"""
        summary = {
            'basic_info': {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'missing_values': df.isnull().sum().sum(),
                'duplicate_rows': df.duplicated().sum()
            },
            'column_info': {},
            'data_types': df.dtypes.astype(str).to_dict()
        }
        
        # 分析每個欄位
        for col in df.columns:
            col_info = {
                'dtype': str(df[col].dtype),
                'non_null_count': df[col].count(),
                'unique_count': df[col].nunique(),
                'missing_count': df[col].isnull().sum()
            }
            
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info.update({
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'mean': df[col].mean(),
                    'std': df[col].std()
                })
            elif pd.api.types.is_string_dtype(df[col]):
                col_info.update({
                    'most_frequent': df[col].mode().iloc[0] if not df[col].mode().empty else None,
                    'avg_length': df[col].astype(str).str.len().mean()
                })
            
            summary['column_info'][col] = col_info
        
        return summary
    
    def filter_data(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """資料篩選"""
        filtered_df = df.copy()
        
        for column, condition in filters.items():
            if column not in df.columns:
                continue
                
            if isinstance(condition, dict):
                if 'min' in condition and 'max' in condition:
                    filtered_df = filtered_df[
                        (filtered_df[column] >= condition['min']) & 
                        (filtered_df[column] <= condition['max'])
                    ]
                elif 'values' in condition:
                    filtered_df = filtered_df[filtered_df[column].isin(condition['values'])]
                elif 'contains' in condition:
                    filtered_df = filtered_df[
                        filtered_df[column].astype(str).str.contains(condition['contains'], na=False)
                    ]
        
        return filtered_df
    
    def aggregate_data(self, df: pd.DataFrame, group_by: List[str], 
                      agg_functions: Dict[str, str]) -> pd.DataFrame:
        """資料聚合"""
        try:
            grouped = df.groupby(group_by).agg(agg_functions).reset_index()
            return grouped
        except Exception as e:
            raise Exception(f"資料聚合失敗: {str(e)}")
    
    def get_processing_history(self) -> List[Dict]:
        """取得處理歷史"""
        return self.processing_history


class BusinessMetricsCalculator:
    """業務指標計算器"""
    
    @staticmethod
    def calculate_achievement_rate(actual: float, target: float) -> float:
        """計算達成率"""
        if target == 0:
            return 0.0
        return (actual / target) * 100
    
    @staticmethod
    def calculate_growth_rate(current: float, previous: float) -> float:
        """計算成長率"""
        if previous == 0:
            return 0.0
        return ((current - previous) / previous) * 100
    
    @staticmethod
    def calculate_yoy_growth(current_year: float, previous_year: float) -> float:
        """計算去年比"""
        return BusinessMetricsCalculator.calculate_growth_rate(current_year, previous_year)
    
    @staticmethod
    def calculate_mom_growth(current_month: float, previous_month: float) -> float:
        """計算前月比"""
        return BusinessMetricsCalculator.calculate_growth_rate(current_month, previous_month)
    
    @staticmethod
    def calculate_cumulative_data(df: pd.DataFrame, date_column: str, 
                                value_column: str) -> pd.DataFrame:
        """計算累計資料"""
        df_sorted = df.sort_values(date_column)
        df_sorted[f'{value_column}_累計'] = df_sorted[value_column].cumsum()
        return df_sorted


def integrate_langchain_tools():
    """
    整合現有的 LangChain 工具
    這個函數將被用來連接現有的 solution_combine.py 中的功能
    """
    try:
        # 這裡將整合現有的 LangChain 工具
        # 從 solution_combine.py 引入相關功能
        pass
    except ImportError:
        # 如果無法引入現有模組，返回 None
        return None


# 工具函數
def format_number(num: float, decimal_places: int = 2) -> str:
    """格式化數字顯示"""
    if pd.isna(num):
        return "N/A"
    return f"{num:,.{decimal_places}f}"


def format_percentage(num: float, decimal_places: int = 1) -> str:
    """格式化百分比顯示"""
    if pd.isna(num):
        return "N/A"
    return f"{num:.{decimal_places}f}%"


def safe_division(numerator: float, denominator: float, default: float = 0.0) -> float:
    """安全除法運算"""
    if denominator == 0 or pd.isna(denominator) or pd.isna(numerator):
        return default
    return numerator / denominator