#!/usr/bin/env python3
"""
Main Telegram Bot application - supports both polling and webhook modes.
"""

import logging
import sys
import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Add the project root to Python path
sys.path.append('.')

from telegram_bot.config import load_config
from telegram_bot.services.bedrock_service import BedrockChatService

# Load environment variables
# 優先載入 .env.local（本地開發用），如果不存在則載入 .env
if os.path.exists('.env.local'):
    load_dotenv('.env.local')
else:
    load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global bedrock service
bedrock_service = None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    welcome_message = f"👋 你好 {user.first_name}!\n\n我是整合了 bedrock-chat API 的 Telegram Bot。\n\n直接發送訊息給我，我會使用 Claude 3.5 Haiku 來回應你！"
    
    try:
        await update.message.reply_text(welcome_message)
        logger.info(f"發送歡迎訊息給用戶 {user.id}")
    except Exception as e:
        logger.error(f"發送歡迎訊息失敗: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = """
🤖 可用指令:
/start - 開始使用
/help - 顯示此幫助訊息
/status - 檢查服務狀態

💬 使用方式:
直接發送任何訊息，我會使用 AI 來回應你！
    """
    try:
        await update.message.reply_text(help_text)
        logger.info(f"發送幫助訊息給用戶 {update.effective_user.id}")
    except Exception as e:
        logger.error(f"發送幫助訊息失敗: {e}")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    try:
        # Test bedrock service
        health = await bedrock_service.health_check()
        status_text = f"🟢 Bot 狀態: 正常運行\n🧠 AI 服務: {'✅ 正常' if health else '❌ 異常'}"
        await update.message.reply_text(status_text)
        logger.info(f"發送狀態訊息給用戶 {update.effective_user.id}")
    except Exception as e:
        logger.error(f"檢查狀態失敗: {e}")
        await update.message.reply_text("❌ 無法檢查服務狀態")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages with instant response when AI completes."""
    user = update.effective_user
    message_text = update.message.text
    
    logger.info(f"📨 收到來自用戶 {user.id} ({user.first_name}) 的訊息: {message_text}")
    
    # Check authorization (optional for testing)
    authorized_users = os.getenv('AUTHORIZED_USERS', '').split(',')
    if authorized_users and str(user.id) not in authorized_users:
        await update.message.reply_text("❌ 抱歉，你沒有使用此 bot 的權限。")
        return
    
    # 立即顯示處理狀態
    status_message = await update.message.reply_text("AI正在處理...")
    start_time = asyncio.get_event_loop().time()
    
    try:
        # 啟動打字指示器
        typing_task = asyncio.create_task(
            _keep_typing(context.bot, update.effective_chat.id)
        )
        
        # 獲取 AI 回應（使用優化的輪詢）
        logger.info(f"🚀 開始為用戶 {user.id} 獲取 AI 回應...")
        ai_response = await bedrock_service.get_chat_response(message_text, user.id)
        
        # 停止打字指示器
        typing_task.cancel()
        
        # 計算處理時間
        end_time = asyncio.get_event_loop().time()
        processing_time = end_time - start_time
        
        # 刪除狀態訊息並發送 AI 回應
        await status_message.delete()
        await update.message.reply_text(ai_response)
        
        logger.info(f"✅ 已發送回應給用戶 {user.id}，處理時間: {processing_time:.1f}秒")
        
    except Exception as e:
        # 停止打字指示器
        if 'typing_task' in locals():
            typing_task.cancel()
            
        logger.error(f"❌ 處理訊息時發生錯誤: {e}")
        error_message = "❌ 抱歉，AI 處理時發生錯誤。請稍後再試。"
        try:
            await status_message.edit_text(error_message)
        except Exception as send_error:
            logger.error(f"發送錯誤訊息失敗: {send_error}")

async def _keep_typing(bot, chat_id: int):
    """Keep sending typing indicator while processing."""
    try:
        while True:
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            await asyncio.sleep(4)  # Telegram typing indicator lasts ~5 seconds
    except asyncio.CancelledError:
        pass  # Task was cancelled, which is expected

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"更新 {update} 導致錯誤 {context.error}")

def main():
    """Main function to run the bot."""
    global bedrock_service
    
    try:
        # Load configuration
        config = load_config()
        logger.info("配置載入成功")
        
        # Initialize bedrock service
        bedrock_service = BedrockChatService(config)
        logger.info("Bedrock 服務初始化完成")
        
        # Create application
        application = Application.builder().token(config.telegram_bot_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_error_handler(error_handler)
        
        logger.info("🚀 Telegram Bot 正在啟動 (Polling 模式)...")
        logger.info(f"🤖 Bot 用戶名: @danny_for_demo_bot")
        logger.info("📱 現在可以在 Telegram 中發送訊息測試了！")
        logger.info("⏹️  按 Ctrl+C 停止 bot")
        
        # Start polling
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except KeyboardInterrupt:
        logger.info("收到停止信號，正在關閉 bot...")
    except Exception as e:
        logger.error(f"啟動 bot 時發生錯誤: {e}")
        raise

if __name__ == "__main__":
    main()