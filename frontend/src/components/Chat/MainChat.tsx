import { Box, Flex } from "@chakra-ui/react"
import { useState } from "react"
import ChatSidebar from "./ChatSidebar"
import ChatArea from "./ChatArea"

interface MainChatProps { }

const MainChat = ({ }: MainChatProps) => {
    const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null)
    const [sidebarOpen, setSidebarOpen] = useState(true)

    return (
        <Flex h="100vh">
            {/* 侧边栏 */}
            <ChatSidebar
                isOpen={sidebarOpen}
                onToggle={() => setSidebarOpen(!sidebarOpen)}
                selectedConversationId={selectedConversationId}
                onSelectConversation={setSelectedConversationId}
            />

            {/* 主要聊天区域 */}
            <Box flex={1} overflow="hidden">
                <ChatArea
                    conversationId={selectedConversationId}
                    onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
                />
            </Box>
        </Flex>
    )
}

export default MainChat
