"""
即时通讯路由组件
提供实时消息推送、历史消息查询、消息发送等 API 接口
零侵入实现 - 使用 send_api 和 message_api 公开接口
"""

import time
from typing import Any, Optional

from fastapi import Query, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from pydantic import BaseModel

from src.common.logger import get_logger
from src.common.security import VerifiedDep
from src.plugin_system import BaseRouterComponent
from src.plugin_system.apis import send_api, message_api

from ..utils.message_broadcaster import get_message_broadcaster

logger = get_logger("WebUI.LiveChatRouter")


# ==================== 请求/响应模型 ====================


class SendMessageRequest(BaseModel):
    """发送消息请求"""

    stream_id: str
    content: str
    message_type: str = "text"  # text, image, emoji, file
    image_base64: Optional[str] = None
    reply_to_id: Optional[str] = None  # 引用消息ID


class StreamInfo(BaseModel):
    """聊天流信息"""

    stream_id: str
    platform: Optional[str] = None
    user_id: Optional[str] = None
    user_nickname: Optional[str] = None
    group_id: Optional[str] = None
    group_name: Optional[str] = None
    last_active_time: Optional[float] = None


class StreamsResponse(BaseModel):
    """聊天流列表响应"""

    success: bool
    streams: list[StreamInfo]
    count: int


class MessageInfo(BaseModel):
    """消息信息"""

    message_id: Optional[str] = None
    stream_id: Optional[str] = None
    user_id: Optional[str] = None
    user_nickname: Optional[str] = None
    content: Optional[str] = None
    timestamp: Optional[float] = None
    is_emoji: bool = False
    is_picid: bool = False
    reply_to_id: Optional[str] = None
    direction: str = "incoming"
    sender_type: str = "user"


class MessagesResponse(BaseModel):
    """消息列表响应"""

    success: bool
    messages: list[MessageInfo]
    count: int


class SendResponse(BaseModel):
    """发送消息响应"""

    success: bool
    error: Optional[str] = None


class ImageResponse(BaseModel):
    """图片响应"""

    success: bool
    data: Optional[str] = None
    error: Optional[str] = None


class ReplyMessageResponse(BaseModel):
    """被引用消息响应"""

    success: bool
    message: Optional[MessageInfo] = None
    error: Optional[str] = None


# ==================== 路由组件 ====================


