<script setup lang="ts">
import {
  DeleteOutlined,
  PlusOutlined,
} from '@ant-design/icons-vue'
import type { FormInstance, TableColumnsType } from 'ant-design-vue'
import { message } from 'ant-design-vue'
import { computed, reactive, ref } from 'vue'
import type { KBSchema } from '@/api/globals.d'
import { useI18n } from '@/locales'
import Apis from '@/api'

type SchemaFieldType = 'string' | 'integer' | 'float'

interface SchemaRow {
  id: string
  name: string
  type: SchemaFieldType | ''
  description: string
}

const emit = defineEmits<{
  (e: 'success'): void
  (e: 'cancel'): void
}>()

const { t } = useI18n()
const visible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const createdKbName = ref('')

const formState = reactive({
  kb_name: '',
  kb_description: '',
})

const fieldTypeOptions: Array<{ label: string, value: SchemaFieldType }> = [
  { label: 'string', value: 'string' },
  { label: 'integer', value: 'integer' },
  { label: 'float', value: 'float' },
]

const schemaRows = ref<SchemaRow[]>([])

const rules: Record<string, any[]> = {
  kb_name: [
    { required: true, whitespace: true, message: t('请输入资产库名称'), trigger: 'blur' },
  ],
}

const tableColumns = computed<TableColumnsType<SchemaRow>>(() => ([
  { title: t('名称'), dataIndex: 'name', key: 'name', width: 220 },
  { title: t('类型'), dataIndex: 'type', key: 'type', width: 150 },
  { title: t('描述'), dataIndex: 'description', key: 'description', width: 320 },
  { title: t('操作'), key: 'actions', width: 96, align: 'center' },
]))

function createDefaultRow(): SchemaRow {
  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    name: '',
    type: 'string',
    description: '',
  }
}

function resetModalState() {
  formState.kb_name = ''
  formState.kb_description = ''
  schemaRows.value = [createDefaultRow()]
  createdKbName.value = ''
}

function show() {
  resetModalState()
  visible.value = true
}

function handleCancel() {
  visible.value = false
  emit('cancel')
}

function addRow() {
  schemaRows.value.push(createDefaultRow())
}

function removeRow(index?: number) {
  if (typeof index !== 'number')
    return
  schemaRows.value.splice(index, 1)
}

function validateSchemaRows() {
  if (!schemaRows.value.length) {
    message.warning(t('请至少新增一行Schema字段'))
    return false
  }

  const nameSet = new Set<string>()
  for (const [index, row] of schemaRows.value.entries()) {
    const fieldName = row.name.trim()
    if (!fieldName || !row.type) {
      message.warning(t('请完善第 {index} 行字段配置', { index: index + 1 }))
      return false
    }

    if (nameSet.has(fieldName)) {
      message.warning(t('字段名称不能重复'))
      return false
    }
    nameSet.add(fieldName)

    if (row.description.length > 500) {
      message.warning(t('第 {index} 行描述不能超过500字符', { index: index + 1 }))
      return false
    }
  }

  return true
}

async function createKnowledgeBaseIfNeeded(kbName: string) {
  if (createdKbName.value === kbName)
    return

  const response = await Apis.knowledgeBaseManagement.create_knowledge_base_api_v1_kb_base_post({
    data: {
      kb_name: kbName,
      kb_type: 'structured',
      kb_description: formState.kb_description.trim(),
    },
  })

  if (!response.data)
    throw new Error(t('未返回资产库ID'))

  createdKbName.value = kbName
}

function buildSchemaPayload(): KBSchema {
  const allFieldNames = schemaRows.value
    .map(row => row.name.trim())
    .filter(Boolean)

  const uniqueFieldNames = Array.from(new Set(allFieldNames))
  const defaultInputField = uniqueFieldNames[0] ? [uniqueFieldNames[0]] : []

  return {
    fields: schemaRows.value.map(row => ({
      field_name: row.name.trim(),
      field_type: row.type as SchemaFieldType,
      field_desc: row.description.trim(),
    })),
    match_rules: [
      {
        match_policies: [
          {
            mode: 'es_text',
            input_fields: defaultInputField,
          },
        ],
        output_fields: uniqueFieldNames,
      },
    ],
  }
}

