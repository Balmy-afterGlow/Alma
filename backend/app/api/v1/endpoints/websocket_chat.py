"""
WebSocket聊天端点
提供实时的智能体对话和事件推送，支持AutoAgent事件的实时流式传输
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.db.repository import (
    create_conversation,
    create_message,
    get_agent_by_id,
    get_conversation_by_id,
    get_model_by_id,
    get_messages_by_conversation,
)
from app.schemas import ConversationCreate, MessageCreate
from app.services.agent_service import agent_dialogue_service

router = APIRouter()
logger = logging.getLogger(__name__)


class WebSocketConnectionManager:
    """WebSocket连接管理器，支持实时事件推送"""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.event_queues: dict[str, asyncio.Queue] = {}
        self.connection_tasks: dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """连接WebSocket"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.event_queues[session_id] = asyncio.Queue()

        # 启动事件处理任务
        self.connection_tasks[session_id] = asyncio.create_task(
            self._handle_events(session_id)
        )

        logger.info(f"WebSocket连接建立: {session_id}")

    def disconnect(self, session_id: str):
        """断开连接"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]

        if session_id in self.event_queues:
            del self.event_queues[session_id]

        if session_id in self.connection_tasks:
            self.connection_tasks[session_id].cancel()
            del self.connection_tasks[session_id]

        logger.info(f"WebSocket连接断开: {session_id}")

    async def _handle_events(self, session_id: str):
        """处理事件队列中的消息"""
        try:
            while True:
                if session_id not in self.event_queues:
                    break

                try:
                    # 等待事件，设置超时避免无限等待
                    message = await asyncio.wait_for(
                        self.event_queues[session_id].get(), timeout=30.0
                    )
                    await self._send_direct(session_id, message)
                except asyncio.TimeoutError:
                    # 发送心跳消息
                    await self._send_direct(
                        session_id,
                        {"type": "heartbeat", "timestamp": datetime.now().isoformat()},
                    )
                except Exception as e:
                    logger.error(f"处理事件时出错: {e}")
                    break
        except asyncio.CancelledError:
            pass

    async def _send_direct(self, session_id: str, message: dict):
        """直接发送消息，不经过队列"""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(
                    json.dumps(message, ensure_ascii=False, default=str)
                )
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                self.disconnect(session_id)

    async def send_message(self, session_id: str, message: dict):
        """发送消息给特定会话（通过队列）"""
        if session_id in self.event_queues:
            try:
                await self.event_queues[session_id].put(message)
            except Exception as e:
                logger.error(f"消息入队失败: {e}")

    async def send_immediate(self, session_id: str, message: dict):
        """立即发送消息，不经过队列（用于紧急消息）"""
        await self._send_direct(session_id, message)


manager = WebSocketConnectionManager()


class RealTimeEventHandler:
    """实时事件处理器，用于WebSocket流式推送AutoAgent事件"""

    def __init__(self, session_id: str, manager: WebSocketConnectionManager):
        self.session_id = session_id
        self.manager = manager
        self.events_count = 0

    async def handle_autoagent_event(
        self, event_type: str, agent_name: str, data: dict
    ):
        """处理AutoAgent事件并实时推送给前端"""
        self.events_count += 1

        # 构建事件消息
        event_message = {
            "type": "agent_event",
            "event_type": event_type,
            "agent_name": agent_name,
            "data": data,
            "timestamp": data.get("timestamp", datetime.now().isoformat()),
            "sequence": self.events_count,
        }

        # 发送事件到前端
        await self.manager.send_message(self.session_id, event_message)

        # 根据事件类型发送特定的状态更新
        if event_type == "task_start":
            await self.manager.send_message(
                self.session_id,
                {
                    "type": "status_update",
                    "status": "processing",
                    "message": f"开始处理任务: {data.get('user_query', '')}",
                },
            )

        elif event_type == "ai_thinking_start":
            await self.manager.send_message(
                self.session_id,
                {
                    "type": "status_update",
                    "status": "thinking",
                    "message": f"{agent_name} 正在思考... (第 {data.get('turn', 1)} 轮)",
                },
            )

        elif event_type == "tool_call_start":
            tool_name = data.get("tool_name", "unknown")
            await self.manager.send_message(
                self.session_id,
                {
                    "type": "status_update",
                    "status": "tool_calling",
                    "message": f"{agent_name} 正在调用工具: {tool_name}",
                },
            )

        elif event_type == "tool_call_complete":
            tool_name = data.get("tool_name", "unknown")
            await self.manager.send_message(
                self.session_id,
                {
                    "type": "status_update",
                    "status": "tool_completed",
                    "message": f"{agent_name} 完成工具调用: {tool_name}",
                },
            )

        elif event_type == "agent_switch":
            from_agent = data.get("from_agent", "")
            to_agent = data.get("to_agent", "")
            await self.manager.send_message(
                self.session_id,
                {
                    "type": "status_update",
                    "status": "agent_switch",
                    "message": f"智能体切换: {from_agent} -> {to_agent}",
                },
            )

        elif event_type == "task_complete":
            await self.manager.send_message(
                self.session_id,
                {
                    "type": "status_update",
                    "status": "completed",
                    "message": f"任务完成! 总轮数: {data.get('total_turns', 0)}",
                },
            )


@router.websocket("/ws/{session_id}")
async def websocket_chat_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket聊天端点，支持实时事件流"""
    await manager.connect(websocket, session_id)

    try:
        # 发送连接成功消息
        await manager.send_immediate(
            session_id,
            {
                "type": "connection_success",
                "message": "WebSocket连接成功，准备接收实时事件",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
            },
        )

        while True:
            # 接收客户端消息
            data = await websocket.receive_text()

            try:
                message_data = json.loads(data)
                message_type = message_data.get("type")

                if message_type == "chat":
                    # 处理聊天消息
                    await handle_realtime_chat_message(session_id, message_data)
                elif message_type == "ping":
                    # 心跳检测
                    await manager.send_immediate(
                        session_id,
                        {
                            "type": "pong",
                            "timestamp": datetime.now().isoformat(),
                            "client_timestamp": message_data.get("timestamp"),
                        },
                    )
                elif message_type == "reset_session":
                    # 重置会话
                    await handle_session_reset(session_id, message_data)
                elif message_type == "get_status":
                    # 获取状态
                    await handle_get_status(session_id)
                else:
                    await manager.send_message(
                        session_id,
                        {
                            "type": "error",
                            "message": f"未知的消息类型: {message_type}",
                            "timestamp": datetime.now().isoformat(),
                        },
                    )

            except json.JSONDecodeError:
                await manager.send_message(
                    session_id,
                    {
                        "type": "error",
                        "message": "无效的JSON格式",
                        "timestamp": datetime.now().isoformat(),
                    },
                )
            except Exception as e:
                logger.exception(f"处理WebSocket消息时出错: {e}")
                await manager.send_message(
                    session_id,
                    {
                        "type": "error",
                        "message": f"处理消息时出错: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                    },
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket客户端断开连接: {session_id}")
    except Exception as e:
        logger.exception(f"WebSocket连接异常: {e}")
    finally:
        manager.disconnect(session_id)
        # 清理会话资源
        agent_dialogue_service.cleanup_session(session_id)


async def handle_realtime_chat_message(session_id: str, message_data: dict):
    """处理实时聊天消息，支持AutoAgent事件流式推送"""
    try:
        # 解析消息数据
        user_message = message_data.get("message", "")
        agent_id = message_data.get("agent_id")
        conversation_id = message_data.get("conversation_id")
        model_id = message_data.get("model_id")
        user_id = message_data.get("user_id")

        if not all([user_message, agent_id, user_id]):
            await manager.send_message(
                session_id,
                {
                    "type": "error",
                    "message": "缺少必要的参数: message, agent_id, user_id",
                    "timestamp": datetime.now().isoformat(),
                },
            )
            return

        # 发送处理开始消息
        await manager.send_message(
            session_id,
            {
                "type": "chat_start",
                "message": "开始处理您的消息...",
                "timestamp": datetime.now().isoformat(),
            },
        )

        # 创建数据库会话
        from app.db.session import get_session_context

        async with get_session_context() as session:
            # 验证Agent
            agent = get_agent_by_id(session=session, agent_id=uuid.UUID(agent_id))
            if not agent or not agent.is_system_agent:
                await manager.send_message(
                    session_id,
                    {
                        "type": "error",
                        "message": "Agent不存在或不是系统Agent",
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                return

            # 处理对话
            conversation = None
            if conversation_id:
                conversation = get_conversation_by_id(
                    session=session, conversation_id=uuid.UUID(conversation_id)
                )
                if not conversation or str(conversation.user_id) != user_id:
                    await manager.send_message(
                        session_id,
                        {
                            "type": "error",
                            "message": "对话不存在或无权访问",
                            "timestamp": datetime.now().isoformat(),
                        },
                    )
                    return
            else:
                # 创建新对话
                conversation = create_conversation(
                    session=session,
                    conversation_create=ConversationCreate(title="新对话"),
                    user_id=uuid.UUID(user_id),
                )

            # 创建用户消息
            user_msg = create_message(
                session=session,
                message_create=MessageCreate(
                    role="user",
                    content=user_message,
                    conversation_id=conversation.conversation_id,
                    agent_id=uuid.UUID(agent_id),
                ),
            )

            # 发送用户消息确认
            await manager.send_message(
                session_id,
                {
                    "type": "user_message_saved",
                    "message_id": str(user_msg.message_id),
                    "conversation_id": str(conversation.conversation_id),
                    "timestamp": datetime.now().isoformat(),
                },
            )

            # 获取模型
            model = None
            if model_id:
                model = get_model_by_id(session=session, model_id=uuid.UUID(model_id))

            # 获取对话历史
            conversation_history = get_messages_by_conversation(
                session=session, conversation_id=conversation.conversation_id
            )

            # 创建实时事件处理器
            event_handler = RealTimeEventHandler(session_id, manager)

            # 设置AutoAgent的实时事件回调
            async def async_event_callback(
                event_type: str, agent_name: str, data: dict
            ):
                """异步事件回调"""
                await event_handler.handle_autoagent_event(event_type, agent_name, data)

            try:
                # 调用智能体对话服务，传入实时事件回调
                dialogue_result = await agent_dialogue_service.process_agent_dialogue_with_realtime_events(
                    session=session,
                    agent=agent,
                    user_message=user_message,
                    conversation_history=conversation_history[
                        :-1
                    ],  # 排除刚创建的用户消息
                    session_id=session_id,
                    model=model,
                    realtime_callback=async_event_callback,
                )

                if dialogue_result["success"]:
                    # 创建助手消息
                    assistant_msg = create_message(
                        session=session,
                        message_create=MessageCreate(
                            role="assistant",
                            content=dialogue_result["response"],
                            conversation_id=conversation.conversation_id,
                            agent_id=uuid.UUID(agent_id),
                            model_metadata={
                                "model_id": model_id,
                                "model_name": dialogue_result.get("model_used"),
                                "tools_available": dialogue_result.get(
                                    "tools_available", 0
                                ),
                                "events_count": len(dialogue_result.get("events", [])),
                                "session_id": session_id,
                                "realtime_events": True,
                            },
                        ),
                    )

                    # 发送最终结果
                    await manager.send_message(
                        session_id,
                        {
                            "type": "chat_complete",
                            "conversation_id": str(conversation.conversation_id),
                            "user_message_id": str(user_msg.message_id),
                            "assistant_message_id": str(assistant_msg.message_id),
                            "response": dialogue_result["response"],
                            "model_used": dialogue_result.get("model_used"),
                            "tools_available": dialogue_result.get(
                                "tools_available", 0
                            ),
                            "events_count": len(dialogue_result.get("events", [])),
                            "timestamp": datetime.now().isoformat(),
                        },
                    )
                else:
                    await manager.send_message(
                        session_id,
                        {
                            "type": "chat_error",
                            "message": f"对话处理失败: {dialogue_result.get('error', '未知错误')}",
                            "timestamp": datetime.now().isoformat(),
                        },
                    )

            except Exception as e:
                logger.exception(f"智能体对话处理异常: {e}")
                await manager.send_message(
                    session_id,
                    {
                        "type": "chat_error",
                        "message": f"智能体处理异常: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                    },
                )

    except Exception as e:
        logger.exception(f"处理实时聊天消息异常: {e}")
        await manager.send_message(
            session_id,
            {
                "type": "error",
                "message": f"服务器内部错误: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            },
        )


async def handle_session_reset(session_id: str, message_data: dict):
    """处理会话重置"""
    try:
        agent_id = message_data.get("agent_id")
        if agent_id:
            from app.db.session import get_session_context

            async with get_session_context() as session:
                agent = get_agent_by_id(session=session, agent_id=uuid.UUID(agent_id))
                if agent:
                    agent_dialogue_service.reset_session(agent, session_id)

        await manager.send_message(
            session_id,
            {
                "type": "session_reset_complete",
                "message": "会话已重置",
                "timestamp": datetime.now().isoformat(),
            },
        )
    except Exception as e:
        logger.exception(f"重置会话异常: {e}")
        await manager.send_message(
            session_id,
            {
                "type": "error",
                "message": f"重置会话失败: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            },
        )


async def handle_get_status(session_id: str):
    """获取会话状态"""
    try:
        status_data = agent_dialogue_service.get_session_statistics(session_id)
        await manager.send_message(
            session_id,
            {
                "type": "status_response",
                "data": status_data,
                "timestamp": datetime.now().isoformat(),
            },
        )
    except Exception as e:
        logger.exception(f"获取状态异常: {e}")
        await manager.send_message(
            session_id,
            {
                "type": "error",
                "message": f"获取状态失败: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            },
        )
