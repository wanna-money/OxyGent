<script setup lang="ts">
import {
  ApiOutlined,
  AppstoreOutlined,
  CloseOutlined,
  CloudServerOutlined,
  CodeOutlined,
  CopyOutlined,
  PlusOutlined,
  RobotOutlined,
  ThunderboltOutlined,
  ToolOutlined,
} from '@ant-design/icons-vue'
import { Modal, message } from 'ant-design-vue'
import { computed, reactive, ref, watch } from 'vue'
import type { TriggerCondition, TriggerCreateRequest } from '@/api/globals.d'
import { useI18n } from '@/locales'
import Apis from '@/api'

interface AgentTriggerItem {
  trigger_id: string
  trigger_name: string
  url: string
  conditions: TriggerCondition[]
}

interface Props {
  bankName: string
}

const props = defineProps<Props>()
const { t } = useI18n()

const triggerList = ref<AgentTriggerItem[]>([])
const triggerLoading = ref(false)
const creatingTrigger = ref(false)
const deletingTriggerId = ref('')
const hoveredTriggerId = ref('')
const createdPriorityIds = ref<string[]>([])
const pendingCreatedMatchers = ref<Array<{ trigger_name: string, url: string, status: string }>>([])

const createModalOpen = ref(false)
const createForm = reactive({
  trigger_name: '',
  url: '',
  status_value: '',
})

const CHUNK_STATUS_ENUM = ['待分配', '待标注', '待审核', '待发布', '已发布'] as const

const statusOptions = CHUNK_STATUS_ENUM.map(status => ({
  label: status,
  value: status,
}))

const iconComponents = [
  RobotOutlined,
  ApiOutlined,
  ToolOutlined,
  CodeOutlined,
  ThunderboltOutlined,
  CloudServerOutlined,
  AppstoreOutlined,
]

const triggerIconMap = reactive<Record<string, number>>({})
const iconSeedOrder = ref<number[]>([])

const canCreateTrigger = computed(() => !!props.bankName)

function normalizeCondition(condition: any): TriggerCondition {
  return {
    field_name: String(condition?.field_name || ''),
    field_value: String(condition?.field_value || ''),
    operator: condition?.operator || 'eq',
  }
}

function normalizeTrigger(item: any, index: number): AgentTriggerItem | null {
  const triggerId = item?.trigger_id || item?.id || item?.triggerId
  if (!triggerId)
    return null

  return {
    trigger_id: String(triggerId),
    trigger_name: String(item?.trigger_name || `Agent-${index + 1}`),
    url: String(item?.url || ''),
    conditions: Array.isArray(item?.conditions) ? item.conditions.map(normalizeCondition) : [],
  }
}

function getStatusValueFromConditions(conditions: TriggerCondition[]) {
  const matchedCondition = conditions.find((condition) => {
    return condition.field_name === 'sys_status' && (condition.operator || 'eq') === 'eq'
  })
  return String(matchedCondition?.field_value || '')
}

function getTriggerStatus(item: AgentTriggerItem) {
  return getStatusValueFromConditions(item.conditions) || String(item.conditions?.[0]?.field_value || '--')
}

function sortTriggersByPriority(triggers: AgentTriggerItem[]) {
  const priorityMap = new Map(createdPriorityIds.value.map((triggerId, index) => [triggerId, index]))
  return [...triggers].sort((left, right) => {
    const leftPriority = priorityMap.has(left.trigger_id) ? priorityMap.get(left.trigger_id)! : Number.MAX_SAFE_INTEGER
    const rightPriority = priorityMap.has(right.trigger_id) ? priorityMap.get(right.trigger_id)! : Number.MAX_SAFE_INTEGER
    return leftPriority - rightPriority
  })
}

function parseTriggerList(rawData: any): AgentTriggerItem[] {
  if (Array.isArray(rawData)) {
    return rawData.map(normalizeTrigger).filter(Boolean) as AgentTriggerItem[]
  }

  if (Array.isArray(rawData?.items)) {
    return rawData.items.map(normalizeTrigger).filter(Boolean) as AgentTriggerItem[]
  }

  if (Array.isArray(rawData?.triggers)) {
    return rawData.triggers.map(normalizeTrigger).filter(Boolean) as AgentTriggerItem[]
  }

  return []
}

function ensureIconSeedOrder() {
  if (iconSeedOrder.value.length > 0)
    return

  iconSeedOrder.value = Array.from({ length: iconComponents.length }, (_, index) => index)
    .sort(() => Math.random() - 0.5)
}

