import type { Dayjs } from 'dayjs'

export interface BankChunkItem {
  sys_sample_id: string
  kb_id?: string | null
  sys_group?: string | null
  sys_template?: string | null
  sys_priority?: number | null
  sys_status?: string | null
  sys_executor?: string | null
  sys_overview?: string | null
  sys_remarks?: string | null
  sys_create_time?: string | null
  sys_update_time?: string | null

  // 兼容后端可能返回的字段
  query?: string | null
  answer?: string | null

  // 其他业务字段（由模板决定）
  [key: string]: any
}

export type AnnotationStatus =
  | 'pending'
  | 'annotated'
  | 'approved'
  | 'rejected'
  | 'kb_ingested'
  | 'kb_failed'

export type AnnotationDataType = 'e2e' | 'agent' | 'llm' | 'tool' | 'custom'

export interface AnnotationItem {
  data_id: string
  priority?: number | null
  status: AnnotationStatus
  data_type?: AnnotationDataType | string | null
  caller?: string | null
  callee?: string | null
  question?: string | Record<string, unknown> | null
  answer?: string | Record<string, unknown> | null
  source_group_id?: string | null
  source_trace_id?: string | null
  created_at?: string | null
  annotation?: Record<string, unknown> | null
  reject_reason?: string | null
}

export interface AnnotationStats {
  pending: number
  annotated: number
  approved: number
  rejected: number
  kb_ingested: number
  kb_failed: number
}

export interface AnnotationFilters {
  timeRange: [Dayjs, Dayjs] | undefined
  dataType: string
  status: string
  priority: string
  caller: string
  callee: string
  groupId: string
  traceId: string
  search: string
}
