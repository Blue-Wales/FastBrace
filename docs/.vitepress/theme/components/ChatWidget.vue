<script setup lang="ts">
import { onMounted } from 'vue'

// 聊天服务基础地址，需要配置在线客服地址 (xx 替换为实际ip地址)
const CHAT_BASE_URL = 'http://xx.xx.xx.xx:8081'.replace(/\/+$/, '')

const SCRIPT_ID = 'FastBrace-chat-widget'

onMounted(() => {
  // 避免重复注入（例如 SPA 路由切换或组件重复挂载）
  if (document.getElementById(SCRIPT_ID)) return

  const script = document.createElement('script')
  script.id = SCRIPT_ID
  script.type = 'text/javascript'
  script.src = `${CHAT_BASE_URL}/static/js/chat-widget.js`
  script.onload = () => {
    // 注意：chat-widget.js 顶层用 const 声明 CHAT_WIDGET，不会挂到 window 上，
    // 因此这里不能通过 window.CHAT_WIDGET 访问；注入一段经典内联脚本，
    // 用裸标识符（全局词法环境）调用，与官方接入代码语义一致。
    const init = document.createElement('script')
    init.textContent = `CHAT_WIDGET.initialize({ API_URL: '${CHAT_BASE_URL}', AGENT_ID: 'agent' });`
    document.head.appendChild(init)
  }
  script.onerror = () => {
    // 加载失败不阻塞文档站正常使用
    console.warn(`[FastBrace Docs] 聊天挂件加载失败: ${script.src}`)
  }
  document.head.appendChild(script)
})
</script>

<template>
  <!-- 聊天挂件由 chat-widget.js 自行渲染头像与聊天窗口，本组件仅负责注入脚本 -->
</template>