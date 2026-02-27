<script setup lang="ts">
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import {
  ReloadOutlined,
  SearchOutlined,
} from '@ant-design/icons-vue'
import type { TableColumnsType } from 'ant-design-vue'
import { message } from 'ant-design-vue'
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useWindowSize } from '@vueuse/core'
import { useRoute } from 'vue-router'
import type { AnnotationFilters, AnnotationStats, BankChunkItem } from '@/views/annotation/types'
import AgentSidebar from '@/views/annotation/components/AgentSidebar.vue'
import QaAnnotationDrawer from '@/views/annotation/components/QaAnnotationDrawer.vue'
import DefaultAnnotationDrawer from '@/views/annotation/components/DefaultAnnotationDrawer.vue'
import { useI18n } from '@/locales'

const { t } = useI18n()

dayjs.extend(utc)

const route = useRoute()

const bankName = computed(() => {
  const value = route.query.bank_name
  return typeof value === 'string' ? value : ''
})

// 左侧筛选条件面板：按需恢复（设置为 true）
const showSidebar = ref(false)

const sidebarWidth = ref(320)
const sidebarMinWidth = 200
const sidebarMaxWidth = 400
const sidebarResizing = ref(false)
let sidebarStartX = 0
let sidebarStartWidth = 0

const columnWidths = reactive({
  sampleId: 160,
  group: 140,
  template: 140,
  priority: 110,
  status: 110,
  executor: 120,
  overview: 260,
  remarks: 220,
  createTime: 160,
  updateTime: 160,
  action: 110,
})

const resizingColumnKey = ref<string | null>(null)
let columnStartX = 0
let columnStartWidth = 0

const { width: windowWidth } = useWindowSize()
const drawerWidth = computed(() => {
  if (windowWidth.value < 768)
    return '100%'
  if (windowWidth.value < 1200)
    return '60%'
  return '50%'
})

const statusOptions = computed(() => ([
  { label: t('All Status'), value: '' },
  { label: t('Pending'), value: 'pending' },
  { label: t('Annotated'), value: 'annotated' },
  { label: t('Approved'), value: 'approved' },
  { label: t('Rejected'), value: 'rejected' },
  { label: t('KB Ingested'), value: 'kb_ingested' },
  { label: t('KB Failed'), value: 'kb_failed' },
]))

const dataTypeOptions = computed(() => ([
  { label: t('All Types'), value: '' },
  { label: t('End-to-End'), value: 'e2e' },
  { label: t('Agent'), value: 'agent' },
  { label: t('LLM'), value: 'llm' },
  { label: t('Tool'), value: 'tool' },
  { label: t('Custom'), value: 'custom' },
]))

const priorityOptions = computed(() => ([
  { label: t('All Priorities'), value: '' },
  { label: t('P0-End-to-End'), value: '0' },
  { label: t('P1-Agent'), value: '1' },
  { label: t('P2-LLM'), value: '2' },
  { label: t('P3-Tool'), value: '3' },
  { label: t('P4-Other'), value: '4' },
]))

const filters = reactive<AnnotationFilters>({
  timeRange: undefined,
  dataType: '',
  status: '',
  priority: '',
  caller: '',
  callee: '',
  groupId: '',
  traceId: '',
  search: '',
})

const statsLoading = ref(false)
const stats = reactive<AnnotationStats>({
  pending: 0,
  annotated: 0,
  approved: 0,
  rejected: 0,
  kb_ingested: 0,
  kb_failed: 0,
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
})

const dataList = ref<BankChunkItem[]>([])
const loading = ref(false)

const drawerOpen = ref(false)
const selectedIndex = ref(-1)
const submitting = ref(false)

const schemaDraft = ref<Record<string, any>>({})

const selectedRow = computed(() => {
  if (selectedIndex.value < 0)
    return null
  return dataList.value[selectedIndex.value] || null
})

const activeTemplate = computed(() => {
  const raw = String(selectedRow.value?.sys_template ?? 'default').toLowerCase()
  return raw === 'qa' ? 'qa' : 'default'
})

const isSatisfiedModel = computed({
  get: () => String(schemaDraft.value?.is_satisfied ?? '1'),
  set: value => (schemaDraft.value.is_satisfied = value),
})

