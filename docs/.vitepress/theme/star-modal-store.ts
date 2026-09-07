import { ref } from 'vue'

// Star 支持模态框的共享状态与全局点击拦截。
//
// 为什么拦截逻辑必须放在「模块顶层」而不是组件 setup 内：
// VitePress 的 createRouter() 会以捕获阶段（{ capture: true }）在 window 上注册
// click 监听，并在回调开头判断 e.defaultPrevented 决定是否接管 SPA 导航
// （见 vitepress/dist/client/app/router.js）。createRouter 只在 app 入口模块主体
// （app/index.js 的 createApp()）中执行；而本模块作为 @theme/index 的静态依赖，
// 在模块求值阶段就被执行，早于 createRouter。因此在这里注册捕获阶段监听，
// 能确保 preventDefault 先于 VitePress 路由接管生效，避免模态框「一闪而过」
// 直接进入文档页的问题。

export const GITHUB_URL = 'https://github.com/Blue-Wales/FastBrace'

export const visible = ref(false)
export const quickStartHref = ref('/intro/getting-started')

// 匹配中英文首页「快速开始」按钮文案
const QUICK_START_LABELS = ['快速开始', 'Getting Started']

function onQuickStartClick(e: MouseEvent) {
  const target = (e.target as HTMLElement | null)?.closest(
    '.VPHero a.VPButton'
  ) as HTMLAnchorElement | null
  if (!target) return

  const href = target.getAttribute('href') || ''
  const text = (target.textContent || '').trim()
  const isQuickStart =
    QUICK_START_LABELS.some((label) => text.includes(label)) ||
    href.includes('/intro/getting-started')

  if (isQuickStart) {
    e.preventDefault()
    e.stopPropagation()
    quickStartHref.value = href || '/intro/getting-started'
    visible.value = true
  }
}

if (typeof window !== 'undefined') {
  window.addEventListener('click', onQuickStartClick, true)
}

export function close() {
  visible.value = false
}