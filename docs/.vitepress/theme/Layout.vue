<script setup lang="ts">
import DefaultTheme from 'vitepress/theme'
import { useData } from 'vitepress'
import StarModal from './components/StarModal.vue'
import MediaChannels from './components/MediaChannels.vue'
import ChatWidget from './components/ChatWidget.vue'

const { frontmatter } = useData()
</script>

<template>
  <DefaultTheme.Layout>
    <!-- 首页：Star 支持模态框（拦截「快速开始」按钮） -->
    <template v-if="frontmatter.layout === 'home'" #home-hero-after>
      <StarModal />
    </template>
    <!-- 首页：features 下方的媒体分发平台 -->
    <template v-if="frontmatter.layout === 'home'" #home-features-after>
      <MediaChannels />
    </template>
  </DefaultTheme.Layout>

  <!-- 全站客服聊天挂件：右侧头像，点击展开聊天 -->
  <ChatWidget />
</template>
