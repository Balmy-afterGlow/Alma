import {
    Box,
    Button,
    Flex,
    Text,
    VStack,
    HStack,
    IconButton,
    Badge,
    useDisclosure,
} from "@chakra-ui/react"
import { FiPlus, FiEdit, FiTrash2, FiCpu } from "react-icons/fi"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"

import { LlmConfigsService } from "@/client"
import useAuth from "@/hooks/useAuth"
import LLMConfigForm from "./LLMConfigForm"
import ModelManagement from "./ModelManagement"

const LLMConfiguration = () => {
    const { user } = useAuth()
    const { open, onOpen, onClose } = useDisclosure()
    const [editingConfig, setEditingConfig] = useState<any>(null)
    const [viewMode, setViewMode] = useState<'list' | 'models'>('list')
    const [selectedLLM, setSelectedLLM] = useState<any>(null)
    const queryClient = useQueryClient()

    // 获取用户的 LLM 配置
    const { data: llmConfigs, isLoading } = useQuery({
        queryKey: ["llmConfigs"],
        queryFn: () => LlmConfigsService.getUserLlmConfigs({
            args: {},
            kwargs: {},
        }),
        enabled: !!user,
    })

    // 删除 LLM 配置
    const deleteMutation = useMutation({
        mutationFn: (llmId: string) =>
            LlmConfigsService.deleteUserLlmConfig({
                args: {},
                kwargs: {},
                llmId,
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['llmConfigs'] })
        },
    })

    const handleAddConfig = () => {
        setEditingConfig(null)
        onOpen()
    }

    const handleEditConfig = (config: any) => {
        setEditingConfig(config)
        onOpen()
    }

    const handleDeleteConfig = (configId: string) => {
        if (confirm('确认删除这个 LLM 配置吗？这会同时删除该配置下的所有模型。此操作不可撤销。')) {
            deleteMutation.mutate(configId)
        }
    }

    const handleViewModels = (llm: any) => {
        setSelectedLLM(llm)
        setViewMode('models')
    }

    const handleBackToList = () => {
        setViewMode('list')
        setSelectedLLM(null)
    }

    if (isLoading) {
        return <Text>加载中...</Text>
    }

    // 如果是查看模型模式，显示模型管理组件
    if (viewMode === 'models' && selectedLLM) {
        return (
            <ModelManagement
                llmId={selectedLLM.llm_id}
                llmProvider={selectedLLM.provider}
                onBack={handleBackToList}
            />
        )
    }

    return (
        <Box>
            <Flex justify="space-between" align="center" mb={6}>
                <Box>
                    <Text fontSize="xl" fontWeight="semibold">
                        LLM 配置管理
                    </Text>
                    <Text fontSize="sm" color="gray.500">
                        管理你的 AI 模型提供商配置和具体模型
                    </Text>
                </Box>
                <Button onClick={handleAddConfig} colorScheme="blue">
                    <FiPlus />
                    <Text ml={2}>添加 LLM 提供商</Text>
                </Button>
            </Flex>

            <VStack align="stretch" gap={4}>
                {llmConfigs?.data?.map((config) => (
                    <Box
                        key={config.llm_id}
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
                                                {config.provider}
                                            </Text>
                                            <Badge colorScheme="blue" variant="subtle">
                                                LLM 提供商
                                            </Badge>
                                        </HStack>

                                        <Text fontSize="sm" color="gray.500" mb={3}>
                                            LLM ID: {config.llm_id}
                                        </Text>
                                    </Box>

                                    <HStack>
                                        <IconButton
                                            aria-label="查看模型"
                                            size="sm"
                                            variant="ghost"
                                            onClick={() => handleViewModels(config)}
                                            colorScheme="blue"
                                        >
                                            <FiCpu />
                                        </IconButton>
                                        <IconButton
                                            aria-label="编辑配置"
                                            size="sm"
                                            variant="ghost"
                                            onClick={() => handleEditConfig(config)}
                                        >
                                            <FiEdit />
                                        </IconButton>
                                        <IconButton
                                            aria-label="删除配置"
                                            size="sm"
                                            variant="ghost"
                                            colorScheme="red"
                                            onClick={() => handleDeleteConfig(config.llm_id)}
                                        >
                                            <FiTrash2 />
                                        </IconButton>
                                    </HStack>
                                </HStack>

                                {/* 配置信息显示 */}
                                <Box
                                    p={3}
                                    bg="gray.50"
                                    borderRadius="md"
                                >
                                    <Text fontSize="sm" color="gray.600">
                                        点击"查看模型"按钮可以管理此 LLM 提供商下的具体模型配置
                                    </Text>
                                </Box>
                            </Box>
                        </Flex>
                    </Box>
                ))}

                {(!llmConfigs?.data || llmConfigs.data.length === 0) && (
                    <Box
                        p={8}
                        textAlign="center"
                        borderWidth={1}
                        borderRadius="lg"
                        borderStyle="dashed"
                        color="gray.500"
                    >
                        <Text mb={4}>还没有配置任何 LLM 提供商</Text>
                        <Text fontSize="sm" mb={4} color="gray.400">
                            添加 LLM 提供商（如 DeepSeek、OpenAI 等）后，你可以在其下配置具体的模型。
                        </Text>
                        <Button onClick={handleAddConfig} variant="outline">
                            添加第一个 LLM 提供商
                        </Button>
                    </Box>
                )}
            </VStack>

            {/* LLM 配置表单对话框 */}
            <LLMConfigForm
                isOpen={open}
                onClose={onClose}
                editingConfig={editingConfig}
            />
        </Box>
    )
}

export default LLMConfiguration
