import DefaultTheme from 'vitepress/theme'
import Layout from './Layout.vue'
import './custom.css'
// 先导入 Star 拦截模块，确保其模块顶层 click 监听早于 VitePress 路由创建时注册
import './star-modal-store'

export default {
  extends: DefaultTheme,
  Layout
}