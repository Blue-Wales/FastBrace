<script setup lang="ts">
// 媒体分发平台：后续迭代完善
const channels = [
  {
    name: 'Bilibili',
    logo: '/media/bilibili.svg',
    href: '#',
    desc: '视频教程与实战演示'
  },
  {
    name: '小红书',
    logo: '/media/xiaohongshu.svg',
    href: '#',
    desc: '开发心得与图文笔记'
  },
  {
    name: '抖音',
    logo: '/media/douyin.svg',
    href: '#',
    desc: '短视频速览项目亮点'
  },
  {
    name: '微信公众号',
    logo: '/media/wechat-mp.svg',
    href: '#',
    desc: '深度文章与版本动态'
  }
]
</script>

<template>
  <section class="media-channels">
    <div class="media-channels-container">
      <h2 class="media-channels-title">关注我们</h2>
      <p class="media-channels-subtitle">
        关注官方账号，获取 FastBrace 最新教程、实战视频与版本动态
      </p>
      <div class="media-channels-grid">
        <a
          v-for="channel in channels"
          :key="channel.name"
          class="media-channel-card"
          :href="channel.href"
          target="_blank"
          rel="noopener"
        >
          <img class="media-channel-logo" :src="channel.logo" :alt="channel.name" />
          <span class="media-channel-name">{{ channel.name }}</span>
          <span class="media-channel-desc">{{ channel.desc }}</span>
        </a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.media-channels {
  padding: 24px 24px 64px;
}

.media-channels-container {
  margin: 0 auto;
  max-width: 1152px;
  text-align: center;
}

.media-channels-title {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 700;
  color: var(--vp-c-text-1);
}

.media-channels-subtitle {
  margin: 0 0 28px;
  font-size: 14px;
  color: var(--vp-c-text-2);
}

.media-channels-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.media-channel-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px 16px;
  border-radius: 12px;
  border: 1px solid var(--vp-c-divider, rgba(60, 60, 67, 0.12));
  background: var(--vp-c-bg-soft);
  text-decoration: none;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

.media-channel-card:hover {
  transform: translateY(-4px);
  border-color: var(--vp-c-brand-1, #3451b2);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.12);
}

.media-channel-logo {
  width: 48px;
  height: 48px;
  border-radius: 12px;
}

.media-channel-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.media-channel-desc {
  font-size: 12px;
  color: var(--vp-c-text-2);
}

@media (max-width: 768px) {
  .media-channels-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
