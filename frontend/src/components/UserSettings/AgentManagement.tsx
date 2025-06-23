import {
    Box,
    Text,
    VStack,
    HStack,
    Badge,
    Button,
    Flex,
} from "@chakra-ui/react"
import { FiTool, FiInfo } from "react-icons/fi"
import { useQuery } from "@tanstack/react-query"

import { AgentsService } from "@/client"
import useAuth from "@/hooks/useAuth"

const AgentManagement = () => {
    const { user } = useAuth()

    // 获取可用的系统智能体
    const { data: systemAgents, isLoading } = useQuery({
        queryKey: ["agents", "system"],
        queryFn: () => AgentsService.getAvailableSystemAgents({
            args: {},
            kwargs: {},
        }),
        enabled: !!user,
    })

    const handleViewAgent = (agentId: string) => {
        console.log("View agent details:", agentId)
        // TODO: 实现查看智能体详情
    }

    if (isLoading) {
        return <Text>加载中...</Text>
    }

    return (
        <Box>
            <Flex justify="space-between" align="center" mb={6}>
                <Box>
                    <Text fontSize="xl" fontWeight="semibold">
                        智能体管理
                    </Text>
                    <Text fontSize="sm" color="gray.500">
                        查看和了解可用的系统智能体
                    </Text>
                </Box>
            </Flex>

            <VStack align="stretch" gap={4}>
                {systemAgents?.data?.map((agent) => (
                    <Box
                        key={agent.agent_id}
                        p={6}
                        borderWidth={1}
                        borderRadius="lg"
                        bg="white"
                        shadow="sm"
                    >
                        <Flex justify="space-between" align="flex-start">
                            <Box flex={1}>
                                <HStack justify="space-between" align="flex-start" mb={4}>
                                    <Box>
                                        <HStack mb={2}>
                                            <Text fontSize="lg" fontWeight="semibold">
                                                {agent.name}
                                            </Text>
                                            {agent.is_system_agent && (
                                                <Badge colorScheme="blue" variant="subtle">
                                                    系统智能体
                                                </Badge>
                                            )}
                                            <Badge
                                                colorScheme={agent.status === "active" ? "green" : "gray"}
                                                variant="subtle"
                                            >
                                                {agent.status === "active" ? "可用" : "不可用"}
                                            </Badge>
                                        </HStack>

                                        <Text fontSize="sm" color="gray.600" mb={3}>
                                            {agent.instruction}
                                        </Text>

                                        {/* 团队信息 */}
                                        {agent.team && agent.team.length > 0 && (
                                            <Box mb={3}>
                                                <Text fontSize="sm" fontWeight="medium" mb={1}>
                                                    所属团队:
                                                </Text>
                                                <HStack wrap="wrap" gap={1}>
                                                    {agent.team.map((teamName, index) => (
                                                        <Badge key={index} variant="outline" size="sm">
                                                            {teamName}
                                                        </Badge>
                                                    ))}
                                                </HStack>
                                            </Box>
                                        )}

                                        {/* 模型信息 */}
                                        {agent.model_id && (
                                            <HStack>
                                                <FiTool size={16} color="gray" />
                                                <Text fontSize="sm" color="gray.600">
                                                    模型 ID: {agent.model_id}
                                                </Text>
                                            </HStack>
                                        )}
                                    </Box>

                                    <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => handleViewAgent(agent.agent_id)}
                                    >
                                        <FiInfo />
                                        <Text ml={2}>查看详情</Text>
                                    </Button>
                                </HStack>
                            </Box>
                        </Flex>
                    </Box>
                ))}

                {(!systemAgents?.data || systemAgents.data.length === 0) && (
                    <Box
                        p={8}
                        textAlign="center"
                        borderWidth={1}
                        borderRadius="lg"
                        borderStyle="dashed"
                        color="gray.500"
                    >
                        <Text mb={4}>暂无可用的智能体</Text>
                        <Text fontSize="sm" color="gray.400">
                            系统智能体将在配置完成后显示在这里。
                        </Text>
                    </Box>
                )}
            </VStack>
        </Box>
    )
}

export default AgentManagement