function pickRandomUniqueIcon(usedIndexes: Set<number>) {
  ensureIconSeedOrder()
  const availableIndexes = iconSeedOrder.value.filter(index => !usedIndexes.has(index))
  if (availableIndexes.length > 0) {
    const randomIndex = Math.floor(Math.random() * availableIndexes.length)
    return availableIndexes[randomIndex] ?? 0
  }
  return iconSeedOrder.value[Math.floor(Math.random() * iconSeedOrder.value.length)] ?? 0
}

function syncTriggerIcons(triggers: AgentTriggerItem[]) {
  const nextMap: Record<string, number> = {}
  const usedIndexes = new Set<number>()

  for (const trigger of triggers) {
    const existing = triggerIconMap[trigger.trigger_id]
    if (typeof existing === 'number' && !usedIndexes.has(existing)) {
      nextMap[trigger.trigger_id] = existing
      usedIndexes.add(existing)
    }
  }

  for (const trigger of triggers) {
    if (nextMap[trigger.trigger_id] !== undefined)
      continue
    const iconIndex = pickRandomUniqueIcon(usedIndexes)
    nextMap[trigger.trigger_id] = iconIndex
    usedIndexes.add(iconIndex)
  }

  for (const key of Object.keys(triggerIconMap)) {
    delete triggerIconMap[key]
  }
  Object.assign(triggerIconMap, nextMap)
}

function getTriggerIcon(triggerId: string) {
  const iconIndex = triggerIconMap[triggerId] ?? 0
  return iconComponents[iconIndex] || RobotOutlined
}

async function fetchTriggerList() {
  if (!props.bankName) {
    triggerList.value = []
    for (const key of Object.keys(triggerIconMap)) {
      delete triggerIconMap[key]
    }
    return
  }

  triggerLoading.value = true
  try {
    const response = await Apis.trigger.get_triggers_api_v1_trigger__kb_name___get({
      pathParams: {
        kb_name: props.bankName,
      },
    })

    const normalizedList = parseTriggerList((response as any)?.data)

    if (pendingCreatedMatchers.value.length > 0) {
      const unmatchedMatchers: Array<{ trigger_name: string, url: string, status: string }> = []
      for (const matcher of pendingCreatedMatchers.value) {
        const matchedTrigger = normalizedList.find((item) => {
          return item.trigger_name === matcher.trigger_name
            && item.url === matcher.url
            && getStatusValueFromConditions(item.conditions) === matcher.status
        })
        if (matchedTrigger) {
          createdPriorityIds.value = [
            matchedTrigger.trigger_id,
            ...createdPriorityIds.value.filter(triggerId => triggerId !== matchedTrigger.trigger_id),
          ]
        }
        else {
          unmatchedMatchers.push(matcher)
        }
      }
      pendingCreatedMatchers.value = unmatchedMatchers
    }

    const availableIds = new Set(normalizedList.map(item => item.trigger_id))
    createdPriorityIds.value = createdPriorityIds.value.filter(triggerId => availableIds.has(triggerId))

    const sortedList = sortTriggersByPriority(normalizedList)
    triggerList.value = sortedList
    syncTriggerIcons(sortedList)
  }
  catch (error) {
    console.error(error)
    message.error(t('获取 Agent 列表失败'))
  }
  finally {
    triggerLoading.value = false
  }
}

function resetCreateForm() {
  createForm.trigger_name = ''
  createForm.url = ''
  createForm.status_value = ''
}

function openCreateModal() {
  if (!props.bankName) {
    message.warning(t('新增 Agent 前请先指定 bank_name'))
    return
  }
  resetCreateForm()
  createModalOpen.value = true
}

function buildCreatePayload(): TriggerCreateRequest | null {
  const triggerName = createForm.trigger_name.trim()
  const url = createForm.url.trim()

  if (!triggerName) {
    message.warning(t('请输入 Trigger 名称'))
    return null
  }

  if (!url) {
    message.warning(t('请输入回调 URL'))
    return null
  }

  if (!createForm.status_value) {
    message.warning(t('请选择状态'))
    return null
  }

  return {
    trigger_name: triggerName,
    url,
    conditions: [
      {
        field_name: 'sys_status',
        field_value: createForm.status_value,
        operator: 'eq',
      },
    ],
  }
}

