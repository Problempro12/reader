<template>
  <div class="privacy-policy-page">
    <div class="container mt-4 pb-5">
      <div class="policy-content" v-html="renderedMarkdown"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { marked } from 'marked';
import privacyPolicyMarkdown from '@/content/privacy_policy.md?raw';

const renderedMarkdown = ref('');

onMounted(() => {
  // Парсим Markdown и присваиваем результат реактивной переменной
  renderedMarkdown.value = marked(privacyPolicyMarkdown);
});
</script>

<style scoped>
.privacy-policy-page {
  min-height: calc(100vh - var(--header-height, 60px) - var(--footer-height, 60px));
  padding-top: var(--header-height, 60px);
  color: #fff;
  background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
}

.policy-content {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(168, 230, 207, 0.1);
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.4);
}

.policy-content h1, .policy-content h2 {
    color: #a8e6cf;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
}

.policy-content h1:first-child {
    margin-top: 0;
}

.policy-content p {
    margin-bottom: 1rem;
    line-height: 1.6;
    color: rgba(255, 255, 255, 0.8);
}

.policy-content ul {
    margin-bottom: 1rem;
    padding-left: 1.5rem;
}

.policy-content li {
    margin-bottom: 0.5rem;
    color: rgba(255, 255, 255, 0.8);
}

.policy-content strong {
    color: #a8e6cf;
}

/* Стили для ссылок внутри контента политики */
.policy-content a {
    color: #a8e6cf;
    text-decoration: none;
    transition: color 0.3s ease;
}

.policy-content a:hover {
    color: #8cd3b0;
    text-decoration: underline;
}

</style> 