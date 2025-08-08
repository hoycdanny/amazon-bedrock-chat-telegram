# Telegram Bedrock Chat Bot

一個整合了 AWS Bedrock Claude 3.5 Haiku 的 Telegram 聊天機器人，透過 [bedrock-chat](https://github.com/aws-samples/bedrock-chat) API 提供智能對話功能。

## 🚀 功能特色

- **智能對話**: 使用 Claude 3.5 Haiku 模型提供高質量的 AI 回應
- **即時回應**: 優化的輪詢機制，AI 完成回應後立即發送
- **用戶授權**: 支持指定用戶授權使用
- **打字指示器**: 處理過程中顯示打字狀態
- **錯誤處理**: 完善的錯誤處理和日誌記錄
- **簡潔配置**: 僅保留必要配置，易於部署和維護

## 📋 系統需求

- Python 3.8+
- AWS 帳號（用於部署 bedrock-chat API）
- Telegram 帳號（用於創建機器人）

## 🏗️ 完整部署流程

### 第一步：部署 AWS Bedrock Chat API

在開始之前，你需要先部署 bedrock-chat API 服務。

#### 1.1 克隆 bedrock-chat 專案

```bash
git clone https://github.com/aws-samples/bedrock-chat.git
cd bedrock-chat
```

#### 1.2 部署到 AWS

按照 bedrock-chat 專案的 README 指示進行部署：

1. **安裝 AWS CDK**（如果尚未安裝）：
   ```bash
   npm install -g aws-cdk
   ```

2. **配置 AWS 認證**：
   ```bash
   aws configure
   ```
   輸入你的 AWS Access Key ID、Secret Access Key 和預設區域。

3. **部署 CDK Stack**：
   ```bash
   # 安裝依賴
   npm install
   
   # 首次部署需要 bootstrap
   cdk bootstrap
   
   # 部署
   cdk deploy
   ```

4. **記錄 API 端點**：
   部署完成後，CDK 會輸出 API Gateway 的端點 URL，類似：
   ```
   ✅  BedrockChatStack
   
   Outputs:
   BedrockChatStack.ApiEndpoint = https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod
   ```
   
   **重要**: 請記錄這個 URL，稍後會用到。

#### 1.3 測試 API 是否正常運作

```bash
curl -X POST https://your-api-endpoint.execute-api.us-east-1.amazonaws.com/prod/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

如果回應正常，表示 API 部署成功。

### 第二步：創建 Telegram 機器人

#### 2.1 與 BotFather 對話

1. 在 Telegram 中搜尋並開啟 [@BotFather](https://t.me/BotFather)
2. 發送 `/start` 開始對話

#### 2.2 創建新機器人

1. 發送 `/newbot` 命令
2. BotFather 會要求你提供機器人名稱：
   ```
   Alright, a new bot. How are we going to call it? Please choose a name for your bot.
   ```
   輸入你想要的機器人顯示名稱，例如：`My Bedrock Chat Bot`

3. 接著要求提供用戶名（必須以 `bot` 結尾）：
   ```
   Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot.
   ```
   輸入用戶名，例如：`my_bedrock_chat_bot`

#### 2.3 獲取 Bot Token

創建成功後，BotFather 會提供你的 Bot Token：
```
Done! Congratulations on your new bot. You will find it at t.me/my_bedrock_chat_bot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

**重要**: 請安全保存這個 Token，不要分享給他人。


### 第三步：獲取 Telegram 用戶 ID

為了設定授權用戶，你需要獲取 Telegram 用戶 ID。

#### 3.1 使用 GetIDs Bot

1. 在 Telegram 中搜尋並開啟 [@getidsbot](https://t.me/getidsbot)
2. 發送 `/start` 或任意訊息
3. 機器人會回覆你的用戶資訊：
   ```
   🆔 Your ID: 123456789
   👤 First Name: John
   👤 Username: @john_doe
   🌐 Language: en
   ```

4. 記錄你的用戶 ID（例如：`123456789`）

#### 3.2 獲取其他用戶 ID（如果需要）

如果你想授權其他用戶使用機器人：
1. 請他們也與 [@getidsbot](https://t.me/getidsbot) 對話
2. 獲取他們的用戶 ID
3. 將所有授權用戶的 ID 記錄下來

### 第四步：設定本地專案

#### 4.1 克隆本專案

```bash
git clone https://github.com/hoycdanny/amazon-bedrock-chat-telegram.git
cd amazon-bedrock-chat-telegram
```

#### 4.2 安裝 Python 依賴

```bash
# 建議使用虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements.txt
```

#### 4.3 配置環境變數

1. **複製環境變數範例**：
   ```bash
   cp .env.example .env
   ```

2. **編輯 `.env` 文件**：
   ```bash
   nano .env  # 或使用你喜歡的編輯器
   ```

3. **填入實際配置**：
   ```env
   # Telegram Bot Configuration
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   
   # bedrock-chat API Configuration  
   BEDROCK_CHAT_API_URL=https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod
   BEDROCK_CHAT_API_TOKEN=
   BEDROCK_CHAT_TIMEOUT=30
   
   # Security Configuration (用逗號分隔多個用戶 ID)
   AUTHORIZED_USERS=123456789,987654321
   
   # System Configuration
   LOG_LEVEL=INFO
   ```

   **配置說明**：
   - `TELEGRAM_BOT_TOKEN`: 從 BotFather 獲得的 Token
   - `BEDROCK_CHAT_API_URL`: 從 CDK 部署輸出獲得的 API 端點
   - `BEDROCK_CHAT_API_TOKEN`: 通常留空（除非你的 API 需要額外認證）
   - `AUTHORIZED_USERS`: 從 @getidsbot 獲得的用戶 ID 列表

### 第五步：測試和運行

#### 5.1 運行機器人

```bash
python main.py
```

成功啟動會看到：
```
🚀 Telegram Bot 正在啟動 (Polling 模式)...
🤖 Bot 用戶名: @my_bedrock_chat_bot
📱 現在可以在 Telegram 中發送訊息測試了！
⏹️  按 Ctrl+C 停止 bot
```

#### 5.2 測試機器人

1. 在 Telegram 中搜尋你的機器人（例如：`@my_bedrock_chat_bot`）
2. 發送 `/start` 開始對話
3. 發送任意訊息測試 AI 回應功能

#### 5.3 驗證授權功能

- 使用授權用戶帳號測試：應該能正常對話
- 使用未授權帳號測試：應該收到權限拒絕訊息
#
# 🎯 使用方法

### 基本指令

- `/start` - 開始使用機器人
- `/help` - 顯示幫助訊息
- `/status` - 檢查服務狀態

### 對話功能

直接發送任何文字訊息給機器人，它會透過 AWS Bedrock Chat API 使用 Claude 3.5 Haiku 來回應你的問題。

### 使用流程

1. **開始對話**: 在 Telegram 中找到你的機器人並發送 `/start`
2. **發送訊息**: 直接輸入你想問的問題或想聊的內容
3. **等待回應**: 機器人會顯示「正在輸入...」狀態，然後回傳 AI 生成的回應
4. **繼續對話**: 可以持續對話，每次都會獲得智能回應

## ⚙️ 配置說明

### 環境變數詳解

| 變數名 | 必填 | 說明 | 範例 | 獲取方式 |
|--------|------|------|------|----------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Telegram Bot 的認證 Token | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` | 從 [@BotFather](https://t.me/BotFather) 創建機器人時獲得 |
| `BEDROCK_CHAT_API_URL` | ✅ | Bedrock Chat API 的端點 URL | `https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod` | 從 bedrock-chat CDK 部署輸出獲得 |
| `BEDROCK_CHAT_API_TOKEN` | ❌ | API 認證 Token（通常留空） | `your-api-token` | 如果 API 需要額外認證才填入 |
| `BEDROCK_CHAT_TIMEOUT` | ❌ | API 請求超時時間（秒） | `30` | 根據需要調整，預設 30 秒 |
| `AUTHORIZED_USERS` | ❌ | 授權用戶 ID 列表（逗號分隔） | `123456789,987654321` | 從 [@getidsbot](https://t.me/getidsbot) 獲得用戶 ID |
| `LOG_LEVEL` | ❌ | 日誌級別 | `INFO` | 可選：DEBUG, INFO, WARNING, ERROR |

### 授權設定

- 如果 `AUTHORIZED_USERS` 為空，所有用戶都可以使用
- 如果設定了用戶 ID，只有列表中的用戶可以使用機器人
- 多個用戶 ID 用逗號分隔，不要有空格

## 🏗️ 專案結構

```
amazon-bedrock-chat-telegram/
├── main.py                          # 主程式入口
├── requirements.txt                 # Python 依賴
├── .env.example                     # 環境變數範例
├── .gitignore                      # Git 忽略文件
├── README.md                       # 專案說明
└── telegram_bot/                   # 機器人模組
    ├── __init__.py
    ├── config/                     # 配置管理
    │   ├── __init__.py
    │   └── settings.py            # 設定類別
    └── services/                   # 服務層
        ├── __init__.py
        └── bedrock_service.py     # Bedrock API 服務
```

## 🔧 開發指南

### 本地開發

1. 創建虛擬環境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

2. 安裝開發依賴：
```bash
pip install -r requirements.txt
```

3. 運行測試：
```bash
python main.py
```

### 日誌查看

機器人會輸出詳細的運行日誌，包括：
- 用戶訊息接收
- API 請求狀態
- 回應處理時間
- 錯誤訊息



## 🔗 相關連結

- [AWS Bedrock Chat 專案](https://github.com/aws-samples/bedrock-chat)
- [Telegram Bot API 文檔](https://core.telegram.org/bots/api)
- [AWS Bedrock 文檔](https://docs.aws.amazon.com/bedrock/)
- [AWS CDK 文檔](https://docs.aws.amazon.com/cdk/)