const reasonModel = computed({
  get: () => String(schemaDraft.value?.reason ?? ''),
  set: value => (schemaDraft.value.reason = value),
})

const selectedSampleId = computed(() => selectedRow.value?.sys_sample_id || null)

const drawerTitle = computed(() => {
  if (!selectedRow.value)
    return t('标注')
  return t('标注 ({cur}/{total})', {
    cur: selectedIndex.value + 1,
    total: dataList.value.length,
  })
})

function formatCellValue(value: unknown) {
  if (value === null || value === undefined || value === '')
    return '--'
  return String(value)
}

const totalPages = computed(() => Math.max(1, Math.ceil(pagination.total / pagination.pageSize)))
const paginationInfo = computed(
  () => t('Page {page}/{total}, {count} items', {
    page: pagination.page,
    total: totalPages.value,
    count: pagination.total,
  }),
)

const progressTotal = computed(
  () => stats.pending + stats.annotated + stats.approved + stats.rejected + stats.kb_ingested + stats.kb_failed,
)

const progressSegments = computed(() => {
  const total = progressTotal.value
  const calc = (value: number) => (total > 0 ? (value / total) * 100 : 0)
  return {
    pending: calc(stats.pending),
    annotated: calc(stats.annotated),
    approved: calc(stats.approved),
    rejected: calc(stats.rejected),
    kb_ingested: calc(stats.kb_ingested),
    kb_failed: calc(stats.kb_failed),
  }
})

function setDefaultTimeRange() {
  const now = dayjs().utcOffset(8 * 60)
  const roundedNow = now.second(0).millisecond(0).add(1, 'minute')
  const threeDaysAgo = roundedNow.subtract(3, 'day')
  filters.timeRange = [threeDaysAgo, roundedNow]
}

function resetFilters() {
  filters.dataType = ''
  filters.status = ''
  filters.priority = ''
  filters.caller = ''
  filters.callee = ''
  filters.groupId = ''
  filters.traceId = ''
  filters.search = ''
  setDefaultTimeRange()
  applyFilters()
}

function loadStats() {
  stats.pending = pagination.total
  stats.annotated = 0
  stats.approved = 0
  stats.rejected = 0
  stats.kb_ingested = 0
  stats.kb_failed = 0
}

function applyFilters() {
  pagination.page = 1
  loadData(pagination.page)
}

const columns = computed<TableColumnsType>(() => [
  {
    title: t('样本ID'),
    dataIndex: 'sys_sample_id',
    key: 'sampleId',
    width: columnWidths.sampleId,
    ellipsis: true,
  },
  {
    title: t('分组'),
    dataIndex: 'sys_group',
    key: 'group',
    width: columnWidths.group,
    ellipsis: true,
  },
  {
    title: t('模板'),
    dataIndex: 'sys_template',
    key: 'template',
    width: columnWidths.template,
    ellipsis: true,
  },
  {
    title: t('优先级'),
    dataIndex: 'sys_priority',
    key: 'priority',
    width: columnWidths.priority,
    align: 'center',
  },
  {
    title: t('状态'),
    dataIndex: 'sys_status',
    key: 'status',
    width: columnWidths.status,
    align: 'center',
  },
  {
    title: t('执行人'),
    dataIndex: 'sys_executor',
    key: 'executor',
    width: columnWidths.executor,
    ellipsis: true,
  },
  {
    title: t('概览'),
    dataIndex: 'sys_overview',
    key: 'overview',
    width: columnWidths.overview,
    ellipsis: true,
  },
  {
    title: t('备注'),
    dataIndex: 'sys_remarks',
    key: 'remarks',
    width: columnWidths.remarks,
    ellipsis: true,
  },
  {
    title: t('创建时间'),
    dataIndex: 'sys_create_time',
    key: 'createTime',
    width: columnWidths.createTime,
  },
  {
    title: t('更新时间'),
    dataIndex: 'sys_update_time',
    key: 'updateTime',
    width: columnWidths.updateTime,
  },
  {
    title: t('操作'),
    key: 'action',
    width: columnWidths.action,
    align: 'center',
    fixed: 'right',
  },
])

