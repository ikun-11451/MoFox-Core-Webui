"""
消息广播器
用于实时推送聊天消息到 WebSocket 客户端
零侵入实现 - 不修改 MMC 核心代码
"""

import asyncio
from collections import deque
from collections.abc import Callable, Coroutine
from typing import Any, Union

from src.common.logger import get_logger

logger = get_logger("WebUI.MessageBroadcaster")

# 回调类型：同步或异步函数
CallbackType = Callable[[dict[str, Any]], Union[None, Coroutine[Any, Any, None]]]


class MessageBroadcaster:
    """消息广播器 - 将消息推送到 WebSocket 客户端"""

    def __init__(self, max_buffer_size: int = 500):
        """
        初始化消息广播器

        Args:
            max_buffer_size: 缓冲区最大大小，超过后会丢弃旧消息
        """
        # stream_id -> callbacks 的映射
        self.subscribers: dict[str, set[CallbackType]] = {}
        # 订阅所有消息的回调
        self.global_subscribers: set[CallbackType] = set()
        # 消息缓冲区
        self.buffer: deque[dict[str, Any]] = deque(maxlen=max_buffer_size)
        self._lock = asyncio.Lock()

    async def subscribe(
        self, callback: CallbackType, stream_id: str | None = None
    ) -> None:
        """
        订阅消息推送

        Args:
            callback: 接收消息的回调函数，参数为消息字典
            stream_id: 指定订阅的聊天流ID，None表示订阅所有消息
        """
        async with self._lock:
            if stream_id:
                if stream_id not in self.subscribers:
                    self.subscribers[stream_id] = set()
                self.subscribers[stream_id].add(callback)
                logger.debug(f"客户端订阅聊天流: {stream_id}")
            else:
                self.global_subscribers.add(callback)
                logger.debug("客户端订阅所有消息")

    async def unsubscribe(
        self, callback: CallbackType, stream_id: str | None = None
    ) -> None:
        """
        取消订阅

        Args:
            callback: 要移除的回调函数
            stream_id: 指定取消订阅的聊天流ID
        """
        async with self._lock:
            if stream_id and stream_id in self.subscribers:
                self.subscribers[stream_id].discard(callback)
                # 如果该流没有订阅者了，删除键
                if not self.subscribers[stream_id]:
                    del self.subscribers[stream_id]
            else:
                self.global_subscribers.discard(callback)
            logger.debug(f"客户端取消订阅: stream_id={stream_id}")

    async def broadcast(
        self,
        message: Any,
        stream_id: str | None = None,
        direction: str = "incoming",
        sender_type: str = "user",
    ) -> None:
        """
        广播消息到所有订阅者

        Args:
            message: 消息对象（DatabaseMessages 或 dict）
            stream_id: 聊天流ID
            direction: 消息方向 ("incoming" / "outgoing")
            sender_type: 发送者类型 ("user" / "bot" / "webui")
        """
        # 序列化消息
        msg_dict = self._serialize_message(message, stream_id, direction, sender_type)

        # 添加到缓冲区
        async with self._lock:
            self.buffer.append(msg_dict)
            # 复制订阅者列表
            global_subs = list(self.global_subscribers)
            stream_subs = (
                list(self.subscribers.get(stream_id, [])) if stream_id else []
            )

        # 发送给全局订阅者
        tasks = []
        for callback in global_subs:
            tasks.append(self._safe_callback(callback, msg_dict))

        # 发送给特定流订阅者
        for callback in stream_subs:
            tasks.append(self._safe_callback(callback, msg_dict))

        # 并行执行所有回调
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_callback(
        self, callback: CallbackType, msg_dict: dict[str, Any]
    ) -> None:
        """安全执行回调函数"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(msg_dict)
            else:
                callback(msg_dict)
        except Exception as e:
            logger.debug(f"消息回调执行失败: {e}")

    def _serialize_message(
        self,
        message: Any,
        stream_id: str | None,
        direction: str,
        sender_type: str,
    ) -> dict[str, Any]:
        """
        将消息对象序列化为字典

        Args:
            message: 消息对象
            stream_id: 聊天流ID
            direction: 消息方向
            sender_type: 发送者类型

        Returns:
            序列化后的消息字典
        """
        try:
            from src.common.data_models.database_data_model import DatabaseMessages
        except ImportError:
            DatabaseMessages = None

        # 基础消息结构
        msg_dict: dict[str, Any] = {
            "type": "message",
            "direction": direction,
            "sender_type": sender_type,
            "is_bot": direction == "outgoing",
        }

        if DatabaseMessages and isinstance(message, DatabaseMessages):
            # DatabaseMessages 对象
            msg_dict.update(
                {
                    "message_id": message.message_id,
                    "stream_id": stream_id or message.chat_id,
                    "platform": (
                        message.chat_info.platform if message.chat_info else None
                    ),
                    "user_id": message.user_info.user_id if message.user_info else None,
                    "user_nickname": (
                        message.user_info.user_nickname if message.user_info else None
                    ),
                    "content": message.processed_plain_text,
                    "display_message": message.display_message,
                    "timestamp": message.time,
                    "is_emoji": message.is_emoji,
                    "is_picid": message.is_picid,
                    "reply_to_id": message.reply_to,  # 引用消息ID
                    "group_id": (
                        message.group_info.group_id if message.group_info else None
                    ),
                    "group_name": (
                        message.group_info.group_name if message.group_info else None
                    ),
                }
            )
        elif isinstance(message, dict):
            # MessageEnvelope 或其他字典
            message_info = message.get("message_info", {})
            user_info = message_info.get("user_info", {})
            group_info = message_info.get("group_info", {})
            message_segment = message.get("message_segment", {})

            # 提取引用消息ID
            reply_to_id = self._extract_reply_from_segment(message_segment)

            # 提取消息内容
            content = self._extract_content_from_segment(message_segment)

            msg_dict.update(
                {
                    "message_id": message_info.get("message_id"),
                    "stream_id": stream_id,
                    "platform": message_info.get("platform") or message.get("platform"),
                    "user_id": user_info.get("user_id"),
                    "user_nickname": user_info.get("user_nickname"),
                    "content": content,
                    "display_message": content,
                    "timestamp": message_info.get("time"),
                    "is_emoji": False,
                    "is_picid": False,
                    "reply_to_id": reply_to_id,
                    "group_id": group_info.get("group_id") if group_info else None,
                    "group_name": group_info.get("group_name") if group_info else None,
                }
            )
        else:
            # 未知类型
            msg_dict.update(
                {
                    "message_id": None,
                    "stream_id": stream_id,
                    "content": str(message),
                    "timestamp": None,
                }
            )

        return msg_dict

    def _extract_reply_from_segment(
        self, segment: dict | list | None
    ) -> str | None:
        """
        从 message_segment 中提取引用消息 ID

        Args:
            segment: message_segment 数据

        Returns:
            被引用消息的 message_id，或 None
        """
        if not segment:
            return None

        if isinstance(segment, dict):
            seg_type = segment.get("type")
            if seg_type == "reply":
                # reply 类型的 data 直接是 message_id 字符串
                return segment.get("data")
            elif seg_type == "seglist":
                # seglist 包含多个段
                for seg in segment.get("data", []):
                    if isinstance(seg, dict) and seg.get("type") == "reply":
                        return seg.get("data")
        elif isinstance(segment, list):
            for seg in segment:
                if isinstance(seg, dict) and seg.get("type") == "reply":
                    return seg.get("data")

        return None

    def _extract_content_from_segment(
        self, segment: dict | list | None
    ) -> str:
        """
        从 message_segment 中提取文本内容

        Args:
            segment: message_segment 数据

        Returns:
            消息文本内容
        """
        if not segment:
            return ""

        contents = []

        def extract_from_seg(seg: dict) -> None:
            seg_type = seg.get("type")
            data = seg.get("data")

            if seg_type == "text":
                if isinstance(data, str):
                    contents.append(data)
                elif isinstance(data, dict):
                    contents.append(data.get("text", ""))
            elif seg_type == "image":
                contents.append("[图片]")
            elif seg_type == "emoji":
                contents.append("[表情]")
            elif seg_type == "voice":
                contents.append("[语音]")
            elif seg_type == "video":
                contents.append("[视频]")
            elif seg_type == "file":
                contents.append("[文件]")
            elif seg_type == "at":
                at_name = data.get("name", "") if isinstance(data, dict) else ""
                contents.append(f"@{at_name}")
            elif seg_type == "seglist":
                for sub_seg in data if isinstance(data, list) else []:
                    if isinstance(sub_seg, dict):
                        extract_from_seg(sub_seg)

        if isinstance(segment, dict):
            extract_from_seg(segment)
        elif isinstance(segment, list):
            for seg in segment:
                if isinstance(seg, dict):
                    extract_from_seg(seg)

        return "".join(contents)

    def get_recent_messages(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        获取最近的消息缓存

        Args:
            limit: 返回的最大消息数量

        Returns:
            消息列表
        """
        return list(self.buffer)[-limit:]

    def get_recent_messages_for_stream(
        self, stream_id: str, limit: int = 100
    ) -> list[dict[str, Any]]:
        """
        获取指定聊天流的最近消息

        Args:
            stream_id: 聊天流ID
            limit: 返回的最大消息数量

        Returns:
            消息列表
        """
        messages = [
            msg for msg in self.buffer if msg.get("stream_id") == stream_id
        ]
        return messages[-limit:]

    def clear_buffer(self) -> None:
        """清空消息缓冲区"""
        self.buffer.clear()


# ==================== 全局单例 ====================

_broadcaster: MessageBroadcaster | None = None


def get_message_broadcaster() -> MessageBroadcaster:
    """获取消息广播器单例"""
    global _broadcaster
    if _broadcaster is None:
        _broadcaster = MessageBroadcaster()
        logger.info("消息广播器已初始化")
    return _broadcaster
