<template>
  <div class="code-view-wrapper">
    <pre class="code-pre"><code>{{ codeValue }}</code></pre>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'javascript' | 'vue'
  codeJson: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'javascript',
  codeJson: '',
})

const codeValue = computed(() => props.codeJson)
</script>

<style scoped lang="scss">
.code-view-wrapper {
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: var(--color-bg-2);
  border-radius: 4px;

  .code-pre {
    margin: 0;
    padding: 16px;
    font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.6;
    color: var(--color-text-1);
    white-space: pre;
    overflow-x: auto;
    tab-size: 2;

    code {
      font-family: inherit;
      font-size: inherit;
      line-height: inherit;
    }
  }
}
</style>