async function handleCreateTrigger() {
  if (!props.bankName) {
    message.error(t('缺少 bank_name'))
    return
  }

  let payload: TriggerCreateRequest | null = null
  try {
    payload = buildCreatePayload()
  }
  catch (error: any) {
    message.warning(error?.message || t('请求失败'))
    return
  }
  if (!payload)
    return

  creatingTrigger.value = true
  try {
    await Apis.trigger.create_trigger_api_v1_trigger__kb_name___post({
      pathParams: {
        kb_name: props.bankName,
      },
      data: payload,
    })

    pendingCreatedMatchers.value = [
      {
        trigger_name: payload.trigger_name,
        url: payload.url,
        status: String(payload.conditions?.[0]?.field_value || ''),
      },
      ...pendingCreatedMatchers.value,
    ]

    message.success(t('创建 Agent 成功'))
    createModalOpen.value = false
    await fetchTriggerList()
  }
  catch (error: any) {
    console.error(error)
    message.error(t('创建 Agent 失败: {message}', { message: error?.message || t('未知错误') }))
  }
  finally {
    creatingTrigger.value = false
  }
}

async function handleDeleteTrigger(item: AgentTriggerItem) {
  if (!props.bankName || !item.trigger_id)
    return

  deletingTriggerId.value = item.trigger_id
  try {
    await Apis.trigger.delete_trigger_api_v1_trigger__kb_name___trigger_id__delete({
      pathParams: {
        kb_name: props.bankName,
        trigger_id: item.trigger_id,
      },
    })
    message.success(t('删除 Agent 成功'))
    await fetchTriggerList()
  }
  catch (error: any) {
    console.error(error)
    message.error(t('删除 Agent 失败: {message}', { message: error?.message || t('未知错误') }))
  }
  finally {
    deletingTriggerId.value = ''
  }
}

function confirmDeleteTrigger(item: AgentTriggerItem) {
  Modal.confirm({
    title: t('确定删除 Agent「{name}」吗？', { name: item.trigger_name }),
    okText: t('删除'),
    cancelText: t('取消'),
    okType: 'danger',
    async onOk() {
      await handleDeleteTrigger(item)
    },
  })
}

async function copyText(value: string, successMessage?: string) {
  const text = String(value || '').trim()
  if (!text || text === '--')
    return

  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
    }
    else {
      const textarea = document.createElement('textarea')
      textarea.value = text
      textarea.setAttribute('readonly', 'readonly')
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
    }
    message.success(successMessage || t('复制成功'))
  }
  catch (error) {
    console.error(error)
    message.error(t('复制失败，请手动复制'))
  }
}

watch(
  () => props.bankName,
  () => {
    fetchTriggerList()
  },
  { immediate: true },
)
</script>

<template>
  <aside class="annotation-agent-dock">
    <div class="annotation-agent-dock-inner">
      <a-spin :spinning="triggerLoading" size="small">
        <div class="agent-list">
          <div
            v-for="trigger in triggerList"
            :key="trigger.trigger_id"
            class="agent-item-wrap"
            @mouseleave="hoveredTriggerId = ''"
          >
            <a-popover
              trigger="hover"
              placement="rightTop"
              overlay-class-name="agent-info-popover"
            >
              <template #content>
                <div class="agent-info-card">
                  <div class="agent-info-row agent-info-id-row">
                    <span class="agent-info-label">{{ t('ID') }}</span>
                    <span class="agent-info-value" @dblclick="copyText(trigger.trigger_id)">
                      {{ trigger.trigger_id || '--' }}
                    </span>
                    <button
                      class="agent-copy-btn"
                      :title="t('复制')"
                      @click.stop="copyText(trigger.trigger_id, t('Trigger ID 已复制'))"
                    >
                      <copy-outlined />
                    </button>
                  </div>

                  <div class="agent-info-row">
                    <span class="agent-info-label">URL</span>
                    <span class="agent-info-value" @dblclick="copyText(trigger.url)">
                      {{ trigger.url || '--' }}
                    </span>
                  </div>

                  <div class="agent-info-row">
                    <span class="agent-info-label">{{ t('名称') }}</span>
                    <span class="agent-info-value" @dblclick="copyText(trigger.trigger_name)">
                      {{ trigger.trigger_name || '--' }}
                    </span>
                  </div>

                  <div class="agent-info-row">
                    <span class="agent-info-label">{{ t('状态') }}</span>
                    <span class="agent-info-value" @dblclick="copyText(getTriggerStatus(trigger))">
                      {{ getTriggerStatus(trigger) }}
                    </span>
                  </div>
                </div>
              </template>

              <button class="agent-item-btn" @mouseenter="hoveredTriggerId = trigger.trigger_id">
                <component :is="getTriggerIcon(trigger.trigger_id)" class="text-[22px]" />
              </button>
            </a-popover>
            <button
              class="agent-delete-btn"
              :class="{ visible: hoveredTriggerId === trigger.trigger_id }"
              :disabled="deletingTriggerId === trigger.trigger_id"
              @click.stop="confirmDeleteTrigger(trigger)"
            >
              <close-outlined />
            </button>
          </div>
        </div>
      </a-spin>

      <a-tooltip :title="canCreateTrigger ? t('新增 Agent') : t('新增 Agent 前请先指定 bank_name')">
        <button
          class="agent-add-btn"
          :disabled="!canCreateTrigger"
          @click="openCreateModal"
        >
          <plus-outlined class="text-[26px]" />
        </button>
      </a-tooltip>
    </div>

    <a-modal
      v-model:open="createModalOpen"
      :title="t('新增 Agent')"
      :confirm-loading="creatingTrigger"
      :ok-text="t('保存')"
      @ok="handleCreateTrigger"
      @cancel="createModalOpen = false"
    >
      <a-form layout="vertical">
        <a-form-item :label="t('Trigger 名称')" required>
          <a-input
            v-model:value="createForm.trigger_name"
            :placeholder="t('请输入 Trigger 名称')"
            :maxlength="100"
          />
        </a-form-item>

        <a-form-item :label="t('回调 URL')" required>
          <a-input
            v-model:value="createForm.url"
            :placeholder="t('请输入回调 URL')"
          />
        </a-form-item>

        <a-form-item :label="t('Conditions')" required>
          <a-select
            v-model:value="createForm.status_value"
            :options="statusOptions"
            :placeholder="`${t('请选择')}${t('状态')}`"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </aside>
