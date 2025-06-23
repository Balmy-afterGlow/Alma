import {
    Button,
    Input,
    Text,
    VStack,
    HStack,
} from "@chakra-ui/react"
import { useForm } from "react-hook-form"
import { useMutation, useQueryClient } from "@tanstack/react-query"

import { LlmConfigsService } from "@/client"
import {
    DialogActionTrigger,
    DialogBody,
    DialogCloseTrigger,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogRoot,
    DialogTitle,
} from "@/components/ui/dialog"
import { Field } from "@/components/ui/field"

interface LLMConfigFormProps {
    isOpen: boolean
    onClose: () => void
    editingConfig?: any
}

interface LLMConfigFormData {
    provider: string
    api_key: string
}

const LLMConfigForm = ({ isOpen, onClose, editingConfig }: LLMConfigFormProps) => {
    const queryClient = useQueryClient()

    const {
        register,
        handleSubmit,
        reset,
        formState: { errors }
    } = useForm<LLMConfigFormData>({
        defaultValues: {
            provider: editingConfig?.provider || '',
            api_key: '',
        }
    })

    // 创建 LLM 配置
    const createMutation = useMutation({
        mutationFn: (data: LLMConfigFormData) =>
            LlmConfigsService.createUserLlmConfig({
                args: {},
                kwargs: {},
                requestBody: data,
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['llmConfigs'] })
            onClose()
            reset()
        },
    })

    // 更新 LLM 配置
    const updateMutation = useMutation({
        mutationFn: (data: LLMConfigFormData) =>
            LlmConfigsService.updateUserLlmConfig({
                args: {},
                kwargs: {},
                llmId: editingConfig.llm_id,
                requestBody: data,
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['llmConfigs'] })
            onClose()
            reset()
        },
    })

    const onSubmit = (data: LLMConfigFormData) => {
        if (editingConfig) {
            updateMutation.mutate(data)
        } else {
            createMutation.mutate(data)
        }
    }

    const isLoading = createMutation.isPending || updateMutation.isPending

    return (
        <DialogRoot open={isOpen} onOpenChange={() => onClose()}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>
                        {editingConfig ? '编辑 LLM 配置' : '添加 LLM 配置'}
                    </DialogTitle>
                </DialogHeader>

                <DialogBody>
                    <form onSubmit={handleSubmit(onSubmit)} id="llm-config-form">
                        <VStack align="stretch" gap={4}>
                            <Field
                                label="提供商名称"
                                required
                                invalid={!!errors.provider}
                                errorText={errors.provider?.message}
                            >
                                <Input
                                    {...register('provider', {
                                        required: '请输入提供商名称',
                                        maxLength: { value: 50, message: '提供商名称不能超过50字符' }
                                    })}
                                    placeholder="例如：DeepSeek, OpenAI, Claude"
                                />
                            </Field>

                            <Field
                                label="API Key"
                                required
                                invalid={!!errors.api_key}
                                errorText={errors.api_key?.message}
                                helperText="API Key 将被安全加密存储"
                            >
                                <Input
                                    type="password"
                                    {...register('api_key', {
                                        required: '请输入 API Key'
                                    })}
                                    placeholder="输入你的 API Key"
                                />
                            </Field>
                        </VStack>
                    </form>
                </DialogBody>

                <DialogFooter>
                    <HStack>
                        <DialogActionTrigger asChild>
                            <Button variant="outline">取消</Button>
                        </DialogActionTrigger>
                        <Button
                            type="submit"
                            form="llm-config-form"
                            colorScheme="blue"
                            loading={isLoading}
                        >
                            {editingConfig ? '更新' : '添加'}
                        </Button>
                    </HStack>
                </DialogFooter>

                <DialogCloseTrigger />
            </DialogContent>
        </DialogRoot>
    )
}

export default LLMConfigForm
