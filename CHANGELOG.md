# 📋 程式變動記錄 (CHANGELOG)

本檔案記錄 HOTAI MOTOR 銷售數據分析平台的所有重要變動和更新。

格式基於 [Keep a Changelog](https://keepachangelog.com/)，版本號遵循 [語義化版本](https://semver.org/)。

---

## [v1.2.0] - 2025-08-28

### ✨ 新增功能 (Added)
- **DEBUG INFO 除錯資訊區塊**：新增完整的 LangChain 執行除錯功能，便於比對 PyCharm 和 Streamlit 的執行結果

### 🔍 **功能描述**
用戶要求能夠比對 PyCharm 和 Streamlit 環境中 LangChain 的執行結果，以便進行除錯和驗證分析過程的一致性。

### 📝 **用戶原始需求**
> 我想比對 PyCharm 和 Streamlit 的 LangChain 執行結果，請在 Streamlit 程式中新增一個「DEBUG INFO」區塊，內容包括：
> 1. LangChain 工具調用紀錄 (Tool Invocations)  
> 2. Python 執行的 query  
> 3. LangChain 原始回傳 (Raw Response)

### ✅ **實作內容**
1. **🔧 Tool Invocations**：顯示 LangChain 工具調用的完整記錄
   - 每個步驟的工具名稱、輸入參數、輸出結果
   - 以 `Invoking: {tool_name}` 格式顯示調用訊息
   - 支援多步驟工具鏈的完整追蹤

2. **🐍 Python Query**：展示 Python 執行的查詢內容
   - 自動識別 `python_repl_ast` 和相關 Python 執行工具
   - 顯示實際執行的 Python 程式碼
   - 支援複雜查詢中的多段 Python 執行

3. **📄 Raw Response**：完整的 LangChain 原始回應
   - JSON 格式化顯示完整回應結構
   - 包含所有中間步驟和執行統計
   - 便於深度除錯和效能分析

4. **📊 執行統計**：額外的執行資訊
   - 原始查詢內容
   - 回應結構分析
   - 執行步驟統計

### 🔧 技術實作 (Technical Implementation)
```python
def display_debug_info(response: dict, prompt: str):
    # 四個主要區塊的可折疊展示器 (st.expander)
    # 1. Tool Invocations - 工具調用記錄
    # 2. Python Query - Python 執行內容  
    # 3. Raw Response - 原始回應 (JSON 格式)
    # 4. 執行統計 - 查詢和回應分析
```

### 📁 檔案異動
```
修改的檔案：
├── streamlit_app.py        # 新增：display_debug_info() 函數
│                          # 修改：兩處 query_agent() 調用點加入 DEBUG 顯示
└── CHANGELOG.md           # 更新：記錄 DEBUG INFO 功能實作
```

### 🎯 應用場景
- **開發除錯**：比較不同環境的執行結果
- **效能分析**：監控工具調用和執行時間
- **問題診斷**：深入了解 LangChain 的執行過程
- **學習研究**：了解 AI Agent 的工作原理

### 💡 使用方式
在智能問答介面提出問題後，系統會自動在回答下方顯示 **🔍 DEBUG INFO** 區塊，包含四個可展開的資訊區域，提供完整的執行追蹤資訊。

---

## [v1.1.1] - 2025-01-25

### 🐛 修復問題 (Fixed)
- **Streamlit Cloud API Key 讀取問題**：修復在 Streamlit Cloud 部署環境中無法正確讀取 OpenAI API Key 的問題

### ❌ **問題描述**
用戶在 Streamlit Cloud 中已正確設定 `OPENAI_API_KEY` secrets，但智能問答介面仍顯示「❌ 未找到 secret_key 檔案，請確保 OpenAI API Key 已設定」錯誤。

### 🔍 **問題根因**
1. 程式碼只檢查本地 `secret_key` 檔案，未考慮 Streamlit Cloud secrets
2. LangChain 模組導入時，環境變數尚未正確設定
3. API Key 檢查邏輯不完整，未支援多種設定方式

### ✅ **解決方案**
1. **新增多層次 API Key 檢測**：
   ```python
   # 檢查順序：Streamlit secrets → 環境變數 → 本地檔案
   if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
       api_key_available = True
       api_source = "Streamlit Cloud Secrets"
   elif os.environ.get("OPENAI_API_KEY"):
       api_key_available = True
       api_source = "環境變數"
   elif os.path.exists("secret_key"):
       api_key_available = True
       api_source = "本地 secret_key 檔案"
   ```

2. **預先設定環境變數**：
   ```python
   def setup_api_key():
       if not os.environ.get("OPENAI_API_KEY"):
           if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
               os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
   ```

3. **改善錯誤訊息**：提供清楚的設定指引，區分雲端和本地環境

### 🔧 改進項目 (Changed)
- **API Key 檢測增強**：支援 Streamlit Cloud secrets、環境變數、本地檔案三種方式
- **錯誤訊息優化**：提供具體的設定步驟說明
- **成功狀態顯示**：顯示 API Key 來源，便於除錯

### 📁 檔案異動
```
修改的檔案：
├── streamlit_app.py        # 修改：新增多層次 API Key 檢測和設定
└── CHANGELOG.md           # 更新：記錄問題修復過程
```

### 🎯 技術細節
- **相容性保證**：同時支援雲端部署和本地開發環境
- **無侵入性**：不修改原始 LangChain 程式碼，僅在 Streamlit 層處理
- **錯誤處理**：提供清晰的診斷訊息和解決步驟

---

## [v1.1.0] - 2025-01-25

### ✨ 新增功能 (Added)
- **檔案上傳功能**：在 Streamlit 介面中新增完整的檔案上傳系統
  - 支援多檔案同時上傳 (.xlsx, .xls 格式)
  - 自動檔案保存到程式執行目錄
  - 即時檔案狀態檢查和大小顯示
  - 上傳成功/失敗訊息回饋

- **專案文檔完善**：
  - 全新撰寫的 `README.md`，包含完整的專案說明、安裝指南、使用說明
  - 建立 `CHANGELOG.md`，記錄所有程式變動和版本歷史
  - 新增系統架構圖和技術說明

### 🔧 改進項目 (Changed)
- **檔案上傳頁面重構**：
  - 從純狀態檢查改為功能性檔案上傳介面
  - 新增檔案要求說明和系統整合說明
  - 優化使用者體驗和視覺回饋

### 📁 檔案異動
```
新增/修改的檔案：
├── streamlit_app.py        # 修改：新增檔案上傳功能
├── README.md              # 新增：完整專案說明文檔
└── CHANGELOG.md           # 新增：程式變動記錄檔案
```

### 🎯 技術細節
- **檔案處理**：使用 Streamlit 的 `st.file_uploader()` 實現多檔案上傳
- **錯誤處理**：新增檔案保存失敗的異常處理和使用者提示
- **狀態管理**：即時檢查檔案存在狀態，提供清晰的視覺反饋

---

## [v1.0.0] - 2025-01-25

### 🎉 初始發布 (Initial Release)

### ✨ 核心功能 (Core Features)
- **Streamlit Web 應用程式**：完整的網頁介面系統
  - 📤 資料上傳頁面：檔案狀態檢查和管理
  - 📊 資料檢視頁面：資料預覽、統計資訊、欄位分析
  - 💬 智能問答頁面：自然語言查詢介面

- **LangChain 整合**：完全保留原始分析邏輯
  - 直接調用 `solution_combine.py` 的 `query_agent()` 函數
  - 支援兩種分析流程：一般分析 + 目標對比分析
  - 整合所有原始工具函數和業務邏輯

- **智能問答系統**：
  - 自然語言查詢處理
  - 聊天記錄保存
  - 範例查詢按鈕
  - 即時結果顯示

### 🔧 技術架構 (Technical Architecture)
- **前端框架**：Streamlit 1.28+
- **AI 引擎**：LangChain + OpenAI GPT-4
- **資料處理**：Pandas + Excel 檔案支援
- **部署平台**：Streamlit Cloud + GitHub 整合

### 📦 核心模組 (Core Modules)
```
專案結構：
├── streamlit_app.py          # Streamlit Web 應用程式主檔案
├── solution_combine.py       # 核心 LangChain 整合邏輯 (原始)
├── solution1.py             # 一般資料分析工具 (原始)
├── solution3.py             # 目標對比分析工具 (原始)
├── requirements.txt         # Python 套件依賴清單
├── MBIS實績_2025上半年.xlsx    # 實際銷售資料檔案
├── 經銷商目標_2025上半年.xlsx   # 銷售目標資料檔案
└── Mapping Dataframe.xlsx   # 經銷商映射對應表
```

### 🎯 設計原則 (Design Principles)
1. **零程式碼修改**：完全不修改任何原始 LangChain 程式碼
2. **純介面整合**：只提供 Web 展示層，保留所有分析邏輯
3. **業務邏輯不變**：所有計算和分析完全依照原始程式
4. **使用者友善**：提供現代化、直觀的操作介面

### 🔍 支援功能 (Supported Features)
- **檔案格式**：Excel (.xlsx, .xls)
- **多工作表**：自動解析和管理多個工作表
- **業務指標**：達成率、去年比、前月比、推進率
- **專業術語**：汽車銷售業務專用名詞和計算規則
- **雙模式分析**：
  - A. 一般性資料探索與分析
  - B. 目標 vs. 實際銷售達標比對

### 🚀 部署配置 (Deployment Configuration)
- **GitHub 儲存庫**：`victoria304040/AI-Powered-Automotive-Business-Intelligence-System`
- **主分支**：`main`
- **主檔案**：`streamlit_app.py`
- **環境變數**：`OPENAI_API_KEY` (透過 Streamlit Secrets 管理)

### 📋 依賴套件 (Dependencies)
```
核心套件版本：
- streamlit>=1.28.0          # Web 應用框架
- pandas>=1.5.0             # 資料處理
- langchain>=0.1.0          # AI 分析框架
- langchain-openai>=0.0.5   # OpenAI 整合
- langchain-experimental>=0.0.50  # Pandas Agent
- openai>=1.0.0             # OpenAI API
- openpyxl>=3.0.0           # Excel 檔案處理
- tabulate>=0.9.0           # 表格格式化
```

---

## 🔄 變動類型說明 (Types of Changes)

- **✨ Added (新增)**：新功能
- **🔧 Changed (變更)**：既有功能的變更
- **⚠️ Deprecated (棄用)**：即將移除的功能
- **❌ Removed (移除)**：已移除的功能
- **🐛 Fixed (修復)**：錯誤修復
- **🔒 Security (安全)**：安全性相關修復

---

## 🎯 開發里程碑 (Development Milestones)

### 完成項目 ✅
- [x] Streamlit Web 應用程式建置
- [x] LangChain 程式碼完整整合
- [x] 檔案上傳功能實現
- [x] 智能問答系統建置
- [x] 資料檢視功能完成
- [x] GitHub 部署配置
- [x] 專案文檔撰寫

### 未來規劃 🚀
- [ ] 資料視覺化圖表
- [ ] 使用者認證系統
- [ ] 多語言支援 (英文介面)
- [ ] API 化服務
- [ ] 行動裝置優化
- [ ] 資料匯出功能增強

---

## 📞 變動記錄維護

本檔案由開發團隊維護，每次重要更新都會記錄在此。

- **記錄格式**：遵循 [Keep a Changelog](https://keepachangelog.com/) 標準
- **版本號規則**：使用 [語義化版本](https://semver.org/) (MAJOR.MINOR.PATCH)
- **更新頻率**：每次功能發布或重要修改後更新

如有任何問題或建議，請透過 GitHub Issues 回報。

---

**最後更新**：2025-08-28  
**維護者**：HOTAI MOTOR Development Team