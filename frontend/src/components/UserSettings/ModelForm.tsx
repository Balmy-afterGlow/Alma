import {
    Button,
    Input,
    VStack,
    HStack,
} from "@chakra-ui/react"
import { useForm } from "react-hook-form"
import { useMutation, useQueryClient } from "@tanstack/react-query"

import { ModelsService } from "@/client"
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

interface ModelFormProps {
    isOpen: boolean
    onClose: () => void
    llmId: string
    editingModel?: any
}

interface ModelFormData {
    name: string
    base_url?: string
}

const ModelForm = ({ isOpen, onClose, llmId, editingModel }: ModelFormProps) => {
    const queryClient = useQueryClient()

    const {
        register,
        handleSubmit,
        reset,
        formState: { errors }
    } = useForm<ModelFormData>({
        defaultValues: {
            name: editingModel?.name || '',
            base_url: editingModel?.base_url || '',
        }
    })

    // 创建模型
    const createMutation = useMutation({
        mutationFn: (data: ModelFormData) =>
            ModelsService.createUserModel({
                args: {},
                kwargs: {},
                requestBody: {
                    ...data,
                    llm_id: llmId,
                },
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['models'] })
            onClose()
            reset()
        },
    })

    // 更新模型
    const updateMutation = useMutation({
        mutationFn: (data: ModelFormData) =>
            ModelsService.updateUserModel({
                args: {},
                kwargs: {},
                modelId: editingModel.model_id,
                requestBody: data,
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['models'] })
            onClose()
            reset()
        },
    })

    const onSubmit = (data: ModelFormData) => {
        if (editingModel) {
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
                        {editingModel ? '编辑模型配置' : '添加模型配置'}
                    </DialogTitle>
                </DialogHeader>

                <DialogBody>
                    <form onSubmit={handleSubmit(onSubmit)} id="model-form">
                        <VStack align="stretch" gap={4}>
                            <Field
                                label="模型名称"
                                required
                                invalid={!!errors.name}
                                errorText={errors.name?.message}
                                helperText="例如：deepseek-chat, gpt-4o, claude-3-5-sonnet"
                            >
                                <Input
                                    {...register('name', {
                                        required: '请输入模型名称',
                                        maxLength: { value: 100, message: '模型名称不能超过100字符' }
                                    })}
                                    placeholder="例如：deepseek-chat"
                                />
                            </Field>

                            <Field
                                label="Base URL"
                                invalid={!!errors.base_url}
                                errorText={errors.base_url?.message}
                                helperText="可选，自定义API端点地址。如果为空将使用默认端点"
                            >
                                <Input
                                    {...register('base_url')}
                                    placeholder="https://api.deepseek.com"
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
                            form="model-form"
                            colorScheme="blue"
                            loading={isLoading}
                        >
                            {editingModel ? '更新' : '添加'}
                        </Button>
                    </HStack>
                </DialogFooter>

                <DialogCloseTrigger />
            </DialogContent>
        </DialogRoot>
    )
}

export default ModelForm
