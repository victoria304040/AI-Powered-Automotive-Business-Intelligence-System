# HOTAI MOTOR 銷售數據分析平台

一個基於 Streamlit 的多功能數據分析平台，整合了檔案上傳、資料檢視編輯和 AI 問答功能。

## 🚀 功能特色

### 📤 資料上傳
- 支援 Excel (.xlsx, .xls) 和 CSV (.csv) 檔案
- 多檔案同時上傳
- 自動解析多個工作表
- 檔案大小最大支援 200MB

### 📊 資料檢視與編輯
- 互動式資料預覽
- 基本資料編輯功能
- 統計分析和視覺化
- 資料篩選和匯出

### 💬 智能問答
- 整合 LangChain 和 OpenAI
- 自然語言資料分析
- 業務指標計算
- 即時對話式查詢

## 🛠 技術架構

- **前端**: Streamlit
- **資料處理**: Pandas, NumPy
- **AI 整合**: LangChain, OpenAI API
- **檔案處理**: openpyxl, xlrd
- **部署**: Streamlit Cloud

## 📦 專案結構

```
HOTAI MOTOR/
├── streamlit_app.py           # 主應用程式
├── requirements.txt           # Python 依賴套件
├── README.md                 # 專案說明文件
├── CLAUDE.md                 # Claude Code 指引
├── .streamlit/
│   └── config.toml           # Streamlit 配置
├── utils/
│   ├── __init__.py
│   ├── data_processor.py     # 資料處理工具
│   └── langchain_integration.py  # LangChain 整合
└── 現有檔案/
    ├── app.py               # 原始 Streamlit 應用
    ├── solution_combine.py   # LangChain 主程式
    ├── solution1.py         # 分析工具 1
    ├── solution3.py         # 分析工具 3
    └── *.xlsx              # 範例資料檔案
```

## 🚀 部署到 Streamlit Cloud

### 步驟 1: 準備 GitHub 儲存庫

1. 在 GitHub 上建立新的儲存庫
2. 將所有檔案上傳到儲存庫，確保包含：
   - `streamlit_app.py` (主要應用程式檔案)
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `utils/` 目錄及所有內容

### 步驟 2: 設定 Streamlit Cloud

1. 前往 [share.streamlit.io](https://share.streamlit.io)
2. 使用 GitHub 帳戶登入
3. 點擊 "New app"
4. 選擇您的 GitHub 儲存庫
5. 設定以下參數：
   - **Repository**: 您的儲存庫名稱
   - **Branch**: `main` 或 `master`
   - **Main file path**: `streamlit_app.py`

### 步驟 3: 環境變數設定

在 Streamlit Cloud 的 App settings → Advanced settings → Secrets 中新增：

```toml
# .streamlit/secrets.toml 格式
OPENAI_API_KEY = "your-openai-api-key-here"

# 可選的其他設定
[general]
app_name = "HOTAI MOTOR Analysis Platform"
version = "1.0.0"
```

### 步驟 4: 部署確認

1. 點擊 "Deploy" 按鈕
2. 等待應用程式建置完成（通常需要 2-5 分鐘）
3. 檢查應用程式是否正常運行
4. 測試所有功能：檔案上傳、資料檢視、AI 問答

## 🔧 本地開發環境設定

### 環境需求
- Python 3.8+
- pip 套件管理器

### 安裝步驟

```bash
# 1. 複製專案
git clone <your-repository-url>
cd HOTAI-MOTOR

# 2. 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 安裝依賴套件
pip install -r requirements.txt

# 4. 設定環境變數
# 建立 .streamlit/secrets.toml 檔案
mkdir .streamlit
echo 'OPENAI_API_KEY = "your-api-key-here"' > .streamlit/secrets.toml

# 5. 執行應用程式
streamlit run streamlit_app.py
```

## 🔑 API Key 管理

### 取得 OpenAI API Key
1. 前往 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登入您的帳戶
3. 建立新的 API Key
4. 複製 API Key（請妥善保存，它只會顯示一次）

### 設定方式

#### 本地開發
在 `.streamlit/secrets.toml` 中設定：
```toml
OPENAI_API_KEY = "sk-your-api-key-here"
```

#### Streamlit Cloud 部署
在 App settings → Advanced settings → Secrets 中設定：
```toml
OPENAI_API_KEY = "sk-your-api-key-here"
```

## 📝 使用說明

### 1. 資料上傳
1. 選擇「📤 資料上傳」頁面
2. 拖拽或選擇 Excel/CSV 檔案
3. 等待上傳完成
4. 檢視檔案摘要

### 2. 資料檢視與編輯
1. 選擇「📊 資料檢視與編輯」頁面
2. 選擇檔案和工作表
3. 使用各種分析工具：
   - 資料預覽
   - 基本編輯
   - 統計分析
   - 資料篩選

### 3. 智能問答
1. 選擇「💬 智能問答」頁面
2. 確認已設定 OpenAI API Key
3. 在聊天框中輸入問題
4. 等待 AI 分析回應

## 🔧 進階配置

### 自定義主題
在 `.streamlit/config.toml` 中修改：
```toml
[theme]
primaryColor = "#1f77b4"      # 主要顏色
backgroundColor = "#ffffff"    # 背景顏色
secondaryBackgroundColor = "#f0f2f6"  # 次要背景顏色
textColor = "#262730"         # 文字顏色
```

### 效能優化
```toml
[server]
maxUploadSize = 200          # 檔案上傳大小限制 (MB)
enableCORS = true            # 啟用 CORS
enableWebsocketCompression = true  # 啟用 WebSocket 壓縮
```

## 🐛 疑難排解

### 常見問題

#### 1. LangChain 相關錯誤
**問題**: `ModuleNotFoundError: No module named 'langchain'`
**解決**: 確認 requirements.txt 包含所有必要套件並重新安裝

#### 2. OpenAI API 錯誤
**問題**: `openai.error.AuthenticationError`
**解決**: 檢查 API Key 是否正確設定在環境變數中

#### 3. 檔案上傳失敗
**問題**: 檔案上傳時出現錯誤
**解決**: 
- 檢查檔案大小是否超過 200MB
- 確認檔案格式為 .xlsx, .xls, 或 .csv
- 檢查檔案是否損壞

#### 4. 應用程式載入緩慢
**解決**:
- 檢查網路連線
- 減少上傳檔案大小
- 清除瀏覽器快取

## 📊 效能指標

- **檔案上傳**: 支援最大 200MB
- **資料處理**: 支援百萬行級別資料
- **回應時間**: AI 問答通常 3-10 秒
- **並發支援**: Streamlit Cloud 預設支援多用戶

## 🔄 更新與維護

### 版本更新
1. 修改程式碼
2. 更新 `requirements.txt`（如有新依賴）
3. 提交到 GitHub
4. Streamlit Cloud 會自動重新部署

### 監控與除錯
- 檢查 Streamlit Cloud 的 logs
- 使用瀏覽器開發者工具檢查前端錯誤
- 監控 OpenAI API 使用量和成本

## 📞 支援與聯絡

如有問題或建議，請聯絡開發團隊或在 GitHub 上提交 issue。

## 📜 授權條款

本專案採用 MIT License 授權。