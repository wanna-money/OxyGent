<script setup lang="ts">
import {
  LeftOutlined,
  RightOutlined,
} from '@ant-design/icons-vue'
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  open: boolean
  title: string
  width?: string | number
  submitting?: boolean
  prevText?: string
  nextText?: string
  submitText?: string
  labelWidth?: number
}>(), {
  width: 560,
  submitting: false,
  prevText: '上一个',
  nextText: '下一个',
  submitText: '提交',
  labelWidth: 88,
})

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'prev'): void
  (e: 'next'): void
  (e: 'submit'): void
}>()

const labelCol = computed(() => ({ style: { width: `${props.labelWidth}px` } }))
const wrapperCol = computed(() => ({ style: { flex: 1 } }))

function handleClose() {
  emit('update:open', false)
}
</script>

<template>
  <a-drawer
    :open="open"
    placement="right"
    :width="width"
    :destroy-on-close="true"
    :title="title"
    :body-style="{ padding: '16px', display: 'flex', flexDirection: 'column', height: '100%' }"
    @close="handleClose"
  >
    <a-form
      layout="horizontal"
      :label-col="labelCol"
      :wrapper-col="wrapperCol"
      class="annotation-drawer-form flex min-h-0 flex-1 flex-col"
    >
      <div class="min-h-0 flex-1 overflow-y-auto pr-1">
        <slot />
      </div>

      <div class="mt-3 shrink-0 border-t border-gray-200 bg-white pt-3">
        <div class="flex items-center justify-between">
          <a-space>
            <a-button @click="emit('prev')">
              <left-outlined />
              {{ prevText }}
            </a-button>
            <a-button @click="emit('next')">
              {{ nextText }}
              <right-outlined />
            </a-button>
          </a-space>
          <a-button type="primary" :loading="submitting" @click="emit('submit')">
            {{ submitText }}
          </a-button>
        </div>
      </div>
    </a-form>

    <slot name="after" />
  </a-drawer>
</template>

<style scoped>
.annotation-drawer-form :deep(.ant-form-item-label) {
  padding: 0 12px 0 0;
  text-align: right;
}
</style>
