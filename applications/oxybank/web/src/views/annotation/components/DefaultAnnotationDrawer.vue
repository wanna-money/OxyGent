<script setup lang="ts">
import { EditOutlined } from '@ant-design/icons-vue'
import { computed, ref, watch } from 'vue'
import AnnotationDrawerTemplate from './AnnotationDrawerTemplate.vue'
import { useI18n } from '@/locales'

const props = withDefaults(defineProps<{
  open: boolean
  title: string
  width?: string | number
  submitting?: boolean
  schema: Record<string, any>
}>(), {
  width: 560,
  submitting: false,
})

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'update:schema', value: Record<string, any>): void
  (e: 'prev'): void
  (e: 'next'): void
  (e: 'submit'): void
}>()

const { t } = useI18n()

const editingKeys = ref(new Set<string>())

watch(
  () => props.open,
  (v) => {
    if (!v)
      editingKeys.value = new Set()
  },
)

const entries = computed(() => {
  return Object.entries(props.schema || {})
    .filter(([k]) => k)
    .sort(([a], [b]) => a.localeCompare(b))
})

function updateValue(key: string, value: any) {
  emit('update:schema', {
    ...(props.schema || {}),
    [key]: value,
  })
}

function toggleEdit(key: string) {
  const next = new Set(editingKeys.value)
  if (next.has(key))
    next.delete(key)
  else
    next.add(key)
  editingKeys.value = next
}

function isEditable(key: string) {
  return editingKeys.value.has(key)
}
</script>

<template>
  <annotation-drawer-template
    :open="open"
    :title="title"
    :width="width"
    :submitting="submitting"
    :label-width="140"
    :prev-text="t('上一个')"
    :next-text="t('下一个')"
    :submit-text="t('提交')"
    @update:open="emit('update:open', $event)"
    @prev="emit('prev')"
    @next="emit('next')"
    @submit="emit('submit')"
  >
    <div v-if="entries.length === 0" class="py-8 text-center text-sm text-gray-400">
      {{ t('No data available') }}
    </div>

    <div v-else class="px-2">
      <a-form-item
        v-for="([key, value]) in entries"
        :key="key"
        :label="key"
        class="mb-3"
      >
        <div class="flex items-center gap-2">
          <a-input
            class="flex-1"
            :value="value === null || value === undefined ? '' : String(value)"
            :disabled="!isEditable(key)"
            @update:value="(val) => updateValue(key, val)"
          />
          <a-button
            type="text"
            class="!p-0 text-blue-600"
            @click="toggleEdit(key)"
          >
            <edit-outlined />
          </a-button>
        </div>
      </a-form-item>
    </div>
  </annotation-drawer-template>
</template>
