# 🚗 HOTAI MOTOR 銷售數據分析平台

一個基於 LangChain 和 Streamlit 的智能汽車銷售數據分析系統，專為 HOTAI MOTOR 銷售業務設計。

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.28+-red.svg)
![LangChain](https://img.shields.io/badge/langchain-v0.1+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 📋 系統概述

本系統整合了先進的 AI 技術與汽車銷售業務邏輯，提供：

- 🤖 **智能問答分析**：使用 LangChain + OpenAI GPT-4 進行自然語言查詢
- 📊 **雙模式分析**：一般資料探索 + 目標 vs 實際銷售比對
- 🌐 **現代化 Web 介面**：Streamlit 打造的友善操作界面
- 📈 **專業業務指標**：達成率、去年比、前月比、推進率自動計算
- 🔄 **完整資料流程**：檔案上傳、資料檢視、智能分析一站式服務

## 🎯 核心功能

### 1. 📤 資料上傳管理
- **多檔案支援**：同時上傳多個 Excel 檔案
- **自動檢測**：智能識別目標檔案、實績檔案、映射表
- **格式驗證**：確保資料格式符合業務需求
- **即時狀態**：檔案上傳狀態和大小顯示

### 2. 📊 資料檢視分析
- **全方位預覽**：資料表頭、統計資訊、缺失值分析
- **彈性檢視**：可調整顯示行數、欄位資訊詳細展示
- **多表管理**：支援多個資料集同時檢視和管理

### 3. 💬 智能問答系統
- **自然語言查詢**：支援中文自然語言問答
- **業務邏輯整合**：內建汽車銷售專業術語和計算規則
- **範例查詢**：預設常用查詢模板，一鍵執行
- **聊天記錄**：保留查詢歷史，便於追蹤分析過程

## 🏗️ 技術架構

```
HOTAI MOTOR 銷售數據分析平台
├── 🌐 Web 前端 (Streamlit)
│   ├── 📤 檔案上傳介面
│   ├── 📊 資料檢視與管理
│   └── 💬 智能問答介面
├── 🤖 AI 分析引擎 (LangChain)
│   ├── solution_combine.py - 主要整合邏輯
│   ├── solution1.py - 一般資料分析工具
│   └── solution3.py - 目標對比分析工具
└── 📊 資料處理層
    ├── Excel 檔案解析
    ├── 多工作表管理
    └── 業務指標計算
```

## 🚀 快速開始

### 環境要求
- Python 3.8+
- OpenAI API Key

### 1. 安裝依賴套件
```bash
pip install -r requirements.txt
```

### 2. 設定 API Key
在 Streamlit Cloud 的 Secrets 設定中新增：
```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

### 3. 啟動應用程式
```bash
streamlit run streamlit_app.py
```

### 4. 準備資料檔案
系統需要以下三個 Excel 檔案：
- `MBIS實績_2025上半年.xlsx` - 實際銷售資料
- `經銷商目標_2025上半年.xlsx` - 銷售目標資料
- `Mapping Dataframe.xlsx` - 經銷商對應表

## 📁 專案結構

```
HOTAI MOTOR/
├── streamlit_app.py          # Streamlit Web 應用程式
├── solution_combine.py       # 核心 LangChain 整合邏輯
├── solution1.py             # 一般資料分析工具集
├── solution3.py             # 目標對比分析工具集
├── requirements.txt         # Python 套件依賴
├── README.md               # 專案說明文件
├── CHANGELOG.md            # 程式變動記錄
├── MBIS實績_2025上半年.xlsx    # 實績資料檔案
├── 經銷商目標_2025上半年.xlsx   # 目標資料檔案
└── Mapping Dataframe.xlsx   # 經銷商映射表
```

## 💡 使用說明

### 資料上傳
1. 進入「📤 資料上傳」頁面
2. 點擊「選擇 Excel 檔案」上傳必要資料檔案
3. 系統會自動檢查檔案狀態並顯示上傳結果

### 資料檢視
1. 進入「📊 資料檢視」頁面
2. 選擇要檢視的資料集
3. 查看資料統計、預覽內容和欄位資訊

### 智能問答
1. 進入「💬 智能問答」頁面
2. 輸入自然語言查詢或點擊範例查詢
3. 系統會自動調用 LangChain 進行分析並顯示結果

### 範例查詢

```
"請提供5/22 TOYOTA各車種的販賣台數"
"哪一個據點在 1 月販賣進度最快？"
"經銷商達標狀況分析"
"哪個車款販售得最少？"
```

## 🔧 業務邏輯說明

### 專業術語定義
- **C CROSS** = CC, **Y CROSS** = YC
- **HV** = **HEV** = 油電車
- **據點** = **營業所**, **大盤** = **全體進度**

### 業務指標計算
- **去年比** = 今年實績台數 / 去年實績台數 × 100%
- **前月比** = 本月實績台數 / 上月實績台數 × 100%
- **達成率** = 實績台數 / 目標台數 × 100%
- **推進率** = 實績台數 / 目標台數 × 100%（當月進度）

### 分析流程
1. **一般分析流程**：資料探索、排行分析、統計計算
2. **目標對比流程**：目標 vs 實際銷售達標比對分析

## 🛠️ 開發說明

### 核心原則
- **完全保留原始 LangChain 程式碼**：不修改任何分析邏輯
- **純 Web 介面整合**：只提供 Streamlit 展示層
- **業務邏輯不變**：所有計算和分析完全依照原始程式

### 主要模組
- `streamlit_app.py`：Web 介面，負責檔案管理和結果展示
- `solution_combine.py`：主要分析邏輯，整合兩種分析流程
- `solution1.py`：一般資料分析工具，包含檔案讀取和 Pandas Agent
- `solution3.py`：目標對比分析工具，包含檔案分類和達標比對

## 📊 系統需求

### 必要套件
```
streamlit>=1.28.0
pandas>=1.5.0
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-experimental>=0.0.50
openai>=1.0.0
openpyxl>=3.0.0
tabulate>=0.9.0
```

### 資料格式要求
- **Excel 檔案**：支援 .xlsx, .xls 格式
- **工作表**：支援多工作表結構
- **編碼**：UTF-8 編碼
- **大小限制**：單檔案 < 200MB

## 🚀 部署指南

### Streamlit Cloud 部署
1. 連接 GitHub 儲存庫
2. 設定主檔案路徑：`streamlit_app.py`
3. 在 Advanced settings → Secrets 中設定 `OPENAI_API_KEY`
4. 部署完成後即可使用

### 本地開發環境
1. Clone 專案到本地
2. 安裝依賴套件：`pip install -r requirements.txt`
3. 設定環境變數或建立 `secret_key` 檔案
4. 執行：`streamlit run streamlit_app.py`

## 📝 版本資訊

- **目前版本**：v1.0.0
- **最後更新**：2025-01-25
- **相容性**：Python 3.8+, Streamlit 1.28+

## 🤝 貢獻指南

歡迎提交問題回報、功能建議或貢獻程式碼：

1. Fork 專案
2. 建立功能分支：`git checkout -b feature/new-feature`
3. 提交變更：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 建立 Pull Request

## 📄 授權條款

本專案採用 MIT 授權條款。詳細資訊請參考 [LICENSE](LICENSE) 檔案。

## 📞 支援與聯絡

如有任何問題或需要技術支援，請透過以下方式聯繫：

- 🐛 問題回報：[GitHub Issues](https://github.com/victoria304040/AI-Powered-Automotive-Business-Intelligence-System/issues)
- 📧 Email：透過 GitHub 聯繫
- 📚 文檔：查閱本 README 和 [程式變動記錄](CHANGELOG.md)

---

**Made with ❤️ for HOTAI MOTOR | Powered by LangChain & Streamlit**