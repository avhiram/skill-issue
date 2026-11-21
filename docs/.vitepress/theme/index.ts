import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import CustomSidebarItem from './components/CustomSidebarItem.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('VPSidebarItem', CustomSidebarItem)
  }
} satisfies Theme
