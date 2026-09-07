<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vitepress'
import { GITHUB_URL, close, quickStartHref, visible } from '../star-modal-store'

const router = useRouter()

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') close()
}

function goQuickStart() {
  close()
  router.go(quickStartHref.value)
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
})
onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <Teleport to="body">
    <Transition name="star-modal">
      <div v-if="visible" class="star-modal-mask" @click.self="close">
        <div class="star-modal-card" role="dialog" aria-modal="true">
          <button class="star-modal-close" aria-label="关闭" @click="close">
            ×
          </button>

          <!-- 动画星星区域 -->
          <div class="star-modal-stage">
            <span class="spark spark-1">✦</span>
            <span class="spark spark-2">✦</span>
            <span class="spark spark-3">✧</span>
            <div class="star-main">⭐</div>
          </div>

          <h2 class="star-modal-title">开源不易，给个 Star 支持一下</h2>
          <p class="star-modal-desc">
            如果 FastBrace 对你有帮助，点亮一颗 Star 就是对项目最大的鼓励。
          </p>

          <div class="star-modal-actions">
            <a
              class="star-btn star-btn-primary"
              :href="GITHUB_URL"
              target="_blank"
              rel="noopener"
            >
              ⭐ 立刻 Star
            </a>
            <button class="star-btn star-btn-ghost" @click="goQuickStart">
              已 Star，进入快速开始
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.star-modal-mask {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(6px);
}

.star-modal-card {
  position: relative;
  width: 100%;
  max-width: 420px;
  padding: 40px 32px 32px;
  text-align: center;
  background: var(--vp-c-bg-soft, #fff);
  border: 1px solid var(--vp-c-divider, rgba(60, 60, 67, 0.12));
  border-radius: 20px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.25);
}

.star-modal-close {
  position: absolute;
  top: 12px;
  right: 16px;
  font-size: 22px;
  line-height: 1;
  color: var(--vp-c-text-2);
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
}
.star-modal-close:hover {
  color: var(--vp-c-text-1);
}

/* ========== 动画舞台 ========== */
.star-modal-stage {
  position: relative;
  height: 96px;
  margin-bottom: 8px;
}

.star-main {
  font-size: 64px;
  line-height: 96px;
  animation: star-pop 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) both,
    star-float 2.6s ease-in-out 0.6s infinite;
}

.spark {
  position: absolute;
  color: var(--vp-c-brand-1, #3451b2);
  opacity: 0;
  animation: spark-twinkle 1.8s ease-in-out infinite;
}
.spark-1 {
  top: 6px;
  left: 26%;
  font-size: 18px;
  animation-delay: 0.2s;
}
.spark-2 {
  top: 14px;
  right: 24%;
  font-size: 14px;
  animation-delay: 0.7s;
}
.spark-3 {
  bottom: 4px;
  right: 32%;
  font-size: 20px;
  animation-delay: 1.1s;
}

.star-modal-title {
  margin: 0 0 10px;
  font-size: 20px;
  font-weight: 700;
  color: var(--vp-c-text-1);
}

.star-modal-desc {
  margin: 0 0 24px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--vp-c-text-2);
}

/* ========== 按钮 ========== */
.star-modal-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.star-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  border-radius: 10px;
  border: 1px solid transparent;
  cursor: pointer;
  text-decoration: none;
  transition: transform 0.2s, box-shadow 0.2s, background-color 0.2s;
}
.star-btn:active {
  transform: scale(0.96);
}

.star-btn-primary {
  color: #fff;
  background: var(--vp-c-brand-1, #3451b2);
  box-shadow: 0 6px 18px rgba(52, 81, 178, 0.35);
}
.star-btn-primary:hover {
  background: var(--vp-c-brand-2, #405fd6);
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(52, 81, 178, 0.45);
}

.star-btn-ghost {
  color: var(--vp-c-text-1);
  background: var(--vp-c-bg-mute, #f1f1f1);
}
.star-btn-ghost:hover {
  background: var(--vp-c-bg-alt, #e7e7e7);
}

/* ========== 过渡与关键帧动画 ========== */
.star-modal-enter-active .star-modal-card {
  transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.25s ease;
}
.star-modal-leave-active .star-modal-card {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.star-modal-enter-from .star-modal-card,
.star-modal-leave-to .star-modal-card {
  opacity: 0;
  transform: translateY(28px) scale(0.9);
}
.star-modal-enter-active,
.star-modal-leave-active {
  transition: opacity 0.25s ease;
}
.star-modal-enter-from,
.star-modal-leave-to {
  opacity: 0;
}

@keyframes star-pop {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes star-float {
  0%,
  100% {
    transform: translateY(0) rotate(-3deg);
  }
  50% {
    transform: translateY(-8px) rotate(3deg);
  }
}

@keyframes spark-twinkle {
  0%,
  100% {
    opacity: 0;
    transform: scale(0.4) rotate(0deg);
  }
  50% {
    opacity: 1;
    transform: scale(1.15) rotate(20deg);
  }
}
</style>