</template>

<style scoped>
.annotation-agent-dock {
  width: 84px;
  height: 100%;
  flex-shrink: 0;
}

.annotation-agent-dock-inner {
  height: 100%;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
  background: #fff;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
  padding: 10px 8px;
  display: flex;
  flex-direction: column;
}

.agent-add-btn {
  width: 56px;
  height: 56px;
  margin: 10px auto 0;
  border-radius: 16px;
  border: 1px dashed #93c5fd;
  background: #eff6ff;
  color: #2563eb;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.agent-add-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  border-color: #60a5fa;
  box-shadow: 0 8px 18px rgba(37, 99, 235, 0.22);
}

.agent-add-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.agent-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-right: 2px;
}

.agent-item-wrap {
  position: relative;
  display: flex;
  justify-content: center;
  padding: 2px;
}

.agent-item-btn {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  background: #fff;
  color: #334155;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.agent-item-btn:hover {
  transform: translateY(-1px) scale(1.02);
  border-color: #93c5fd;
  box-shadow: 0 10px 18px rgba(59, 130, 246, 0.18);
  color: #2563eb;
}

.agent-info-card {
  width: 280px;
}

.agent-info-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
}

.agent-info-row:last-child {
  margin-bottom: 0;
}

.agent-info-id-row {
  align-items: center;
}

.agent-info-label {
  width: 44px;
  flex-shrink: 0;
  font-size: 12px;
  color: #64748b;
  line-height: 1.6;
}

.agent-info-value {
  flex: 1;
  min-width: 0;
  font-size: 12px;
  color: #0f172a;
  line-height: 1.6;
  word-break: break-all;
  user-select: text;
  cursor: copy;
}

.agent-copy-btn {
  width: 20px;
  height: 20px;
  border-radius: 6px;
  border: 1px solid #dbeafe;
  background: #f8fbff;
  color: #2563eb;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.agent-copy-btn:hover {
  border-color: #93c5fd;
  background: #eff6ff;
}

.agent-delete-btn {
  width: 18px;
  height: 18px;
  border-radius: 999px;
  border: 1px solid #fff;
  background: #ef4444;
  color: #fff;
  font-size: 10px;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  right: -1px;
  top: -1px;
  opacity: 0;
  pointer-events: none;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.35);
  transition:
    transform 0.2s ease,
    opacity 0.2s ease,
    box-shadow 0.2s ease;
  z-index: 2;
}

.agent-delete-btn.visible {
  opacity: 1;
  pointer-events: auto;
}

.agent-delete-btn:hover:not(:disabled) {
  transform: scale(1.06);
  box-shadow: 0 4px 10px rgba(239, 68, 68, 0.45);
}

.agent-delete-btn:disabled {
  cursor: wait;
  opacity: 0.6;
}

@media (max-width: 1024px) {
  .annotation-agent-dock {
    width: 76px;
  }

  .annotation-agent-dock-inner {
    padding: 10px 8px;
  }

  .agent-add-btn {
    width: 50px;
    height: 50px;
  }

  .agent-item-btn {
    width: 46px;
    height: 46px;
  }
}

:deep(.agent-info-popover .ant-popover-inner) {
  border-radius: 12px;
}

:deep(.agent-info-popover .ant-popover-inner-content) {
  padding: 10px 12px;
}
</style>
