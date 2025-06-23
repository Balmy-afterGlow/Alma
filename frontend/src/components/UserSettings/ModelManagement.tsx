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
import { FiPlus, FiEdit, FiTrash2, FiArrowLeft } from "react-icons/fi"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"

import { ModelsService } from "@/client"
import useAuth from "@/hooks/useAuth"
import ModelForm from "./ModelForm"

interface ModelManagementProps {
    llmId: string
    llmProvider: string
    onBack: () => void
}

const ModelManagement = ({ llmId, llmProvider, onBack }: ModelManagementProps) => {
    const { user } = useAuth()
    const { open, onOpen, onClose } = useDisclosure()
    const [editingModel, setEditingModel] = useState<any>(null)
    const queryClient = useQueryClient()

    // 获取该 LLM 下的所有模型
    const { data: models, isLoading } = useQuery({
        queryKey: ["models", llmId],
        queryFn: () => ModelsService.getUserModels({
            args: {},
            kwargs: {},
        }),
        enabled: !!user && !!llmId,
        select: (data) => ({
            ...data,
            data: data.data?.filter(model => model.llm_id === llmId) || []
        })
    })

    // 删除模型
    const deleteMutation = useMutation({
        mutationFn: (modelId: string) =>
            ModelsService.deleteUserModel({
                args: {},
                kwargs: {},
                modelId,
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['models'] })
        },
    })

    const handleAddModel = () => {
        setEditingModel(null)
        onOpen()
    }

    const handleEditModel = (model: any) => {
        setEditingModel(model)
        onOpen()
    }

    const handleDeleteModel = (modelId: string) => {
        if (confirm('确认删除这个模型配置吗？此操作不可撤销。')) {
            deleteMutation.mutate(modelId)
        }
    }

    if (isLoading) {
        return <Text>加载中...</Text>
    }

    return (
        <Box>
            <Flex justify="space-between" align="center" mb={6}>
                <Box>
                    <HStack mb={2}>
                        <IconButton
                            aria-label="返回"
                            size="sm"
                            variant="ghost"
                            onClick={onBack}
                        >
                            <FiArrowLeft />
                        </IconButton>
                        <Text fontSize="xl" fontWeight="semibold">
                            {llmProvider} - 模型管理
                        </Text>
                    </HStack>
                    <Text fontSize="sm" color="gray.500" ml={10}>
                        管理 {llmProvider} 提供商下的具体模型配置
                    </Text>
                </Box>
                <Button onClick={handleAddModel} colorScheme="blue">
                    <FiPlus />
                    <Text ml={2}>添加模型</Text>
                </Button>
            </Flex>

            <VStack align="stretch" gap={4}>
                {models?.data?.map((model) => (
                    <Box
                        key={model.model_id}
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
                                                {model.name}
                                            </Text>
                                            <Badge colorScheme="green" variant="subtle">
                                                模型
                                            </Badge>
                                        </HStack>

                                        <Text fontSize="sm" color="gray.500" mb={3}>
                                            模型 ID: {model.model_id}
                                        </Text>

                                        {/* Base URL */}
                                        {model.base_url && (
                                            <Box>
                                                <Text fontSize="sm" fontWeight="medium" mb={1}>
                                                    API 端点:
                                                </Text>
                                                <Text fontSize="sm" color="gray.600" fontFamily="mono">
                                                    {model.base_url}
                                                </Text>
                                            </Box>
                                        )}
                                    </Box>

                                    <HStack>
                                        <IconButton
                                            aria-label="编辑模型"
                                            size="sm"
                                            variant="ghost"
                                            onClick={() => handleEditModel(model)}
                                        >
                                            <FiEdit />
                                        </IconButton>
                                        <IconButton
                                            aria-label="删除模型"
                                            size="sm"
                                            variant="ghost"
                                            colorScheme="red"
                                            onClick={() => handleDeleteModel(model.model_id)}
                                        >
                                            <FiTrash2 />
                                        </IconButton>
                                    </HStack>
                                </HStack>
                            </Box>
                        </Flex>
                    </Box>
                ))}

                {(!models?.data || models.data.length === 0) && (
                    <Box
                        p={8}
                        textAlign="center"
                        borderWidth={1}
                        borderRadius="lg"
                        borderStyle="dashed"
                        color="gray.500"
                    >
                        <Text mb={4}>此 LLM 提供商下还没有配置任何模型</Text>
                        <Text fontSize="sm" mb={4} color="gray.400">
                            添加具体的模型配置（如 deepseek-chat、deepseek-reasoner 等）
                        </Text>
                        <Button onClick={handleAddModel} variant="outline">
                            添加第一个模型
                        </Button>
                    </Box>
                )}
            </VStack>

            {/* 模型配置表单对话框 */}
            <ModelForm
                isOpen={open}
                onClose={onClose}
                llmId={llmId}
                editingModel={editingModel}
            />
        </Box>
    )
}

export default ModelManagement
