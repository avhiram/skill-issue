import { onMounted, nextTick, watch } from 'vue'
import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import CustomSidebarItem from './components/CustomSidebarItem.vue'
import TransferSelector from './components/TransferSelector.vue'
import AcademyRoadmap from './components/AcademyRoadmap.vue'
import AcademyPractical from './components/AcademyPractical.vue'
import { enhanceAppWithTabs } from 'vitepress-plugin-tabs/client'
import mediumZoom from 'medium-zoom'
import { useRoute } from 'vitepress'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('VPSidebarItem', CustomSidebarItem)
    app.component('TransferSelector', TransferSelector)
    app.component('AcademyRoadmap', AcademyRoadmap)
    app.component('AcademyPractical', AcademyPractical)
    enhanceAppWithTabs(app)
  },
  setup() {
    const route = useRoute()
    const initZoom = () => mediumZoom('.main img', {
      background: 'var(--vp-c-bg)',
      margin: 20
    })
    onMounted(initZoom)
    watch(() => route.path, () => nextTick(initZoom))
  }
} satisfies Theme
