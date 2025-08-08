"""
bedrock-chat API service for generating responses.
"""

import httpx
import asyncio
import structlog
from typing import Dict, Any, Optional, List
from telegram_bot.config import Settings


logger = structlog.get_logger()


class BedrockChatService:
    """Service for interacting with the bedrock-chat API."""
    
    def __init__(self, config: Settings):
        self.config = config
        self.api_url = config.bedrock_chat_api_url
        self.api_token = config.bedrock_chat_api_token
        self.timeout = httpx.Timeout(30.0)
        self.enable_streaming = getattr(config, 'enable_streaming', False)
    
    async def get_chat_response(self, message: str, user_id: int) -> str:
        """Get response from bedrock-chat API."""
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            if self.api_token:
                headers["x-api-key"] = self.api_token
            
            conversation_id = str(user_id)
            
            payload = {
                "conversation_id": conversation_id,
                "message": {
                    "role": "user",
                    "content": [
                        {
                            "content_type": "text",
                            "body": message
                        }
                    ],
                    "model": "claude-v3.5-haiku"
                },
                "bot_id": None,
                "continue_generate": False
            }
            
            logger.info("Sending request to bedrock-chat API", 
                       message_length=len(message),
                       user_id=user_id,
                       conversation_id=conversation_id)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Send message and get the user message ID
                response = await client.post(
                    f"{self.api_url}/conversation",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                result = response.json()
                user_message_id = result.get("messageId")
                logger.info("Message sent successfully", 
                           conversation_id=result.get("conversationId"),
                           message_id=user_message_id)
                
                if not user_message_id:
                    raise Exception("No message ID returned from API")
                
                # Prepare headers for polling
                get_headers = {"Accept": "application/json"}
                if self.api_token:
                    get_headers["x-api-key"] = self.api_token
                
                # Smart polling for AI response
                logger.info("Starting smart polling for AI response...")
                return await self._poll_for_response(client, conversation_id, user_message_id, get_headers)
                
        except httpx.TimeoutException:
            logger.error("Request timeout")
            raise Exception("Request timeout - please try again")
            
        except httpx.RequestError as e:
            logger.error(f"API request error: {str(e)}")
            raise Exception(f"API request error: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error getting chat response: {str(e)}")
            raise Exception(f"Error getting chat response: {str(e)}")
    
    async def _poll_for_response(self, client: httpx.AsyncClient, conversation_id: str, 
                                user_message_id: str, headers: Dict[str, str]) -> str:
        """智能輪詢 - 當 AI 完成時立即回應"""
        max_attempts = 60
        
        logger.info(f"🔄 開始智能輪詢 (最多 {max_attempts} 次嘗試)")
        
        for attempt in range(max_attempts):
            try:
                # 階段性延遲策略
                if attempt == 0:
                    delay = 0.5  # 第一次快速檢查
                elif attempt < 10:
                    delay = 0.5  # 前 10 次，每 0.5 秒
                elif attempt < 30:
                    delay = 1.0  # 接下來 20 次，每 1 秒
                else:
                    delay = 2.0  # 最後 30 次，每 2 秒
                
                if attempt > 0:
                    await asyncio.sleep(delay)
                
                # 每 10 次嘗試記錄一次進度
                if attempt % 10 == 0 or attempt < 5:
                    logger.info(f"🔍 輪詢進度: {attempt + 1}/{max_attempts} (延遲: {delay}s)")
                
                # 檢查 AI 回應
                conv_response = await client.get(
                    f"{self.api_url}/conversation/{conversation_id}",
                    headers=headers
                )
                conv_response.raise_for_status()
                
                conv_data = conv_response.json()
                message_map = conv_data.get("messageMap", {})
                
                # 尋找 AI 回應
                for msg_id, msg_data in message_map.items():
                    if (msg_data.get("role") == "assistant" and 
                        msg_id != "system" and 
                        msg_data.get("parent") == user_message_id):
                        
                        content_list = msg_data.get("content", [])
                        for content_item in content_list:
                            if content_item.get("contentType") == "text":
                                response_text = content_item.get("body", "").strip()
                                if response_text:
                                    logger.info(f"✅ AI 回應完成！嘗試: {attempt + 1}次")
                                    return response_text
                
            except Exception as e:
                logger.warning(f"⚠️  輪詢嘗試 {attempt + 1} 失敗: {e}")
                if attempt == max_attempts - 1:
                    raise
                await asyncio.sleep(0.5)  # 錯誤後短暫暫停
        
        logger.error(f"❌ 經過 {max_attempts} 次嘗試仍未獲得回應")
        raise Exception("AI 回應超時 - 請重試")


    async def health_check(self) -> bool:
        """Check if the bedrock-chat API is healthy."""
        try:
            headers = {}
            if self.api_token:
                headers["x-api-key"] = self.api_token
                
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                response = await client.get(f"{self.api_url}/health", headers=headers)
                return response.status_code == 200
        except Exception:
            return False
