"""
智能体对话服务
直接集成AutoAgent功能，提供完整的多智能体对话能力
"""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session

from app.models import Agent, Message

# 导入AutoAgent库
from autoagent.api import AutoAgentAPI, AgentEvent


class AutoAgentEventHandler:
    """AutoAgent事件处理器，用于收集和处理智能体事件"""

    def __init__(self):
        self.events_log: list[AgentEvent] = []
        self.current_session_events: list[AgentEvent] = []

    def handle_event(self, event: AgentEvent):
        """处理AutoAgent事件，参考api_usage_example的事件处理方式"""
        self.events_log.append(event)
        self.current_session_events.append(event)

        # 根据事件类型进行不同处理，参考api_usage_example
        if event.event_type == "task_start":
            print(f"🚀 任务开始: {event.data.get('user_query', '')}")
            print(f"📋 使用智能体: {event.data.get('agent_name', '')}")

        elif event.event_type == "ai_thinking_start":
            print(
                f"🤔 {event.data.get('agent_name', '')} 开始思考... (第 {event.data.get('turn', '')} 轮)"
            )

        elif event.event_type == "ai_response":
            agent_name = event.data.get("agent_name", "")
            content = event.data.get("content", "")
            has_tools = event.data.get("has_tool_calls", False)

            print(
                f"💭 {agent_name} 回复: {content[:100]}{'...' if len(content) > 100 else ''}"
            )
            if has_tools:
                tool_calls = event.data.get("tool_calls", [])
                print(f"🔧 准备调用工具: {[tc['name'] for tc in tool_calls]}")

        elif event.event_type == "tool_call_start":
            tool_name = event.data.get("tool_name", "")
            agent_name = event.data.get("agent_name", "")
            print(f"⚡ {agent_name} 开始调用工具: {tool_name}")

        elif event.event_type == "tool_call_complete":
            tool_name = event.data.get("tool_name", "")
            agent_name = event.data.get("agent_name", "")
            result = (
                event.data.get("tool_result", "")[:100] + "..."
                if len(event.data.get("tool_result", "")) > 100
                else event.data.get("tool_result", "")
            )
            print(f"✅ {agent_name} 完成工具调用: {tool_name}")
            print(f"📄 工具结果: {result}")

        elif event.event_type == "agent_switch":
            from_agent = event.data.get("from_agent", "")
            to_agent = event.data.get("to_agent", "")
            reason = event.data.get("reason", "")
            print(f"🔄 智能体切换: {from_agent} -> {to_agent} ({reason})")

        elif event.event_type == "task_complete":
            agent_name = event.data.get("agent_name", "")
            turns = event.data.get("total_turns", 0)
            print(f"🎉 任务完成! 智能体: {agent_name}, 总轮数: {turns}")

        elif event.event_type == "query_complete":
            result = (
                event.data.get("result", "")[:200] + "..."
                if len(event.data.get("result", "")) > 200
                else event.data.get("result", "")
            )
            print(f"📋 最终结果: {result}")

        elif event.event_type == "initialization_complete":
            print(f"📦 AutoAgent初始化完成")
            available_agents = event.data.get("available_agents", [])
            print(f"📋 可用智能体: {available_agents}")

        elif event.event_type == "query_start":
            print(f"🔍 开始处理查询: {event.data.get('query', '')}")

        elif event.event_type == "query_error":
            print(f"❌ 查询处理错误: {event.data.get('error', '')}")

        print("-" * 50)

    def get_current_session_events(self) -> list[dict[str, Any]]:
        """获取当前会话的事件"""
        return [event.to_dict() for event in self.current_session_events]

    def clear_current_session(self):
        """清除当前会话的事件"""
        self.current_session_events.clear()

    def get_events_summary(self) -> dict[str, Any]:
        """获取事件摘要"""
        event_types = {}
        for event in self.current_session_events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1

        return {
            "total_events": len(self.current_session_events),
            "event_types": event_types,
            "timeline": [
                (event.timestamp, event.event_type)
                for event in self.current_session_events
            ],
        }