function getPriorityStyle(priority?: number | null) {
  const value = priority ?? 0
  if (value === 0)
    return { backgroundColor: '#EF4444', color: '#FFFFFF' }
  if (value === 1)
    return { backgroundColor: '#FEF3C7', color: '#D97706' }
  if (value === 2)
    return { backgroundColor: '#DBEAFE', color: '#2563EB' }
  if (value === 3)
    return { backgroundColor: '#E0E7FF', color: '#4F46E5' }
  return { backgroundColor: '#F3F4F6', color: '#6B7280' }
}

function getStatusStyle(status?: string | null) {
  const map: Record<string, { backgroundColor: string, color: string }> = {
    待分配: { backgroundColor: '#FEF3C7', color: '#D97706' },
    待标注: { backgroundColor: '#DBEAFE', color: '#2563EB' },
    待审核: { backgroundColor: '#E0E7FF', color: '#4F46E5' },
    待发布: { backgroundColor: '#C7D2FE', color: '#4338CA' },
    已标注: { backgroundColor: '#D1FAE5', color: '#059669' },
  }
  return map[status || ''] || { backgroundColor: '#F3F4F6', color: '#6B7280' }
}

function getRowSchema(row: BankChunkItem | null | undefined): Record<string, any> {
  const raw = (row as any)?.schema
  if (!raw || typeof raw !== 'object' || Array.isArray(raw))
    return {}
  return raw as Record<string, any>
}

function clonePlainObject<T extends Record<string, any>>(obj: T): T {
  try {
    return structuredClone(obj)
  }
  catch {
    return JSON.parse(JSON.stringify(obj)) as T
  }
}

function resetDraftFromRow(row: BankChunkItem | null) {
  schemaDraft.value = clonePlainObject(getRowSchema(row))
}

function getDisplayQuery(row: BankChunkItem) {
  const schema = getRowSchema(row)
  return String(schema.query ?? row.query ?? row.sys_overview ?? '')
}

function getDisplayAnswer(row: BankChunkItem) {
  const schema = getRowSchema(row)
  return String(schema.answer ?? row.answer ?? '')
}

const legacyToSysFieldMap: Record<string, string> = {
  _sample_id: 'sys_sample_id',
  _status: 'sys_status',
  _group: 'sys_group',
  _priority: 'sys_priority',
  _executor: 'sys_executor',
  _overview: 'sys_overview',
  _remarks: 'sys_remarks',
}

function normalizeSubmissionSchema(schema: Record<string, any>) {
  const next = { ...schema }

  for (const [legacyKey, sysKey] of Object.entries(legacyToSysFieldMap)) {
    if (next[legacyKey] !== undefined && next[sysKey] === undefined)
      next[sysKey] = next[legacyKey]
    delete next[legacyKey]
  }

  delete next.sys_sample_id
  delete next.sys_status
  return next
}

async function requestJson<T>(url: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('token')
  const response = await fetch(url, {
    credentials: 'include',
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options?.headers || {}),
    },
  })

  const json = await response.json().catch(() => null)
  if (!response.ok) {
    const errMsg = json?.message || json?.msg || `HTTP ${response.status}`
    throw new Error(errMsg)
  }
  return json as T
}

function unwrapResponseData(value: any) {
  return value?.data ?? value
}

async function loadData(page = pagination.page) {
  if (!bankName.value) {
    dataList.value = []
    pagination.total = 0
    pagination.page = 1
    loadStats()
    return
  }

  loading.value = true
  try {
    const payload = {
      _page_size: pagination.pageSize,
      _page_number: page,
    }
    const resp = await requestJson<any>(`/kb/${encodeURIComponent(bankName.value)}/search`, {
      method: 'POST',
      body: JSON.stringify(payload),
    })

    const data = unwrapResponseData(resp)
    const items = data?.items || data?.list || data?.records || data?.results || data?.data || []
    dataList.value = Array.isArray(items) ? (items as BankChunkItem[]) : []

    const total = data?.total ?? data?._total ?? data?.count ?? data?.total_count
    pagination.total = typeof total === 'number' ? total : (Number(total) || dataList.value.length)
    pagination.page = page
    loadStats()
  }
  catch (err: any) {
    message.error(err?.message || t('请求失败'))
  }
  finally {
    loading.value = false
  }
}

