<script setup lang="ts">
import { computed } from 'vue'
import AnnotationDrawerTemplate from './AnnotationDrawerTemplate.vue'
import { useI18n } from '@/locales'

const props = withDefaults(defineProps<{
  open: boolean
  title: string
  width?: string | number
  submitting?: boolean
  query?: string | null
  answer?: string | null
  isSatisfied: string
  reason: string
}>(), {
  width: 560,
  submitting: false,
  query: null,
  answer: null,
})

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'update:isSatisfied', value: string): void
  (e: 'update:reason', value: string): void
  (e: 'prev'): void
  (e: 'next'): void
  (e: 'submit'): void
}>()

const { t } = useI18n()

const isSatisfiedModel = computed({
  get: () => props.isSatisfied,
  set: value => emit('update:isSatisfied', value),
})

const reasonModel = computed({
  get: () => props.reason,
  set: value => emit('update:reason', value),
})

const queryValue = computed(() => props.query || '--')
const answerValue = computed(() => props.answer || '--')
</script>

<template>
  <annotation-drawer-template
    :open="open"
    :title="title"
    :width="width"
    :submitting="submitting"
    :prev-text="t('上一个')"
    :next-text="t('下一个')"
    :submit-text="t('提交')"
    @update:open="emit('update:open', $event)"
    @prev="emit('prev')"
    @next="emit('next')"
    @submit="emit('submit')"
  >
    <a-form-item :label="t('query')" class="mb-4">
      <a-input :value="queryValue" disabled />
    </a-form-item>
    <a-form-item :label="t('answer')" class="mb-4">
      <a-input :value="answerValue" disabled />
    </a-form-item>
    <a-form-item :label="t('是否满意')" class="mb-4">
      <a-radio-group v-model:value="isSatisfiedModel">
        <a-radio value="1">
          {{ t('满意') }}
        </a-radio>
        <a-radio value="2">
          {{ t('一般') }}
        </a-radio>
        <a-radio value="3">
          {{ t('不满意') }}
        </a-radio>
      </a-radio-group>
    </a-form-item>
    <a-form-item :label="t('原因')" class="mb-2">
      <a-textarea
        v-model:value="reasonModel"
        :rows="4"
        :maxlength="500"
        show-count
        :placeholder="t('不满意请填写原因，最多500字')"
      />
    </a-form-item>
  </annotation-drawer-template>
</template>
