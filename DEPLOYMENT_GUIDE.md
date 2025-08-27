# 🚀 Streamlit Cloud 部署指南

本指南將詳細說明如何將 HOTAI MOTOR 銷售數據分析平台部署到 Streamlit Cloud。

## 📋 部署前檢查清單

在開始部署前，請確認以下項目：

- [ ] 擁有 GitHub 帳戶
- [ ] 擁有 OpenAI API Key
- [ ] 所有必要檔案已準備完成
- [ ] 本地測試已通過

## 🗂 必要檔案清單

確保您的專案包含以下檔案：

```
專案根目錄/
├── streamlit_app.py          ✅ 主應用程式（必要）
├── requirements.txt          ✅ 依賴套件（必要）
├── README.md                ✅ 說明文件（建議）
├── .streamlit/
│   └── config.toml          ✅ 配置檔案（建議）
├── utils/
│   ├── __init__.py          ✅ 工具模組（必要）
│   ├── data_processor.py    ✅ 資料處理（必要）
│   └── langchain_integration.py ✅ AI 整合（必要）
└── [其他檔案]               ⚠️  可選
```

## 1️⃣ 步驟一：準備 GitHub 儲存庫

### 1.1 建立新儲存庫

1. 前往 [GitHub](https://github.com) 並登入
2. 點擊右上角的 "+" → "New repository"
3. 設定儲存庫資訊：
   - **Repository name**: `hotai-motor-analysis`（或您喜歡的名稱）
   - **Description**: `HOTAI MOTOR Sales Data Analysis Platform`
   - **Public/Private**: 選擇 Public（Streamlit Cloud 免費版需要 Public repo）
   - **Initialize with README**: 不勾選（我們已有 README.md）

4. 點擊 "Create repository"

### 1.2 上傳檔案到 GitHub

#### 方法 A：使用 Git 命令列
```bash
# 在專案目錄中執行
git init
git add .
git commit -m "Initial commit: Add Streamlit app for HOTAI MOTOR analysis"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/hotai-motor-analysis.git
git push -u origin main
```

#### 方法 B：使用 GitHub Web 介面
1. 在 GitHub 儲存庫頁面點擊 "uploading an existing file"
2. 拖拽所有專案檔案到上傳區域
3. 輸入 commit message: "Initial commit: Add Streamlit app"
4. 點擊 "Commit changes"

### 1.3 驗證上傳結果

確認 GitHub 儲存庫包含所有必要檔案，特別是：
- `streamlit_app.py` 在根目錄
- `requirements.txt` 在根目錄
- `.streamlit/config.toml` 在正確路徑

## 2️⃣ 步驟二：設定 Streamlit Cloud

### 2.1 登入 Streamlit Cloud

1. 前往 [share.streamlit.io](https://share.streamlit.io)
2. 點擊 "Sign up" 或 "Sign in with GitHub"
3. 授權 Streamlit 存取您的 GitHub 帳戶

### 2.2 建立新應用程式

1. 點擊 "New app" 按鈕
2. 填寫應用程式設定：

   **Repository 設定**
   - **Repository**: 選擇您剛建立的儲存庫
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`

   **App 設定**
   - **App name**: `hotai-motor-analysis`（或自定義名稱）

3. 點擊 "Deploy!" 按鈕

## 3️⃣ 步驟三：環境變數設定

### 3.1 取得 OpenAI API Key

1. 前往 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登入您的 OpenAI 帳戶
3. 點擊 "Create new secret key"
4. 為 API Key 命名（例如：`hotai-streamlit-app`）
5. **重要**: 立即複製 API Key，它只會顯示一次！

### 3.2 在 Streamlit Cloud 設定密鑰

1. 在 Streamlit Cloud 應用程式頁面，點擊右下角的 "⚙️" (Settings)
2. 選擇 "Secrets"
3. 在文字框中輸入以下內容：

```toml
OPENAI_API_KEY = "sk-your-actual-api-key-here"

# 可選的其他設定
[general]
app_name = "HOTAI MOTOR Analysis Platform"
version = "1.0.0"
debug_mode = false
```

4. 點擊 "Save"

### 3.3 驗證環境變數

設定完成後，應用程式會自動重新部署。檢查：
1. 應用程式重新啟動
2. 沒有顯示 API Key 相關錯誤訊息
3. AI 問答功能可以正常使用

## 4️⃣ 步驟四：部署驗證與測試

### 4.1 等待部署完成

- 初次部署通常需要 3-8 分鐘
- 在 Streamlit Cloud 介面可以看到建置進度
- 如果出現錯誤，檢查 logs 區域

### 4.2 功能測試

部署完成後，請依序測試所有功能：

1. **基本載入測試**
   - [ ] 應用程式能正常開啟
   - [ ] 所有頁面可以正常切換
   - [ ] 沒有明顯的錯誤訊息

2. **檔案上傳測試**
   - [ ] 可以上傳 Excel 檔案
   - [ ] 可以上傳 CSV 檔案
   - [ ] 檔案解析正確
   - [ ] 多工作表檔案處理正常

3. **資料檢視測試**
   - [ ] 資料預覽功能正常
   - [ ] 統計分析顯示正確
   - [ ] 篩選功能運作正常
   - [ ] 資料匯出功能正常

4. **AI 問答測試**
   - [ ] OpenAI 連接成功
   - [ ] 可以提問並收到回應
   - [ ] 聊天記錄正常保存
   - [ ] 沒有 API 相關錯誤

### 4.3 效能測試

1. **檔案大小測試**
   - 測試上傳不同大小的檔案（1MB, 10MB, 50MB）
   - 確認在限制範圍內能正常處理

2. **資料量測試**
   - 測試不同行數的資料（1000行、10000行、100000行）
   - 檢查載入速度和回應性

3. **並發測試**
   - 同時開啟多個瀏覽器標籤
   - 確認 session state 隔離正常

## 5️⃣ 進階設定

### 5.1 自定義域名（付費功能）

如果您有 Streamlit Cloud 付費方案：

1. 在 App settings → General 中
2. 設定 Custom domain
3. 按照指引設定 DNS

### 5.2 資源限制調整

在 `.streamlit/config.toml` 中調整：

```toml
[server]
maxUploadSize = 200
maxMessageSize = 200

[global]
maxCachedMessageAge = 0
```

### 5.3 監控和日誌

1. **應用程式監控**
   - 在 Streamlit Cloud dashboard 檢查應用程式狀態
   - 監控 CPU 和記憶體使用量

2. **錯誤日誌**
   - 點擊 "View logs" 檢查即時日誌
   - 監控錯誤和警告訊息

3. **API 使用監控**
   - 在 OpenAI dashboard 監控 API 使用量
   - 設定使用量警報

## 🔧 疑難排解

### 常見部署問題

#### 問題 1: 應用程式無法啟動
```
錯誤: ModuleNotFoundError: No module named 'xxx'
```
**解決方案**:
1. 檢查 `requirements.txt` 是否包含所有必要套件
2. 確認套件版本相容性
3. 在本地環境測試 `pip install -r requirements.txt`

#### 問題 2: OpenAI API 連接失敗
```
錯誤: openai.error.AuthenticationError
```
**解決方案**:
1. 檢查 Secrets 中的 API Key 是否正確
2. 確認 API Key 格式：`sk-...`
3. 檢查 OpenAI 帳戶餘額

#### 問題 3: 檔案上傳錯誤
```
錯誤: File upload failed
```
**解決方案**:
1. 檢查檔案大小是否超過 200MB
2. 確認檔案格式支援
3. 檢查 `.streamlit/config.toml` 設定

#### 問題 4: 記憶體不足
```
錯誤: Memory limit exceeded
```
**解決方案**:
1. 優化資料處理邏輯
2. 使用資料分塊處理
3. 清理不必要的快取

### 除錯步驟

1. **檢查 Streamlit logs**
   ```
   在 Streamlit Cloud → App → View logs
   ```

2. **本地測試**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **依賴套件檢查**
   ```bash
   pip install -r requirements.txt
   python -c "import streamlit, pandas, openai, langchain"
   ```

## 📊 部署後維護

### 日常監控

1. **每日檢查**
   - 應用程式可用性
   - 錯誤日誌
   - API 使用量

2. **每週檢查**
   - 效能指標
   - 用戶回饋
   - 安全性更新

3. **每月檢查**
   - 依賴套件更新
   - 功能使用統計
   - 成本分析

### 更新流程

1. **程式碼更新**
   ```bash
   git add .
   git commit -m "Update: 描述更新內容"
   git push origin main
   ```

2. **依賴套件更新**
   - 更新 `requirements.txt`
   - 在 Streamlit Cloud 觸發重新部署

3. **設定更新**
   - 修改 Secrets 或 config.toml
   - 重啟應用程式

## ✅ 部署成功確認

完成所有步驟後，您的應用程式應該：

- [ ] 可以通過公開 URL 正常存取
- [ ] 所有功能正常運作
- [ ] 沒有錯誤或警告訊息
- [ ] API 連接穩定
- [ ] 效能表現良好

恭喜！您已成功將 HOTAI MOTOR 銷售數據分析平台部署到 Streamlit Cloud。

## 📞 取得幫助

如果遇到問題：

1. **Streamlit 官方文件**: [docs.streamlit.io](https://docs.streamlit.io)
2. **Streamlit 社群**: [discuss.streamlit.io](https://discuss.streamlit.io)
3. **GitHub Issues**: 在專案儲存庫提交問題
4. **OpenAI 支援**: [help.openai.com](https://help.openai.com)

---

**注意**: 請妥善保管您的 API Key，不要在程式碼中明碼儲存，並定期檢查 API 使用量以避免意外費用。