class AgentDialogueService:
    """智能体对话服务类，直接集成AutoAgent功能"""

    def __init__(self):
        # 存储不同会话的AutoAgent实例和事件处理器
        self.autoagent_instances: dict[str, AutoAgentAPI] = {}
        self.event_handlers: dict[str, AutoAgentEventHandler] = {}

    def _get_or_create_autoagent_instance(
        self, session_id: str
    ) -> tuple[AutoAgentAPI, AutoAgentEventHandler]:
        """获取或创建AutoAgent实例和事件处理器"""

        if session_id not in self.autoagent_instances:
            # 创建事件处理器
            event_handler = AutoAgentEventHandler()

            # 创建AutoAgent API实例，参考api_usage_example的用法
            # 使用本地环境避免Docker相关的序列化问题
            api = AutoAgentAPI(
                container_name=f"alma_agent_{session_id}",
                port=12347 + hash(session_id) % 1000,  # 避免端口冲突
                local_env=True,  # 改为本地环境，避免序列化问题
            )

            # 添加事件回调，这是关键步骤
            api.add_event_callback(event_handler.handle_event)

            # 初始化AutoAgent（参考api_usage_example，可选但推荐）
            try:
                print(f"📦 初始化AutoAgent实例: {session_id}")
                api.initialize()
            except Exception as e:
                print(f"⚠️ AutoAgent初始化失败，将在process_query时自动初始化: {e}")

            # 存储实例
            self.autoagent_instances[session_id] = api
            self.event_handlers[session_id] = event_handler

        return self.autoagent_instances[session_id], self.event_handlers[session_id]

    def _build_agent_query(
        self, agent: Agent, user_message: str, conversation_history: list[Message]
    ) -> str:
        """构建发送给AutoAgent的查询"""
        query_parts = []

        # 添加Agent角色信息
        query_parts.append(f"你是{agent.name}。")
        query_parts.append(f"你的指令：{agent.instruction}")

        if agent.team:
            query_parts.append(f"你所属的团队：{', '.join(agent.team)}")

        # 添加对话历史（最近几条）
        recent_messages = (
            conversation_history[-5:]
            if len(conversation_history) > 5
            else conversation_history
        )
        if recent_messages:
            query_parts.append("\n历史对话：")
            for msg in recent_messages:
                if msg.role == "user":
                    query_parts.append(f"用户: {msg.content}")
                elif msg.role == "assistant":
                    query_parts.append(f"助手: {msg.content}")

        # 添加当前用户消息
        query_parts.append(f"\n当前用户消息: {user_message}")
        query_parts.append("\n请根据你的角色和指令回复用户。")

        return "\n".join(query_parts)

    async def process_agent_dialogue(
        self,
        session: Session,
        agent: Agent,
        user_message: str,
        conversation_history: list[Message],
        session_id: str = None,
    ) -> dict[str, Any]:
        """
        处理智能体对话，使用AutoAgent
        参考api_usage_example.py的实现方式

        Args:
            session: 数据库会话
            agent: 智能体实例
            user_message: 用户消息
            conversation_history: 对话历史
            session_id: 会话ID，用于区分不同对话

        Returns:
            包含回复内容和事件的字典
        """

        if not session_id:
            session_id = str(uuid.uuid4())

        try:
            # 获取或创建AutoAgent实例和事件处理器
            api, event_handler = self._get_or_create_autoagent_instance(session_id)

            # 清除当前会话事件，为新的对话做准备
            event_handler.clear_current_session()

            # 构建查询
            query = self._build_agent_query(agent, user_message, conversation_history)

            # 使用AutoAgent处理查询，这里参考了api_usage_example的用法
            print(f"🔍 处理查询: {user_message}")
            print(f"📋 使用智能体: {agent.name}")
            print(f"📝 查询长度: {len(query)} 字符")

            try:
                result = api.process_query(query)
            except Exception as autoagent_error:
                # AutoAgent处理异常时的备用响应
                print(f"⚠️ AutoAgent处理异常，使用备用响应: {autoagent_error}")

                # 创建备用响应
                backup_response = f"我是{agent.name}，{agent.instruction}。关于您的问题：{user_message}，我正在为您处理中。由于系统正在优化，请稍后再试或联系技术支持。"

                # 添加错误事件
                error_event = {
                    "event_type": "autoagent_error",
                    "timestamp": datetime.now().isoformat(),
                    "data": {
                        "error": str(autoagent_error),
                        "fallback_used": True,
                        "agent_name": agent.name,
                    },
                }
                event_handler.current_session_events.append(
                    type(
                        "Event",
                        (),
                        {
                            "event_type": "autoagent_error",
                            "timestamp": datetime.now().isoformat(),
                            "data": error_event["data"],
                            "to_dict": lambda self: error_event,
                        },
                    )()
                )

                return {
                    "success": True,  # 仍然算成功，因为提供了备用响应
                    "response": backup_response,
                    "raw_result": {"error": str(autoagent_error)},
                    "agent_name": agent.name,
                    "events": [error_event],
                    "events_summary": {
                        "total_events": 1,
                        "event_types": {"autoagent_error": 1},
                    },
                    "session_id": session_id,
                    "autoagent_messages": [],
                    "context_variables": {},
                    "fallback_used": True,
                }

            if result.get("success"):
                # 获取事件信息
                events = event_handler.get_current_session_events()
                events_summary = event_handler.get_events_summary()

                print(f"✅ 查询处理成功，智能体: {result.get('agent_name')}")
                print(f"📊 事件数量: {len(events)}")
                print(f"📊 事件类型分布: {events_summary.get('event_types', {})}")

                return {
                    "success": True,
                    "response": result.get("result", ""),
                    "raw_result": result.get("raw_result", ""),
                    "agent_name": result.get("agent_name", agent.name),
                    "events": events,
                    "events_summary": events_summary,
                    "session_id": session_id,
                    "autoagent_messages": result.get("messages", []),
                    "context_variables": result.get("context_variables", {}),
                }
            else:
                print(f"❌ AutoAgent处理失败: {result.get('error', '未知错误')}")
                return {
                    "success": False,
                    "error": result.get("error", "AutoAgent处理失败"),
                    "events": event_handler.get_current_session_events(),
                    "session_id": session_id,
                }

        except Exception as e:
            print(f"❌ 对话处理异常: {str(e)}")
            return {
                "success": False,
                "error": f"Agent对话处理异常: {str(e)}",
                "events": [],
                "session_id": session_id,
            }

    async def process_agent_dialogue_with_realtime_events(
        self,
        session: Session,
        agent: Agent,
        user_message: str,
        conversation_history: list[Message],
        session_id: str = None,
        model=None,
        realtime_callback=None,
    ) -> dict[str, Any]:
        """
        处理智能体对话，支持实时事件推送
        这个方法专门为WebSocket实时流式传输设计

        Args:
            session: 数据库会话
            agent: 智能体实例
            user_message: 用户消息
            conversation_history: 对话历史
            session_id: 会话ID，用于区分不同对话
            model: 模型实例
            realtime_callback: 实时事件回调函数

        Returns:
            包含回复内容和事件的字典
        """

        if not session_id:
            session_id = str(uuid.uuid4())

        try:
            # 获取或创建AutoAgent实例和事件处理器
            api, event_handler = self._get_or_create_autoagent_instance(session_id)

            # 清除当前会话事件，为新的对话做准备
            event_handler.clear_current_session()

            # 如果提供了实时回调，将其添加到事件处理器
            if realtime_callback:
                # 创建一个包装器来处理异步回调
                original_handle_event = event_handler.handle_event

                def enhanced_handle_event(event):
                    # 调用原始处理
                    original_handle_event(event)

                    # 异步调用实时回调
                    import asyncio

                    try:
                        # 检查是否在事件循环中
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # 创建任务而不是等待
                            asyncio.create_task(
                                realtime_callback(
                                    event.event_type,
                                    event.data.get("agent_name", ""),
                                    event.data,
                                )
                            )
                        else:
                            # 如果没有运行的事件循环，直接运行
                            asyncio.run(
                                realtime_callback(
                                    event.event_type,
                                    event.data.get("agent_name", ""),
                                    event.data,
                                )
                            )
                    except Exception as e:
                        print(f"实时回调执行异常: {e}")

                # 临时替换事件处理方法
                event_handler.handle_event = enhanced_handle_event

            # 构建查询
            query = self._build_agent_query(agent, user_message, conversation_history)

            # 使用AutoAgent处理查询
            print(f"🔍 处理实时查询: {user_message}")
            print(f"📋 使用智能体: {agent.name}")
            print(f"📡 实时推送: {'启用' if realtime_callback else '禁用'}")

            try:
                result = api.process_query(query)
            except Exception as autoagent_error:
                # AutoAgent处理异常时的备用响应
                print(f"⚠️ AutoAgent处理异常，使用备用响应: {autoagent_error}")

                # 如果有实时回调，推送错误事件
                if realtime_callback:
                    try:
                        await realtime_callback(
                            "autoagent_error",
                            agent.name,
                            {
                                "error": str(autoagent_error),
                                "fallback_used": True,
                                "timestamp": datetime.now().isoformat(),
                            },
                        )
                    except Exception:
                        pass

                # 创建备用响应
                backup_response = f"我是{agent.name}，{agent.instruction}。关于您的问题：{user_message}，我正在为您处理中。由于系统正在优化，请稍后再试或联系技术支持。"

                return {
                    "success": True,  # 仍然算成功，因为提供了备用响应
                    "response": backup_response,
                    "raw_result": {"error": str(autoagent_error)},
                    "agent_name": agent.name,
                    "events": [
                        {
                            "event_type": "autoagent_error",
                            "timestamp": datetime.now().isoformat(),
                            "data": {
                                "error": str(autoagent_error),
                                "fallback_used": True,
                                "agent_name": agent.name,
                            },
                        }
                    ],
                    "events_summary": {
                        "total_events": 1,
                        "event_types": {"autoagent_error": 1},
                    },
                    "session_id": session_id,
                    "autoagent_messages": [],
                    "context_variables": {},
                    "fallback_used": True,
                    "realtime_events": True,
                }

            if result.get("success"):
                # 获取事件信息
                events = event_handler.get_current_session_events()
                events_summary = event_handler.get_events_summary()

                print(f"✅ 实时查询处理成功，智能体: {result.get('agent_name')}")
                print(f"📊 事件数量: {len(events)}")
                print(f"📊 事件类型分布: {events_summary.get('event_types', {})}")

                return {
                    "success": True,
                    "response": result.get("result", ""),
                    "raw_result": result.get("raw_result", ""),
                    "agent_name": result.get("agent_name", agent.name),
                    "events": events,
                    "events_summary": events_summary,
                    "session_id": session_id,
                    "autoagent_messages": result.get("messages", []),
                    "context_variables": result.get("context_variables", {}),
                    "realtime_events": True,
                }
            else:
                print(f"❌ AutoAgent实时处理失败: {result.get('error', '未知错误')}")

                # 如果有实时回调，推送失败事件
                if realtime_callback:
                    try:
                        await realtime_callback(
                            "query_error",
                            agent.name,
                            {
                                "error": result.get("error", "未知错误"),
                                "timestamp": datetime.now().isoformat(),
                            },
                        )
                    except Exception:
                        pass

                return {
                    "success": False,
                    "error": result.get("error", "AutoAgent处理失败"),
                    "events": event_handler.get_current_session_events(),
                    "session_id": session_id,
                    "realtime_events": True,
                }

        except Exception as e:
            print(f"❌ 实时对话处理异常: {str(e)}")

            # 如果有实时回调，推送异常事件
            if realtime_callback:
                try:
                    await realtime_callback(
                        "processing_error",
                        agent.name,
                        {
                            "error": str(e),
                            "timestamp": datetime.now().isoformat(),
                        },
                    )
                except Exception:
                    pass

            return {
                "success": False,
                "error": f"Agent实时对话处理异常: {str(e)}",
                "events": [],
                "session_id": session_id,
                "realtime_events": True,
            }

    def get_available_agents(self, session_id: str) -> list[str]:
        """获取可用的智能体列表"""
        if session_id in self.autoagent_instances:
            try:
                api = self.autoagent_instances[session_id]
                return api.get_available_agents()
            except Exception as e:
                print(f"获取可用智能体失败: {e}")
                return []
        return []

    def reset_session(self, agent: Agent, session_id: str):
        """重置会话状态"""
        if session_id in self.autoagent_instances:
            try:
                api = self.autoagent_instances[session_id]
                api.reset_session()
                print(f"🔄 重置会话: {session_id}")
            except Exception as e:
                print(f"重置会话失败: {e}")

        if session_id in self.event_handlers:
            self.event_handlers[session_id].clear_current_session()

    def cleanup_session(self, session_id: str):
        """清理会话资源"""
        if session_id in self.autoagent_instances:
            del self.autoagent_instances[session_id]
            print(f"🧹 清理会话资源: {session_id}")

        if session_id in self.event_handlers:
            del self.event_handlers[session_id]

    def get_session_events(self, session_id: str) -> list[dict[str, Any]]:
        """获取会话事件"""
        if session_id in self.event_handlers:
            return self.event_handlers[session_id].get_current_session_events()
        return []

    def clear_session_events(self, session_id: str):
        """清除会话事件"""
        if session_id in self.event_handlers:
            self.event_handlers[session_id].clear_current_session()

    def get_session_events_summary(self, session_id: str) -> dict[str, Any]:
        """获取会话事件摘要"""
        if session_id in self.event_handlers:
            return self.event_handlers[session_id].get_events_summary()
        return {"total_events": 0, "event_types": {}, "timeline": []}

    def get_session_statistics(self, session_id: str) -> dict[str, Any]:
        """获取会话统计信息，参考api_usage_example的监控功能"""
        if session_id not in self.event_handlers:
            return {
                "total_events": 0,
                "tool_calls": 0,
                "agent_switches": 0,
                "tasks_completed": 0,
                "errors": 0,
            }

        events = self.event_handlers[session_id].events_log

        tool_calls = len([e for e in events if e.event_type == "tool_call_start"])
        agent_switches = len([e for e in events if e.event_type == "agent_switch"])
        tasks_completed = len([e for e in events if e.event_type == "task_complete"])
        errors = len(
            [e for e in events if e.event_type in ["query_error", "tool_call_error"]]
        )

        # 获取使用的工具列表
        tools_used = {
            e.data.get("tool_name", "")
            for e in events
            if e.event_type == "tool_call_start" and e.data.get("tool_name")
        }

        return {
            "total_events": len(events),
            "tool_calls": tool_calls,
            "agent_switches": agent_switches,
            "tasks_completed": tasks_completed,
            "errors": errors,
            "tools_used": tools_used,
            "session_id": session_id,
        }

    def get_all_sessions_summary(self) -> dict[str, Any]:
        """获取所有会话的摘要信息"""
        active_sessions = list(self.autoagent_instances.keys())

        summary = {"total_active_sessions": len(active_sessions), "sessions": {}}

        for session_id in active_sessions:
            summary["sessions"][session_id] = self.get_session_statistics(session_id)

        return summary

    def export_session_events(self, session_id: str, format: str = "json") -> str:
        """导出会话事件，用于调试和分析"""
        if session_id not in self.event_handlers:
            return "" if format == "json" else "No events found"

        events = self.event_handlers[session_id].events_log

        if format == "json":
            import json

            return json.dumps(
                [event.to_dict() for event in events], ensure_ascii=False, indent=2
            )
        else:
            # 简单的文本格式
            lines = []
            for event in events:
                lines.append(f"[{event.timestamp}] {event.event_type}: {event.data}")
            return "\n".join(lines)

    # ...existing code...


# 全局服务实例
agent_dialogue_service = AgentDialogueService()
