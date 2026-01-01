"""
即时通讯消息事件处理器
订阅 ON_MESSAGE 和 AFTER_SEND 事件，将消息广播到 WebSocket 客户端
零侵入实现 - 不修改 MMC 核心代码
"""

from src.common.logger import get_logger
from src.plugin_system import BaseEventHandler, EventType
from src.plugin_system.base.base_event import HandlerResult

from ..utils.message_broadcaster import get_message_broadcaster

logger = get_logger("WebUI.LiveChatHandler")


class LiveChatEventHandler(BaseEventHandler):
    """
    即时通讯消息事件处理器

    功能:
    1. 订阅 ON_MESSAGE 事件，获取平台收到的消息
    2. 订阅 AFTER_SEND 事件，获取机器人发送的消息
    3. 将消息广播到 WebSocket 客户端

    零侵入原理:
    - 使用 MMC 标准的 EventHandler 机制
    - 不修改任何 MMC 核心代码
    - 只读取事件数据，不干预消息处理流程
    """

    handler_name = "live_chat_broadcast"
    handler_description = "将消息广播到 WebUI 即时通讯客户端"
    weight = 100  # 较低权重，确保在其他处理器之后执行
    intercept_message = False  # 不拦截消息
    init_subscribe = [EventType.ON_MESSAGE, EventType.AFTER_SEND]

    async def execute(self, params: dict) -> HandlerResult:
        """
        处理消息事件

        Args:
            params: 事件参数
                - ON_MESSAGE: {"message": DatabaseMessages, "stream_id": str, "chat_stream": ChatStream}
                - AFTER_SEND: {"message": DatabaseMessages|MessageEnvelope, "stream_id": str, ...}

        Returns:
            HandlerResult: 处理结果
        """
        try:
            message = params.get("message")
            stream_id = params.get("stream_id")
            event_type = params.get("event_type")

            if not message:
                return HandlerResult(
                    success=True,
                    continue_process=True,
                    message=None,
                    handler_name=self.handler_name,
                )

            # 获取广播器
            broadcaster = get_message_broadcaster()

            # 根据事件类型确定消息方向和发送者类型
            if event_type == EventType.ON_MESSAGE:
                direction = "incoming"
                sender_type = "user"
            elif event_type == EventType.AFTER_SEND:
                direction = "outgoing"
                # 判断是 AI 自动回复还是 WebUI 手动发送
                # 可以通过 params 中的额外信息判断
                sender_type = params.get("sender_type", "bot")
            else:
                direction = "unknown"
                sender_type = "unknown"

            # 广播消息
            await broadcaster.broadcast(
                message=message,
                stream_id=stream_id,
                direction=direction,
                sender_type=sender_type,
            )

            logger.debug(
                f"消息已广播: stream_id={stream_id}, direction={direction}, sender_type={sender_type}"
            )

            return HandlerResult(
                success=True,
                continue_process=True,  # 继续处理，不阻断其他处理器
                message=None,
                handler_name=self.handler_name,
            )

        except Exception as e:
            logger.error(f"广播消息失败: {e}")
            # 即使广播失败也不应该阻断消息处理流程
            return HandlerResult(
                success=True,
                continue_process=True,
                message=None,
                handler_name=self.handler_name,
            )
