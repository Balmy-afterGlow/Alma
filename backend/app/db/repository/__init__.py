"""
数据库CRUD操作模块
包含所有数据模型的创建、读取、更新、删除操作
"""

from .agent_crud import (
    create_agent,
    delete_agent,
    get_active_agents_by_user,
    get_agent_by_id,
    get_agents_by_user,
    get_agents_count_by_user,
    get_system_agents,
    update_agent,
)
from .agent_tools_crud import (
    add_tool_to_agent,
    clear_agent_tools,
    count_agents_for_tool,
    count_tools_for_agent,
    get_agent_tool_relationships,
    get_agents_by_tool,
    get_tools_by_agent,
    remove_tool_from_agent,
    set_agent_tools,
)
from .conversation_crud import (
    create_conversation,
    delete_conversation,
    get_conversation_by_id,
    get_conversations_by_user,
    get_conversations_count_by_user,
    get_recent_conversations_by_user,
    update_conversation,
)
from .llm_config_crud import (
    create_llm_config,
    delete_llm_config,
    get_decrypted_api_key,
    get_llm_config_by_id,
    get_llm_config_by_provider,
    get_llm_configs_by_user,
    get_llm_configs_count_by_user,
    update_llm_config,
)
from .message_crud import (
    create_message,
    get_latest_message_by_conversation,
    get_message_by_id,
    get_messages_by_agent,
    get_messages_by_conversation,
    get_messages_count_by_conversation,
    hard_delete_message,
    search_messages_by_content,
    soft_delete_message,
    update_message,
)
from .model_crud import (
    create_model,
    delete_model,
    get_all_models,
    get_model_by_id,
    get_model_by_name,
    get_models_by_llm_config,
    get_models_by_user,
    get_models_count_by_llm_config,
    update_model,
)
from .tool_crud import (
    create_tool,
    delete_tool,
    get_all_tools,
    get_tool_by_id,
    get_tool_by_name,
    get_tools_count,
    search_tools_by_name,
    update_tool,
)
from .user_crud import create_user, get_user_by_email, update_user

__all__ = [
    # User CRUD
    "create_user",
    "update_user",
    "get_user_by_email",
    # Agent CRUD
    "create_agent",
    "get_agent_by_id",
    "get_agents_by_user",
    "get_system_agents",
    "get_active_agents_by_user",
    "update_agent",
    "delete_agent",
    "get_agents_count_by_user",
    # Conversation CRUD
    "create_conversation",
    "get_conversation_by_id",
    "get_conversations_by_user",
    "get_recent_conversations_by_user",
    "update_conversation",
    "delete_conversation",
    "get_conversations_count_by_user",
    # Message CRUD
    "create_message",
    "get_message_by_id",
    "get_messages_by_conversation",
    "get_messages_by_agent",
    "get_latest_message_by_conversation",
    "update_message",
    "soft_delete_message",
    "hard_delete_message",
    "get_messages_count_by_conversation",
    "search_messages_by_content",
    # Model CRUD
    "create_model",
    "get_model_by_id",
    "get_model_by_name",
    "get_models_by_llm_config",
    "get_all_models",
    "update_model",
    "delete_model",
    "get_models_by_user",
    "get_models_count_by_llm_config",
    # LLMConfig CRUD
    "create_llm_config",
    "get_llm_config_by_id",
    "get_llm_configs_by_user",
    "get_llm_config_by_provider",
    "update_llm_config",
    "delete_llm_config",
    "get_decrypted_api_key",
    "get_llm_configs_count_by_user",
    # Tool CRUD
    "create_tool",
    "get_tool_by_id",
    "get_tool_by_name",
    "get_all_tools",
    "update_tool",
    "delete_tool",
    "search_tools_by_name",
    "get_tools_count",
    # Agent-Tools relationship CRUD
    "add_tool_to_agent",
    "remove_tool_from_agent",
    "get_tools_by_agent",
    "get_agents_by_tool",
    "get_agent_tool_relationships",
    "clear_agent_tools",
    "set_agent_tools",
    "count_tools_for_agent",
    "count_agents_for_tool",
]
