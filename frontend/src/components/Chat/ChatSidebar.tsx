import {
    Box,
    Text,
    IconButton,
    Flex,
    Button,
} from "@chakra-ui/react"
import { FiMenu, FiPlus, FiSettings } from "react-icons/fi"
import { useQuery } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"

import { ConversationsService } from "@/client"
import useAuth from "@/hooks/useAuth"

interface ChatSidebarProps {
    isOpen: boolean
    onToggle: () => void
    selectedConversationId: string | null
    onSelectConversation: (id: string) => void
}

const ChatSidebar = ({
    isOpen,
    onToggle,
    selectedConversationId,
    onSelectConversation,
}: ChatSidebarProps) => {
    const { user } = useAuth()
    const navigate = useNavigate()

    // 获取最近对话列表
    const { data: recentConversations } = useQuery({
        queryKey: ["conversations", "recent"],
        queryFn: () => ConversationsService.getRecentConversations({
            args: {},
            kwargs: {},
            limit: 10
        }),
        enabled: !!user,
    })

    // 创建新对话
    const handleNewChat = async () => {
        console.log("Create new chat")
    }

    // 前往个人中心
    const handleSettings = () => {
        navigate({ to: "/settings" })
    }

    if (!isOpen) {
        return (
            <Box
                w="60px"
                h="100vh"
                bg="gray.50"
                borderRight="1px solid"
                borderColor="gray.200"
                display="flex"
                flexDirection="column"
                alignItems="center"
                py={4}
            >
                <IconButton
                    aria-label="Toggle sidebar"
                    variant="ghost"
                    onClick={onToggle}
                    mb={4}
                >
                    <FiMenu />
                </IconButton>
                <IconButton
                    aria-label="New chat"
                    variant="ghost"
                    onClick={handleNewChat}
                    mb={4}
                >
                    <FiPlus />
                </IconButton>
                <Box flex={1} />
                <IconButton
                    aria-label="Settings"
                    variant="ghost"
                    onClick={handleSettings}
                >
                    <FiSettings />
                </IconButton>
            </Box>
        )
    }

    return (
        <Box
            w="300px"
            h="100vh"
            bg="gray.50"
            borderRight="1px solid"
            borderColor="gray.200"
            display="flex"
            flexDirection="column"
        >
            {/* 顶部工具栏 */}
            <Flex p={4} align="center" justify="space-between">
                <IconButton
                    aria-label="Toggle sidebar"
                    variant="ghost"
                    size="sm"
                    onClick={onToggle}
                >
                    <FiMenu />
                </IconButton>
                <Text fontSize="lg" fontWeight="semibold">
                    对话列表
                </Text>
                <IconButton
                    aria-label="New chat"
                    variant="ghost"
                    size="sm"
                    onClick={handleNewChat}
                >
                    <FiPlus />
                </IconButton>
            </Flex>

            {/* 对话列表 */}
            <Box flex={1} overflow="auto" p={2}>
                {recentConversations?.data?.map((conversation) => (
                    <Box
                        key={conversation.conversation_id}
                        p={3}
                        mb={2}
                        bg={selectedConversationId === conversation.conversation_id.toString() ? "blue.50" : "transparent"}
                        borderRadius="md"
                        cursor="pointer"
                        onClick={() => onSelectConversation(conversation.conversation_id.toString())}
                        _hover={{ bg: "gray.100" }}
                    >
                        <Text fontSize="sm" fontWeight="medium" truncate>
                            {conversation.title}
                        </Text>
                        <Text fontSize="xs" color="gray.500">
                            {new Date(conversation.created_at).toLocaleDateString()}
                        </Text>
                    </Box>
                ))}
            </Box>

            {/* 底部设置 */}
            <Box p={4} borderTop="1px solid" borderColor="gray.200">
                <Button
                    variant="ghost"
                    w="full"
                    justifyContent="flex-start"
                    onClick={handleSettings}
                >
                    <FiSettings />
                    <Text ml={2}>个人中心</Text>
                </Button>
            </Box>
        </Box>
    )
}

export default ChatSidebar
