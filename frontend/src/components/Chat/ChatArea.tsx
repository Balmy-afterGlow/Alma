import {
    Box,
    Flex,
    Text,
    IconButton,
    Input,
    Button,
    VStack,
    HStack,
} from "@chakra-ui/react"
import { FiMenu, FiSend, FiUser, FiCpu } from "react-icons/fi"
import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"

import { ConversationsService, ChatService, AgentsService } from "@/client"
import useAuth from "@/hooks/useAuth"

interface ChatAreaProps {
    conversationId: string | null
    onToggleSidebar: () => void
}

const ChatArea = ({ conversationId, onToggleSidebar }: ChatAreaProps) => {
    const { user } = useAuth()
    const [inputMessage, setInputMessage] = useState("")
    const [selectedAgentId, setSelectedAgentId] = useState<string>("")
    const [isLoading, setIsLoading] = useState(false)
    const queryClient = useQueryClient()

    // 获取可用的智能体
    const { data: agents } = useQuery({
        queryKey: ["agents"],
        queryFn: () =>
            AgentsService.getAvailableSystemAgents({
                args: {},
                kwargs: {},
                skip: 0,
                limit: 100,
            }),
        enabled: !!user,
    })

    // 获取对话详情
    const { data: conversationDetails } = useQuery({
        queryKey: ["conversation", conversationId],
        queryFn: () =>
            ConversationsService.getConversationDetailed({
                args: {},
                kwargs: {},
                conversationId: conversationId!,
            }),
        enabled: !!conversationId && !!user,
    })

    // 发送消息
    const sendMessageMutation = useMutation({
        mutationFn: async (data: { message: string; agent_id: string; conversation_id?: string }) => {
            return ChatService.chatWithAgent({
                args: {},
                kwargs: {},
                requestBody: {
                    message: data.message,
                    agent_id: data.agent_id,
                    conversation_id: data.conversation_id,
                },
            })
        },
        onSuccess: () => {
            // 刷新对话详情和对话列表
            queryClient.invalidateQueries({ queryKey: ["conversation", conversationId] })
            queryClient.invalidateQueries({ queryKey: ["conversations"] })
            setInputMessage("")
            setIsLoading(false)
        },
        onError: () => {
            setIsLoading(false)
        },
    })

    const handleSendMessage = () => {
        if (!inputMessage.trim() || !selectedAgentId) return

        setIsLoading(true)
        sendMessageMutation.mutate({
            message: inputMessage,
            agent_id: selectedAgentId,
            conversation_id: conversationId || undefined,
        })
    }

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            handleSendMessage()
        }
    }

    // 渲染消息
    const renderMessage = (message: any) => {
        const isUser = message.role === "user"
        const isAssistant = message.role === "assistant"

        return (
            <Flex
                key={message.message_id}
                w="full"
                justify={isUser ? "flex-end" : "flex-start"}
                mb={4}
            >
                <HStack
                    align="flex-start"
                    maxW="70%"
                    flexDirection={isUser ? "row-reverse" : "row"}
                >
                    {/* 头像 */}
                    <Box
                        w={8}
                        h={8}
                        borderRadius="full"
                        bg={isUser ? "blue.500" : "gray.500"}
                        display="flex"
                        alignItems="center"
                        justifyContent="center"
                        color="white"
                        flexShrink={0}
                    >
                        {isUser ? <FiUser size={16} /> : <FiCpu size={16} />}
                    </Box>

                    {/* 消息内容 */}
                    <Box
                        bg={isUser ? "blue.500" : "gray.100"}
                        color={isUser ? "white" : "black"}
                        px={4}
                        py={3}
                        borderRadius="lg"
                        maxW="100%"
                    >
                        <Text fontSize="sm" whiteSpace="pre-wrap">
                            {message.content}
                        </Text>

                        {/* 显示智能体信息和事件 */}
                        {isAssistant && message.agent_name && (
                            <Text fontSize="xs" opacity={0.7} mt={1}>
                                由 {message.agent_name} 回复
                                {message.model_used && ` · ${message.model_used}`}
                                {message.events && message.events.length > 0 &&
                                    ` · ${message.events.length} 个事件`
                                }
                            </Text>
                        )}
                    </Box>
                </HStack>
            </Flex>
        )
    }

    return (
        <Flex direction="column" h="100vh">
            {/* 顶部工具栏 */}
            <Flex
                p={4}
                borderBottom="1px solid"
                borderColor="gray.200"
                align="center"
                bg="white"
            >
                <IconButton
                    aria-label="Toggle sidebar"
                    variant="ghost"
                    size="sm"
                    onClick={onToggleSidebar}
                    mr={3}
                >
                    <FiMenu />
                </IconButton>
                <Text fontSize="lg" fontWeight="semibold">
                    {conversationDetails?.title || "选择一个对话"}
                </Text>
            </Flex>

            {/* 消息区域 */}
            <Box flex={1} overflow="auto" p={4}>
                {conversationId ? (
                    <VStack align="stretch" gap={0}>
                        {conversationDetails?.messages?.map(renderMessage)}
                    </VStack>
                ) : (
                    <Flex
                        h="full"
                        align="center"
                        justify="center"
                        direction="column"
                        color="gray.500"
                    >
                        <Text fontSize="lg" mb={2}>
                            你好，{user?.full_name || user?.email}
                        </Text>
                        <Text fontSize="md">
                            我能为你做什么？
                        </Text>
                    </Flex>
                )}
            </Box>

            {/* 输入区域 */}
            <Box p={4} borderTop="1px solid" borderColor="gray.200" bg="white">
                {/* 智能体选择 */}
                {(!conversationId && agents?.data && agents.data.length > 0) && (
                    <Box mb={3}>
                        <Text fontSize="sm" mb={2} color="gray.600">
                            选择智能体：
                        </Text>
                        <select
                            value={selectedAgentId}
                            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSelectedAgentId(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '8px 12px',
                                borderRadius: '6px',
                                border: '1px solid #E2E8F0',
                                backgroundColor: 'white',
                                fontSize: '14px'
                            }}
                        >
                            <option value="">请选择一个智能体</option>
                            {agents.data.map((agent) => (
                                <option key={agent.agent_id} value={agent.agent_id}>
                                    {agent.name} - {agent.instruction || "无描述"}
                                </option>
                            ))}
                        </select>
                    </Box>
                )}

                <HStack>
                    <Input
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder={
                            !conversationId && !selectedAgentId
                                ? "请先选择一个智能体..."
                                : "输入你的问题..."
                        }
                        size="lg"
                        borderRadius="lg"
                        disabled={!conversationId && !selectedAgentId}
                    />
                    <Button
                        onClick={handleSendMessage}
                        colorScheme="blue"
                        size="lg"
                        borderRadius="lg"
                        disabled={!inputMessage.trim() || (!conversationId && !selectedAgentId)}
                        loading={isLoading}
                    >
                        <FiSend />
                    </Button>
                </HStack>
            </Box>
        </Flex>
    )
}

export default ChatArea
