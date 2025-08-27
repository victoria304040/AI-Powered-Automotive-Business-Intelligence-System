# Streamlit Cloud 部署指南

## 🚀 立即部署步驟

### 前置需求檢查
- ✅ GitHub 儲存庫已建立並上傳所有檔案
- ✅ 儲存庫狀態為 Public
- ✅ requirements.txt 編碼正確
- ✅ OpenAI API Key 已準備（可選，用於 AI 功能）

## 📝 步驟 1: 註冊 Streamlit Cloud

### 1.1 前往 Streamlit Cloud
- 🌐 開啟瀏覽器前往：[share.streamlit.io](https://share.streamlit.io)
- 點擊 **"Sign up"** 或 **"Sign in with GitHub"**

### 1.2 GitHub 授權
- 選擇 **"Continue with GitHub"**
- 授權 Streamlit 存取您的 GitHub 帳戶
- 允許存取您的公開儲存庫

### 1.3 帳戶設定
- 完成 Streamlit Cloud 帳戶設定
- 驗證電子郵件地址（如果需要）

## 🔧 步驟 2: 建立新應用程式

### 2.1 開始建立應用程式
- 在 Streamlit Cloud 儀表板點擊 **"New app"**
- 或點擊 **"Create an app"**

### 2.2 儲存庫設定
```
Repository*: 您的GitHub用戶名/hotai-motor-analysis
Branch*: main
Main file path*: streamlit_app.py
App URL (optional): hotai-motor-analysis (或自定義)
```

### 2.3 進階設定 (Advanced settings)
```
Python version: 3.11 (推薦) 或 3.10
```

### 2.4 部署確認
- 檢查所有設定正確
- 點擊 **"Deploy!"** 開始部署

## ⚙️ 步驟 3: 環境變數設定

### 3.1 存取應用程式設定
- 部署開始後，點擊右下角的 **"⚙️ Settings"**
- 選擇 **"Secrets"**

### 3.2 設定 OpenAI API Key（如需 AI 功能）

在 Secrets 文字框中輸入：

```toml
# OpenAI Configuration
OPENAI_API_KEY = "sk-your-actual-openai-api-key-here"

# Optional: App Configuration
[general]
app_name = "HOTAI MOTOR Analysis Platform"
version = "1.0.0"
debug_mode = false
```

### 3.3 儲存設定
- 點擊 **"Save"**
- 應用程式會自動重新部署

## 📊 步驟 4: 監控部署過程

### 4.1 部署狀態監控
- 觀察部署日誌 (Deploy logs)
- 等待狀態變為 **"Your app is live!"**

### 4.2 常見部署時間
- **初次部署**: 3-8 分鐘
- **後續更新**: 1-3 分鐘
- **包含大型套件**: 5-15 分鐘

### 4.3 部署成功指標
```
✅ Status: Your app is running
✅ Health check: Passed
✅ URL: Available and accessible
✅ Logs: No critical errors
```

## 🌐 步驟 5: 測試已部署的應用程式

### 5.1 基本功能測試
1. **檔案上傳測試**
   - 上傳一個 Excel 或 CSV 檔案
   - 確認檔案解析正常

2. **資料檢視測試**  
   - 切換到「資料檢視與編輯」頁面
   - 確認資料正確顯示

3. **AI 問答測試**（如已設定 API Key）
   - 切換到「智能問答」頁面
   - 嘗試提問並確認回應

### 5.2 效能測試
- 測試頁面載入速度
- 檢查檔案上傳響應時間
- 確認多用戶存取穩定性

## 🔑 步驟 6: 取得 OpenAI API Key（可選）

### 6.1 前往 OpenAI Platform
- 🌐 開啟：[platform.openai.com](https://platform.openai.com)
- 登入或註冊 OpenAI 帳戶

### 6.2 建立 API Key
1. 前往 **"API keys"** 頁面
2. 點擊 **"Create new secret key"**
3. 命名：`hotai-streamlit-app`
4. **立即複製並保存**（只會顯示一次！）

### 6.3 設定使用限制（推薦）
- 前往 **"Usage limits"**
- 設定月度使用限制（例如 $10-50）
- 設定使用警報

### 6.4 更新 Streamlit Cloud Secrets
返回 Streamlit Cloud 應用程式設定，更新 Secrets：
```toml
OPENAI_API_KEY = "sk-your-new-api-key-here"
```

## 🎯 步驟 7: 應用程式優化

### 7.1 自定義域名（付費功能）
- 升級到 Streamlit Cloud Pro
- 設定自定義域名

### 7.2 效能監控
```
監控指標：
- 應用程式回應時間
- 記憶體使用量
- API 呼叫次數
- 用戶活動統計
```

### 7.3 版本管理
- GitHub 更新會自動觸發重新部署
- 使用 Git tags 管理版本
- 監控部署歷史

## 🛠 疑難排解

### 常見問題 1: 部署失敗

**症狀**: 部署停滯在 "Building..."
```bash
解決方案：
1. 檢查 requirements.txt 語法正確性
2. 確認所有依賴套件可安裝
3. 檢查 Python 版本相容性
4. 查看詳細錯誤日誌
```

**症狀**: "ModuleNotFoundError"
```bash
解決方案：
1. 檢查 requirements.txt 是否包含所有套件
2. 確認套件名稱拼寫正確
3. 檢查套件版本相容性
```

### 常見問題 2: 應用程式運行錯誤

**症狀**: "OpenAI API Error"  
```bash
解決方案：
1. 檢查 OPENAI_API_KEY 是否正確設定
2. 確認 API Key 有足夠額度
3. 檢查 API Key 權限設定
4. 驗證網路連接
```

**症狀**: 檔案上傳失敗
```bash
解決方案：
1. 檢查檔案大小是否超過 200MB
2. 確認檔案格式支援
3. 檢查瀏覽器相容性
```

### 常見問題 3: 效能問題

**症狀**: 應用程式載入緩慢
```bash
解決方案：
1. 優化 requirements.txt，移除不必要套件
2. 使用 @st.cache_data 快取資料
3. 分批處理大型資料集
4. 優化程式碼邏輯
```

## 📈 使用統計和監控

### 應用程式分析
Streamlit Cloud 提供：
- 用戶訪問統計
- 應用程式使用時間
- 錯誤率監控
- 效能指標

### API 使用監控
OpenAI Dashboard 提供：
- Token 使用量統計
- API 呼叫次數
- 費用追蹤
- 使用趨勢分析

## 🔄 更新和維護

### 程式碼更新流程
```bash
# 本地更新程式碼
git add .
git commit -m "Update: 描述更新內容"
git push origin main

# Streamlit Cloud 會自動檢測並重新部署
```

### 定期維護檢查清單
- [ ] 監控 API 使用量和費用
- [ ] 檢查應用程式錯誤日誌
- [ ] 更新依賴套件版本
- [ ] 備份重要設定和資料
- [ ] 檢查安全性更新

## 🎉 部署完成

### 成功指標
- ✅ 應用程式可正常存取
- ✅ 所有功能運作正常
- ✅ 沒有嚴重錯誤
- ✅ 效能表現良好

### 分享應用程式
您的應用程式將可在以下網址存取：
```
https://hotai-motor-analysis.streamlit.app
```
或您設定的自定義 URL。

### 後續推廣
- 分享 URL 給客戶測試
- 收集用戶回饋
- 根據需求持續優化
- 考慮升級到付費方案以獲得更多功能

---

## 🏆 恭喜！

您的 **HOTAI MOTOR 銷售數據分析平台** 現已成功部署到 Streamlit Cloud，可以開始為客戶提供專業的 AI 驅動數據分析服務！

**立即存取**: 部署完成後，請將應用程式 URL 提供給客戶進行測試。