async function handleSave() {
  try {
    await formRef.value?.validate()
    if (!validateSchemaRows())
      return

    const kbName = formState.kb_name.trim()
    submitting.value = true

    await createKnowledgeBaseIfNeeded(kbName)

    await Apis.knowledgeBaseManagement.update_kb_schema_api_v1_kb_base__kb_name__schema_post({
      pathParams: {
        kb_name: kbName,
      },
      data: buildSchemaPayload(),
    })

    message.success(t('Schema资产库创建成功'))
    visible.value = false
    emit('success')
  }
  catch (error) {
    console.error(error)
    message.error(t('创建失败: {message}', { message: (error as any).message || t('未知错误') }))
  }
  finally {
    submitting.value = false
  }
}

defineExpose({
  show,
})
</script>

<template>
  <a-drawer
    v-model:open="visible"
    :title="t('Schema方式创建资产库')"
    width="40%"
    :body-style="{ padding: '20px 20px 0', display: 'flex', flexDirection: 'column', height: '100%' }"
    @close="handleCancel"
  >
    <div class="schema-drawer-content">
      <a-form
        ref="formRef"
        :model="formState"
        :rules="rules"
        layout="vertical"
      >
        <a-form-item :label="t('资产库名称')" name="kb_name">
          <a-input v-model:value="formState.kb_name" :placeholder="t('请输入资产库名称')" />
        </a-form-item>

        <a-form-item :label="t('描述')" name="kb_description">
          <a-textarea
            v-model:value="formState.kb_description"
            :placeholder="t('请输入资产库描述（可选）')"
            :rows="2"
            :maxlength="500"
            show-count
          />
        </a-form-item>
      </a-form>

      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-gray-700">{{ t('Schema字段配置') }}</span>
        <a-button type="link" class="px-0" @click="addRow">
          {{ t('新增') }}
        </a-button>
      </div>

      <div class="schema-table-wrap">
        <a-table
          :columns="tableColumns"
          :data-source="schemaRows"
          :pagination="false"
          row-key="id"
          size="small"
          bordered
          :scroll="{ x: 780 }"
        >
          <template #bodyCell="{ column, record, index }">
            <template v-if="column.key === 'name'">
              <a-input
                v-model:value="record.name"
                :placeholder="t('请输入字段名称')"
                :maxlength="100"
              />
            </template>

            <template v-else-if="column.key === 'type'">
              <a-select v-model:value="record.type" :placeholder="t('请选择字段类型')">
                <a-select-option v-for="option in fieldTypeOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </a-select-option>
              </a-select>
            </template>

            <template v-else-if="column.key === 'description'">
              <a-textarea
                v-model:value="record.description"
                :placeholder="t('请输入描述（选填，500字符以内）')"
                :maxlength="500"
                :auto-size="{ minRows: 1, maxRows: 2 }"
              />
            </template>

            <template v-else-if="column.key === 'actions'">
              <a-space size="small">
                <a-tooltip :title="t('新增')">
                  <a-button type="text" @click="addRow">
                    <template #icon>
                      <plus-outlined />
                    </template>
                  </a-button>
                </a-tooltip>
                <a-tooltip :title="t('删除')">
                  <a-button danger type="text" @click="removeRow(index)">
                    <template #icon>
                      <delete-outlined />
                    </template>
                  </a-button>
                </a-tooltip>
              </a-space>
            </template>
          </template>
        </a-table>
      </div>

      <div class="schema-drawer-footer">
        <a-button @click="handleCancel">
          {{ t('取消') }}
        </a-button>
        <a-button type="primary" :loading="submitting" @click="handleSave">
          {{ t('保存') }}
        </a-button>
      </div>
    </div>
  </a-drawer>
</template>

<style scoped>
.schema-drawer-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.schema-table-wrap {
  flex: 1;
  min-height: 0;
  overflow: auto;
}

.schema-drawer-footer {
  margin-top: 12px;
  padding: 14px 0 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