function openDrawer(record: BankChunkItem) {
  const idx = dataList.value.findIndex(item => item.sys_sample_id === record.sys_sample_id)
  selectedIndex.value = idx >= 0 ? idx : 0
  resetDraftFromRow(record)
  drawerOpen.value = true
}

function closeDrawer() {
  drawerOpen.value = false
  selectedIndex.value = -1
  schemaDraft.value = {}
}

function gotoPrev() {
  if (selectedIndex.value <= 0) {
    message.info(t('已经是本页第一条'))
    return
  }
  selectedIndex.value -= 1
  resetDraftFromRow(selectedRow.value)
}

function gotoNext() {
  if (selectedIndex.value >= dataList.value.length - 1) {
    message.info(t('已经是本页最后一条'))
    return
  }
  selectedIndex.value += 1
  resetDraftFromRow(selectedRow.value)
}

async function submit() {
  const row = selectedRow.value
  if (!row)
    return
  if (!bankName.value) {
    message.error(t('缺少 bank_name'))
    return
  }
  if (activeTemplate.value === 'qa') {
    const isSatisfied = String(schemaDraft.value?.is_satisfied ?? '1')
    const reason = String(schemaDraft.value?.reason ?? '')

    if (isSatisfied === '3' && !reason.trim()) {
      message.warning(t('请填写不满意原因'))
      return
    }
    if ((reason || '').length > 500) {
      message.warning(t('原因最多 500 字'))
      return
    }
  }

  submitting.value = true
  try {
    const safeSchema = normalizeSubmissionSchema(schemaDraft.value || {})

    if (activeTemplate.value === 'qa') {
      safeSchema.is_satisfied = safeSchema.is_satisfied ?? '1'
      safeSchema.reason = safeSchema.reason ?? ''
    }
    const payload = {
      sys_sample_id: row.sys_sample_id,
      sys_status: '已标注',
      ...safeSchema,
    }
    await requestJson<any>(`/kb/${encodeURIComponent(bankName.value)}/deposit`, {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    message.success(t('提交成功'))
    closeDrawer()
    await loadData(pagination.page)
  }
  catch (err: any) {
    message.error(err?.message || t('提交失败'))
  }
  finally {
    submitting.value = false
  }
}

function startSidebarResize(event: MouseEvent) {
  sidebarResizing.value = true
  sidebarStartX = event.clientX
  sidebarStartWidth = sidebarWidth.value
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
  window.addEventListener('mousemove', onSidebarResizeMove)
  window.addEventListener('mouseup', stopSidebarResize)
}

function onSidebarResizeMove(event: MouseEvent) {
  if (!sidebarResizing.value)
    return
  const diff = event.clientX - sidebarStartX
  const next = Math.min(sidebarMaxWidth, Math.max(sidebarMinWidth, sidebarStartWidth + diff))
  sidebarWidth.value = next
}

function stopSidebarResize() {
  if (!sidebarResizing.value)
    return
  sidebarResizing.value = false
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
  window.removeEventListener('mousemove', onSidebarResizeMove)
  window.removeEventListener('mouseup', stopSidebarResize)
}

function startColumnResize(key: string, event: MouseEvent) {
  event.stopPropagation()
  resizingColumnKey.value = key
  columnStartX = event.clientX
  columnStartWidth = columnWidths[key as keyof typeof columnWidths]
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
  window.addEventListener('mousemove', onColumnResizeMove)
  window.addEventListener('mouseup', stopColumnResize)
}

function onColumnResizeMove(event: MouseEvent) {
  if (!resizingColumnKey.value)
    return
  const diff = event.clientX - columnStartX
  const next = Math.max(60, columnStartWidth + diff)
  columnWidths[resizingColumnKey.value as keyof typeof columnWidths] = next
}

function stopColumnResize() {
  if (!resizingColumnKey.value)
    return
  resizingColumnKey.value = null
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
  window.removeEventListener('mousemove', onColumnResizeMove)
  window.removeEventListener('mouseup', stopColumnResize)
}

function rowClassName(record: BankChunkItem) {
  return selectedSampleId.value === record.sys_sample_id ? 'bg-blue-50' : ''
}

function handleTableRow(_record: BankChunkItem) {
  return {}
}

onMounted(() => {
  setDefaultTimeRange()
  loadData()
})

onBeforeUnmount(() => {
  stopSidebarResize()
  stopColumnResize()
})

watch(
  bankName,
  () => {
    closeDrawer()
    pagination.page = 1
    loadData(1)
  },
)
</script>

<template>
  <div class="annotation-page flex h-full flex-col gap-4">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="m-0 text-2xl font-semibold text-gray-800">
          {{ t('QA Annotation Platform') }}
        </h1>
        <p class="m-0 text-sm text-gray-400">
          {{ t('Manage QA annotation tasks with filtering, review, and assets base ingestion.') }}
        </p>
      </div>
    </div>

    <div class="flex min-h-0 flex-1 gap-4">
      <agent-sidebar :bank-name="bankName" />

      <!-- 左侧筛选条件暂时移除：将 showSidebar 改为 true 可恢复 -->
      <template v-if="showSidebar">
        <div
          class="relative flex-shrink-0"
          :style="{ width: `${sidebarWidth}px` }"
        >
          <a-card
            class="h-full overflow-hidden"
            :body-style="{ height: '100%', padding: '16px', display: 'flex', flexDirection: 'column' }"
          >
            <div class="flex flex-1 flex-col gap-4 overflow-y-auto pr-1">
              <a-collapse default-active-key="filter" expand-icon-position="end" ghost>
                <a-collapse-panel key="filter">
                  <template #header>
                    <div class="flex items-center gap-2 text-sm font-medium text-gray-700">
                      <span>🔍</span>
                      <span>{{ t('Filter Conditions') }}</span>
                    </div>
                  </template>
                  <a-form layout="vertical" class="filter-form">
                    <a-form-item :label="t('Time Range')">
                      <a-range-picker
                        v-model:value="filters.timeRange"
                        show-time
                        format="YYYY-MM-DD HH:mm"
                        class="w-full"
                      />
                    </a-form-item>
                    <a-form-item :label="t('Type & Status')">
                      <div class="flex flex-col gap-2">
                        <a-select
                          v-model:value="filters.dataType"
                          :options="dataTypeOptions"
                          @change="applyFilters"
                        />
                        <a-select
                          v-model:value="filters.status"
                          :options="statusOptions"
                          @change="applyFilters"
                        />
                        <a-select
                          v-model:value="filters.priority"
                          :options="priorityOptions"
                          @change="applyFilters"
                        />
                      </div>
                    </a-form-item>
                    <a-form-item :label="t('Caller')">
                      <a-input
                        v-model:value="filters.caller"
                        :placeholder="t('Enter Caller...')"
                      >
                        <template #suffix>
                          <search-outlined
                            class="cursor-pointer text-gray-400 transition hover:text-blue-500"
                            @click="applyFilters"
                          />
                        </template>
                      </a-input>
                    </a-form-item>
                    <a-form-item :label="t('Callee')">
                      <a-input
                        v-model:value="filters.callee"
                        :placeholder="t('Enter Callee...')"
                      >
                        <template #suffix>
                          <search-outlined
                            class="cursor-pointer text-gray-400 transition hover:text-blue-500"
                            @click="applyFilters"
                          />
                        </template>
                      </a-input>
                    </a-form-item>
                    <a-form-item :label="t('Group ID')">
                      <a-input
                        v-model:value="filters.groupId"
                        :placeholder="t('Enter Group ID...')"
                      >
                        <template #suffix>
                          <search-outlined
                            class="cursor-pointer text-gray-400 transition hover:text-blue-500"
                            @click="applyFilters"
                          />
                        </template>
                      </a-input>
                    </a-form-item>
                    <a-form-item :label="t('Trace ID')">
                      <a-input
                        v-model:value="filters.traceId"
                        :placeholder="t('Enter Trace ID...')"
                      >
                        <template #suffix>
                          <search-outlined
                            class="cursor-pointer text-gray-400 transition hover:text-blue-500"
                            @click="applyFilters"
                          />
                        </template>
                      </a-input>
                    </a-form-item>
                    <a-form-item :label="t('Search')">
                      <a-input
                        v-model:value="filters.search"
                        :placeholder="t('Search Question content...')"
                      >
                        <template #suffix>
                          <search-outlined
                            class="cursor-pointer text-gray-400 transition hover:text-blue-500"
                            @click="applyFilters"
                          />
                        </template>
                      </a-input>
                    </a-form-item>
                    <div class="flex flex-col gap-2">
                      <a-button type="primary" block @click="applyFilters">
                        {{ t('Search') }}
                      </a-button>
                      <a-button block @click="resetFilters">
                        {{ t('Reset') }}
                      </a-button>
                    </div>
                  </a-form>
                </a-collapse-panel>
              </a-collapse>

              <a-collapse default-active-key="progress" expand-icon-position="end" ghost>
                <a-collapse-panel key="progress">
                  <template #header>
                    <div class="flex items-center gap-2 text-sm font-medium text-gray-700">
                      <span>📊</span>
                      <span>{{ t('Annotation Progress') }}</span>
                    </div>
                  </template>
                  <a-spin :spinning="statsLoading">
                    <div class="grid grid-cols-2 gap-3">
                      <div class="rounded-lg bg-amber-50 p-3 text-center">
                        <div class="text-lg font-semibold text-amber-600">
                          {{ stats.pending }}
                        </div>
                        <div class="text-xs text-gray-500">
                          {{ t('Pending') }}
                        </div>
                      </div>
                      <div class="rounded-lg bg-emerald-50 p-3 text-center">
                        <div class="text-lg font-semibold text-emerald-600">
                          {{ stats.annotated }}
                        </div>
                        <div class="text-xs text-gray-500">
                          {{ t('Annotated') }}
                        </div>
                      </div>
                      <div class="rounded-lg bg-emerald-500/10 p-3 text-center">
                        <div class="text-lg font-semibold text-emerald-600">
                          {{ stats.approved }}
                        </div>
                        <div class="text-xs text-gray-500">
                          {{ t('Approved') }}
                        </div>
                      </div>
                      <div class="rounded-lg bg-red-50 p-3 text-center">
                        <div class="text-lg font-semibold text-red-500">
                          {{ stats.rejected }}
                        </div>
                        <div class="text-xs text-gray-500">
                          {{ t('Rejected') }}
                        </div>
                      </div>
                      <div class="rounded-lg bg-indigo-50 p-3 text-center">
                        <div class="text-lg font-semibold text-indigo-600">
                          {{ stats.kb_ingested }}
                        </div>
                        <div class="text-xs text-gray-500">
                          {{ t('KB Ingested') }}
                        </div>
                      </div>
                      <div class="rounded-lg bg-rose-50 p-3 text-center">
                        <div class="text-lg font-semibold text-rose-500">
                          {{ stats.kb_failed }}
                        </div>
                        <div class="text-xs text-gray-500">
                          {{ t('KB Failed') }}
                        </div>
                      </div>
                    </div>

                    <div class="mt-4 space-y-3">
                      <div class="text-xs font-medium text-gray-600">
                        {{ t('Annotation Progress') }}
                      </div>
                      <div class="h-2 overflow-hidden rounded-full bg-gray-100">
                        <div class="flex h-full">
                          <div
                            class="h-full bg-emerald-500"
                            :style="{ width: `${progressSegments.approved}%` }"
                          />
                          <div
                            class="h-full bg-emerald-300"
                            :style="{ width: `${progressSegments.annotated}%` }"
                          />
                          <div
                            class="h-full bg-red-400"
                            :style="{ width: `${progressSegments.rejected}%` }"
                          />
                          <div
                            class="h-full bg-amber-400"
                            :style="{ width: `${progressSegments.pending}%` }"
                          />
                          <div
                            class="h-full bg-indigo-400"
                            :style="{ width: `${progressSegments.kb_ingested}%` }"
                          />
                          <div
                            class="h-full bg-rose-400"
                            :style="{ width: `${progressSegments.kb_failed}%` }"
                          />
                        </div>
                      </div>
                      <div class="flex flex-wrap gap-3 text-xs text-gray-500">
                        <span class="flex items-center gap-1">
                          <span class="h-2 w-2 rounded-full bg-amber-400" />
                          {{ t('Pending') }}
                        </span>
                        <span class="flex items-center gap-1">
                          <span class="h-2 w-2 rounded-full bg-emerald-300" />
                          {{ t('Annotated') }}
                        </span>
                        <span class="flex items-center gap-1">
                          <span class="h-2 w-2 rounded-full bg-emerald-500" />
                          {{ t('Approved') }}
                        </span>
                        <span class="flex items-center gap-1">
                          <span class="h-2 w-2 rounded-full bg-red-400" />
                          {{ t('Rejected') }}
                        </span>
                        <span class="flex items-center gap-1">
                          <span class="h-2 w-2 rounded-full bg-indigo-400" />
                          {{ t('KB Ingested') }}
                        </span>
                        <span class="flex items-center gap-1">
                          <span class="h-2 w-2 rounded-full bg-rose-400" />
                          {{ t('KB Failed') }}
                        </span>
                      </div>
                    </div>
                  </a-spin>
                </a-collapse-panel>
              </a-collapse>
            </div>
          </a-card>

          <div
            class="annotation-sidebar-resizer"
            :class="{ active: sidebarResizing }"
            @mousedown="startSidebarResize"
          />
        </div>
      </template>

      <div class="flex min-w-0 flex-1 flex-col">
        <a-card
          class="h-full"
          :body-style="{ height: '100%', padding: '16px', display: 'flex', flexDirection: 'column' }"
        >
          <div class="mb-4 flex items-center justify-between">
            <div>
              <h2 class="m-0 text-lg font-semibold text-gray-800">
                {{ t('Data List') }}
              </h2>
              <p class="m-0 text-xs text-gray-400">
                {{ t('{count} items', { count: pagination.total }) }}
              </p>
            </div>
            <div class="flex items-center gap-2">
              <a-button @click="applyFilters">
                <template #icon>
                  <reload-outlined />
                </template>
                {{ t('Refresh') }}
              </a-button>
            </div>
          </div>

          <a-table
            :columns="columns"
            :data-source="dataList"
            :loading="loading"
            :pagination="false"
            :row-key="record => (record as BankChunkItem).sys_sample_id"
            :row-class-name="rowClassName"
            :custom-row="handleTableRow"
            size="middle"
            table-layout="fixed"
            :scroll="{ x: 1600 }"
          >
            <template #headerCell="{ column }">
              <div class="flex w-full items-center justify-between gap-2">
                <span class="text-xs font-semibold text-gray-600">
                  {{ column.title }}
                </span>
                <span
                  class="annotation-column-resizer"
                  @mousedown="startColumnResize(String(column.key), $event)"
                />
              </div>
            </template>

            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'priority'">
                <template v-if="typeof (record as BankChunkItem).sys_priority === 'number'">
                  <a-tag :style="getPriorityStyle((record as BankChunkItem).sys_priority)" bordered>
                    P{{ (record as BankChunkItem).sys_priority }}
                  </a-tag>
                </template>
                <span v-else class="text-xs text-gray-600">--</span>
              </template>
              <template v-else-if="column.key === 'status'">
                <template v-if="(record as BankChunkItem).sys_status">
                  <a-tag :style="getStatusStyle((record as BankChunkItem).sys_status)" bordered>
                    {{ (record as BankChunkItem).sys_status }}
                  </a-tag>
                </template>
                <span v-else class="text-xs text-gray-600">--</span>
              </template>
              <template v-else-if="column.key === 'overview'">
                <a-tooltip :title="(record as BankChunkItem).sys_overview || '--'">
                  <div class="truncate text-xs text-gray-600">
                    {{ (record as BankChunkItem).sys_overview || '--' }}
                  </div>
                </a-tooltip>
              </template>
              <template v-else-if="column.key === 'remarks'">
                <a-tooltip :title="(record as BankChunkItem).sys_remarks || '--'">
                  <div class="truncate text-xs text-gray-600">
                    {{ (record as BankChunkItem).sys_remarks || '--' }}
                  </div>
                </a-tooltip>
              </template>
              <template v-else-if="column.key === 'createTime'">
                <span class="text-xs text-gray-500">
                  {{ (record as BankChunkItem).sys_create_time || '--' }}
                </span>
              </template>
              <template v-else-if="column.key === 'updateTime'">
                <span class="text-xs text-gray-500">
                  {{ (record as BankChunkItem).sys_update_time || '--' }}
                </span>
              </template>
              <template v-else-if="column.key === 'action'">
                <a-button type="link" size="small" class="!px-0" @click.stop="openDrawer(record as BankChunkItem)">
                  {{ t('标注') }}
                </a-button>
              </template>
              <template v-else>
                <span class="text-xs text-gray-600">
                  {{ formatCellValue((record as any)[(column.dataIndex as any) as string]) }}
                </span>
              </template>
            </template>

            <template #emptyText>
              <div class="py-8">
                <a-empty>
                  <template #description>
                    <div class="text-sm text-gray-500">
                      <div>{{ t('No data available. Please inject data via API.') }}</div>
                      <div class="mt-2 text-xs text-gray-400">
                        {{ t('POST /api/v1/deposit') }}
                      </div>
                    </div>
                  </template>
                </a-empty>
              </div>
            </template>
          </a-table>

          <div class="mt-4 flex items-center justify-between">
            <span class="text-xs text-gray-500">
              {{ paginationInfo }}
            </span>
            <a-pagination
              :current="pagination.page"
              :page-size="pagination.pageSize"
              :total="pagination.total"
              :show-size-changer="false"
              @change="loadData"
            />
          </div>
        </a-card>
      </div>
    </div>

    <qa-annotation-drawer
      v-if="selectedRow && activeTemplate === 'qa'"
      v-model:open="drawerOpen"
      v-model:is-satisfied="isSatisfiedModel"
      v-model:reason="reasonModel"
      :title="drawerTitle"
      :width="drawerWidth"
      :submitting="submitting"
      :query="String(schemaDraft.query ?? getDisplayQuery(selectedRow))"
      :answer="String(schemaDraft.answer ?? getDisplayAnswer(selectedRow))"
      @prev="gotoPrev"
      @next="gotoNext"
      @submit="submit"
      @update:open="(val) => { if (!val) closeDrawer() }"
    />

    <default-annotation-drawer
      v-else-if="selectedRow"
      v-model:open="drawerOpen"
      v-model:schema="schemaDraft"
      :title="drawerTitle"
      :width="drawerWidth"
      :submitting="submitting"
      @prev="gotoPrev"
      @next="gotoNext"
      @submit="submit"
      @update:open="(val) => { if (!val) closeDrawer() }"
    />
  </div>
</template>

<style scoped>
.annotation-sidebar-resizer {
  position: absolute;
  right: -4px;
  top: 0;
  bottom: 0;
  width: 6px;
  cursor: col-resize;
  display: flex;
  align-items: center;
  justify-content: center;
}

.annotation-sidebar-resizer::after {
  content: '';
  width: 2px;
  height: 40px;
  background: #cbd5f5;
  border-radius: 999px;
  transition: background 0.2s ease;
}

.annotation-sidebar-resizer:hover::after,
.annotation-sidebar-resizer.active::after {
  background: #3b82f6;
}

.annotation-column-resizer {
  width: 6px;
  height: 100%;
  cursor: col-resize;
  position: relative;
}

.annotation-column-resizer::after {
  content: '';
  position: absolute;
  top: 50%;
  right: 0;
  width: 2px;
  height: 16px;
  background: #d1d5db;
  transform: translateY(-50%);
  border-radius: 999px;
}

/* Force vertical center for annotation result table cells */
.annotation-result-table :deep(.ant-table-cell) {
  vertical-align: middle !important;
}

.annotation-result-table :deep(.ant-table-cell pre) {
  margin: 0;
  display: inline-block;
  vertical-align: middle;
}

/* Reduce spacing between filter form items */
.filter-form :deep(.ant-form-item) {
  margin-bottom: 12px;
}

.filter-form :deep(.ant-form-item:last-of-type) {
  margin-bottom: 16px;
}
</style>