class LiveChatRouterComponent(BaseRouterComponent):
    """
    即时通讯路由组件

    功能:
    1. WebSocket 实时消息推送
    2. 获取活跃聊天流列表
    3. 获取历史消息
    4. 发送消息到指定聊天流
    5. 获取图片/表情包

    零侵入原理:
    - 使用 send_api 发送消息（MoFox-Bot 公开接口）
    - 使用 message_api 查询消息（MoFox-Bot 公开接口）
    - 数据库只读查询
    """

    component_name = "live_chat"
    component_description = "WebUI 即时通讯接口"
    component_version = "1.0.0"

    def register_endpoints(self) -> None:
        """注册所有 HTTP 和 WebSocket 端点"""

        # ==================== 聊天流接口 ====================

        @self.router.get("/streams", response_model=StreamsResponse)
        async def get_streams(
            limit: int = Query(50, ge=1, le=200, description="返回数量限制"),
            platform: Optional[str] = Query(None, description="按平台过滤"),
            _=VerifiedDep,
        ):
            """获取活跃聊天流列表"""
            try:
                from sqlalchemy import select
                from src.common.database.core import get_db_session
                from src.common.database.core.models import ChatStreams

                async with get_db_session() as session:
                    stmt = select(ChatStreams).order_by(
                        ChatStreams.last_active_time.desc()
                    )

                    # 排除 webui_chatroom 平台（WebUI 聊天室）
                    stmt = stmt.where(ChatStreams.platform != "webui_chatroom")
                    stmt = stmt.where(ChatStreams.platform != "ui_chatroom")

                    # 按平台过滤
                    if platform:
                        stmt = stmt.where(ChatStreams.platform == platform)

                    stmt = stmt.limit(limit)
                    result = await session.execute(stmt)
                    streams = result.scalars().all()

                    stream_list = [
                        StreamInfo(
                            stream_id=s.stream_id,
                            platform=s.platform,
                            user_id=s.user_id,
                            user_nickname=s.user_nickname,
                            group_id=s.group_id,
                            group_name=s.group_name,
                            last_active_time=s.last_active_time,
                        )
                        for s in streams
                    ]

                    return StreamsResponse(
                        success=True,
                        streams=stream_list,
                        count=len(stream_list),
                    )

            except Exception as e:
                logger.error(f"获取聊天流列表失败: {e}")
                return StreamsResponse(success=False, streams=[], count=0)

        # ==================== 消息接口 ====================

        @self.router.get("/messages/{stream_id}", response_model=MessagesResponse)
        async def get_messages(
            stream_id: str,
            hours: float = Query(
                24.0, ge=0.1, le=168, description="查询时间范围（小时）"
            ),
            limit: int = Query(100, ge=1, le=500, description="返回数量限制"),
            _=VerifiedDep,
        ):
            """获取指定聊天流的历史消息"""
            try:
                # 使用 message_api 公开接口查询消息
                messages = await message_api.get_recent_messages(
                    chat_id=stream_id,
                    hours=hours,
                    limit=limit,
                )

                message_list = []
                for m in messages:
                    # message_api 返回的是字典列表
                    msg_info = MessageInfo(
                        message_id=m.get("message_id"),
                        stream_id=stream_id,
                        user_id=m.get("user_id"),
                        user_nickname=m.get("user_nickname"),
                        content=m.get("processed_plain_text")
                        or m.get("display_message"),
                        timestamp=m.get("time"),
                        is_emoji=m.get("is_emoji", False),
                        is_picid=m.get("is_picid", False),
                        reply_to_id=m.get("reply_to"),
                        # 历史消息默认为用户发送，后续可以根据 user_id 判断
                        direction="incoming",
                        sender_type="user",
                    )
                    message_list.append(msg_info)

                return MessagesResponse(
                    success=True,
                    messages=message_list,
                    count=len(message_list),
                )

            except Exception as e:
                logger.error(f"获取历史消息失败: {e}")
                return MessagesResponse(success=False, messages=[], count=0)

        @self.router.get(
            "/reply/{stream_id}/{message_id}", response_model=ReplyMessageResponse
        )
        async def get_reply_message(
            stream_id: str,
            message_id: str,
            _=VerifiedDep,
        ):
            """获取被引用的原始消息"""
            try:
                from sqlalchemy import select
                from src.common.database.core import get_db_session
                from src.common.database.core.models import Messages

                async with get_db_session() as session:
                    stmt = select(Messages).where(
                        Messages.message_id == message_id,
                        Messages.chat_id == stream_id,
                    )
                    result = await session.execute(stmt)
                    msg = result.scalar()

                    if msg:
                        return ReplyMessageResponse(
                            success=True,
                            message=MessageInfo(
                                message_id=msg.message_id,
                                stream_id=stream_id,
                                user_id=msg.user_id,
                                user_nickname=msg.user_nickname,
                                content=msg.processed_plain_text,
                                timestamp=msg.time,
                                is_emoji=msg.is_emoji,
                                is_picid=msg.is_picid,
                                reply_to_id=msg.reply_to,
                            ),
                        )
                    else:
                        return ReplyMessageResponse(
                            success=False,
                            error="消息不存在",
                        )

            except Exception as e:
                logger.error(f"获取引用消息失败: {e}")
                return ReplyMessageResponse(success=False, error=str(e))

        # ==================== 发送消息接口 ====================

        @self.router.post("/send", response_model=SendResponse)
        async def send_message(request: SendMessageRequest, _=VerifiedDep):
            """
            发送消息到指定聊天流

            使用 send_api 公开接口，零侵入
            """
            try:
                success = False

                if request.message_type == "text":
                    # 发送文本消息
                    success = await send_api.text_to_stream(
                        text=request.content,
                        stream_id=request.stream_id,
                        storage_message=True,
                    )

                elif request.message_type == "image" and request.image_base64:
                    # 发送图片
                    success = await send_api.image_to_stream(
                        image_base64=request.image_base64,
                        stream_id=request.stream_id,
                    )

                elif request.message_type == "emoji" and request.image_base64:
                    # 发送表情包
                    success = await send_api.emoji_to_stream(
                        emoji_base64=request.image_base64,
                        stream_id=request.stream_id,
                    )

                else:
                    # 其他类型使用 custom_to_stream
                    success = await send_api.custom_to_stream(
                        message_type=request.message_type,
                        content=request.content,
                        stream_id=request.stream_id,
                    )

                if success:
                    logger.info(
                        f"消息已发送: stream_id={request.stream_id}, type={request.message_type}"
                    )
                else:
                    logger.warning(f"消息发送失败: stream_id={request.stream_id}")

                return SendResponse(success=success)

            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                return SendResponse(success=False, error=str(e))

        # ==================== 图片接口 ====================

        @self.router.get("/image/{image_hash}")
        async def get_image(image_hash: str, _=VerifiedDep):
            """获取图片（通过哈希）"""
            try:
                from sqlalchemy import select
                from src.common.database.core import get_db_session
                from src.common.database.core.models import Images
                from src.chat.utils.utils_image import image_path_to_base64

                async with get_db_session() as session:
                    stmt = select(Images).where(Images.emoji_hash == image_hash)
                    result = await session.execute(stmt)
                    image = result.scalar()

                    if image and image.path:
                        try:
                            base64_data = image_path_to_base64(image.path)
                            return ImageResponse(success=True, data=base64_data)
                        except Exception as e:
                            logger.error(f"读取图片文件失败: {e}")
                            return ImageResponse(success=False, error="读取图片失败")

                    return ImageResponse(success=False, error="图片不存在")

            except Exception as e:
                logger.error(f"获取图片失败: {e}")
                return ImageResponse(success=False, error=str(e))

        @self.router.get("/emoji/{emoji_hash}")
        async def get_emoji(emoji_hash: str, _=VerifiedDep):
            """获取表情包（通过哈希）"""
            try:
                from sqlalchemy import select
                from src.common.database.core import get_db_session
                from src.common.database.core.models import Emoji
                from src.chat.utils.utils_image import image_path_to_base64

                async with get_db_session() as session:
                    stmt = select(Emoji).where(Emoji.emoji_hash == emoji_hash)
                    result = await session.execute(stmt)
                    emoji = result.scalar()

                    if emoji and emoji.path:
                        try:
                            base64_data = image_path_to_base64(emoji.path)
                            return ImageResponse(success=True, data=base64_data)
                        except Exception as e:
                            logger.error(f"读取表情包文件失败: {e}")
                            return ImageResponse(success=False, error="读取表情包失败")

                    return ImageResponse(success=False, error="表情包不存在")

            except Exception as e:
                logger.error(f"获取表情包失败: {e}")
                return ImageResponse(success=False, error=str(e))

        # ==================== WebSocket 实时推送 ====================

        @self.router.websocket("/realtime")
        async def websocket_realtime(
            websocket: WebSocket,
            stream_id: Optional[str] = Query(None, description="订阅特定聊天流"),
            token: Optional[str] = Query(None, description="API Token"),
        ):
            """
            WebSocket 实时消息推送

            连接参数:
            - stream_id: 可选，指定只接收某个聊天流的消息
            - token: API Token，用于验证

            客户端消息:
            - "ping": 心跳检测，服务器返回 "pong"
            - {"type": "subscribe", "stream_id": "xxx"}: 动态订阅聊天流
            - {"type": "unsubscribe", "stream_id": "xxx"}: 取消订阅

            服务器推送:
            - {"type": "message", ...}: 新消息
            """
            # 验证 Token
            from src.config.config import global_config as bot_config

            if not token:
                await websocket.close(code=4001, reason="缺少 Token")
                logger.warning("WebSocket 连接被拒绝: 缺少 Token")
                return

            valid_keys = (
                bot_config.plugin_http_system.plugin_api_valid_keys
                if bot_config
                else []
            )
            if not valid_keys or token not in valid_keys:
                await websocket.close(code=4003, reason="无效的 Token")
                logger.warning(f"WebSocket 连接被拒绝: 无效的 Token")
                return

            await websocket.accept()

            # 获取消息广播器
            broadcaster = get_message_broadcaster()

            # 定义消息回调
            async def send_message(msg: dict[str, Any]):
                try:
                    await websocket.send_json(msg)
                except Exception as e:
                    logger.debug(f"发送消息到 WebSocket 失败: {e}")

            # 订阅消息
            await broadcaster.subscribe(send_message, stream_id)

            try:
                # 发送缓存的最近消息
                if stream_id:
                    recent = broadcaster.get_recent_messages_for_stream(stream_id, 50)
                else:
                    recent = broadcaster.get_recent_messages(50)

                for msg in recent:
                    try:
                        await websocket.send_json(msg)
                    except Exception:
                        break

                # 保持连接，处理客户端消息
                while True:
                    try:
                        data = await websocket.receive_text()

                        # 心跳检测
                        if data == "ping":
                            await websocket.send_text("pong")
                            continue

                        # 尝试解析 JSON 命令
                        try:
                            import json

                            cmd = json.loads(data)
                            cmd_type = cmd.get("type")

                            if cmd_type == "subscribe":
                                # 动态订阅
                                new_stream_id = cmd.get("stream_id")
                                if new_stream_id:
                                    await broadcaster.subscribe(
                                        send_message, new_stream_id
                                    )
                                    await websocket.send_json(
                                        {
                                            "type": "subscribed",
                                            "stream_id": new_stream_id,
                                        }
                                    )

                            elif cmd_type == "unsubscribe":
                                # 取消订阅
                                old_stream_id = cmd.get("stream_id")
                                if old_stream_id:
                                    await broadcaster.unsubscribe(
                                        send_message, old_stream_id
                                    )
                                    await websocket.send_json(
                                        {
                                            "type": "unsubscribed",
                                            "stream_id": old_stream_id,
                                        }
                                    )

                        except json.JSONDecodeError:
                            # 非 JSON 消息，忽略
                            pass

                    except WebSocketDisconnect:
                        logger.info("WebSocket 客户端已断开")
                        break
                    except Exception as e:
                        logger.error(f"WebSocket 错误: {e}")
                        break

            finally:
                # 取消订阅
                await broadcaster.unsubscribe(send_message, stream_id)
                logger.debug(f"WebSocket 清理完成, stream_id={stream_id}")
