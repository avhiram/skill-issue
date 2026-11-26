import { h, onMounted, onUnmounted, nextTick, watch } from 'vue'
import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import SmartOutline from './components/SmartOutline.vue'
import PageTools from './components/PageTools.vue'
import LabVariables from './components/LabVariables.vue'
import LabCommand from './components/LabCommand.vue'
import CustomSidebarItem from './components/CustomSidebarItem.vue'
import TransferSelector from './components/TransferSelector.vue'
import AcademyJourney from './components/AcademyJourney.vue'
import BountyChecklist from './components/BountyChecklist.vue'
import BountyTarget from './components/BountyTarget.vue'
import BountyCommand from './components/BountyCommand.vue'
import { enhanceAppWithTabs } from 'vitepress-plugin-tabs/client'
import mediumZoom from 'medium-zoom'
import { useRoute } from 'vitepress'
import './custom.css'


function initInstitutionMarquee(): () => void {
  const viewport = document.querySelector<HTMLElement>('.profile-marquee-wrap')
  const firstGroup = viewport?.querySelector<HTMLElement>('.profile-marquee-group')
  if (!viewport || !firstGroup) return () => {}

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
  let frame = 0
  let lastFrame = 0
  let pausedUntil = 0
  let isHovered = false
  let pointerDown = false
  let wasDragged = false
  let suppressClick = false
  let startX = 0
  let startScroll = 0

  const groupWidth = () => firstGroup.getBoundingClientRect().width
  const normalize = () => {
    const width = groupWidth()
    if (width <= 0) return
    if (viewport.scrollLeft >= width) viewport.scrollLeft -= width
  }
  const tick = (now: number) => {
    const elapsed = lastFrame ? Math.min(now - lastFrame, 60) : 0
    lastFrame = now
    if (!prefersReducedMotion.matches && !isHovered && !pointerDown &&
        now > pausedUntil && document.visibilityState === 'visible') {
      viewport.scrollLeft += elapsed * 0.032
      normalize()
    }
    frame = window.requestAnimationFrame(tick)
  }
  const onPointerDown = (event: PointerEvent) => {
    if (event.pointerType === 'mouse' && event.button !== 0) return
    pointerDown = true
    wasDragged = false
    startX = event.clientX
    startScroll = viewport.scrollLeft
    pausedUntil = performance.now() + 2500
  }
  const onPointerMove = (event: PointerEvent) => {
    if (!pointerDown || event.pointerType === 'touch') return
    const delta = event.clientX - startX
    if (!wasDragged && Math.abs(delta) > 5) {
      wasDragged = true
      viewport.classList.add('is-dragging')
      viewport.setPointerCapture(event.pointerId)
    }
    if (wasDragged) {
      const width = groupWidth()
      let target = startScroll - delta
      if (width > 0 && target < 0) target += width
      if (width > 0 && target >= width) target -= width
      viewport.scrollLeft = target
      event.preventDefault()
    }
  }
  const onPointerUp = (event: PointerEvent) => {
    if (!pointerDown) return
    pointerDown = false
    viewport.classList.remove('is-dragging')
    if (wasDragged) {
      suppressClick = true
      window.setTimeout(() => { suppressClick = false }, 160)
    }
    if (viewport.hasPointerCapture(event.pointerId)) viewport.releasePointerCapture(event.pointerId)
    pausedUntil = performance.now() + 2500
  }
  const onDragStart = (event: DragEvent) => event.preventDefault()
  const onClick = (event: MouseEvent) => {
    if (!suppressClick) return
    event.preventDefault()
    event.stopPropagation()
    suppressClick = false
  }
  const onPointerEnter = () => { isHovered = true }
  const onPointerLeave = () => { isHovered = false }
  const onTouchStart = () => { pausedUntil = performance.now() + 3000 }
  const onTouchEnd = () => { pausedUntil = performance.now() + 3000 }

  viewport.addEventListener('pointerdown', onPointerDown)
  viewport.addEventListener('pointermove', onPointerMove)
  viewport.addEventListener('pointerup', onPointerUp)
  viewport.addEventListener('pointercancel', onPointerUp)
  viewport.addEventListener('click', onClick, true)
  viewport.addEventListener('dragstart', onDragStart)
  viewport.addEventListener('pointerenter', onPointerEnter)
  viewport.addEventListener('pointerleave', onPointerLeave)
  viewport.addEventListener('touchstart', onTouchStart, { passive: true })
  viewport.addEventListener('touchend', onTouchEnd, { passive: true })
  frame = window.requestAnimationFrame(tick)
  return () => {
    window.cancelAnimationFrame(frame)
    viewport.removeEventListener('pointerdown', onPointerDown)
    viewport.removeEventListener('pointermove', onPointerMove)
    viewport.removeEventListener('pointerup', onPointerUp)
    viewport.removeEventListener('pointercancel', onPointerUp)
    viewport.removeEventListener('click', onClick, true)
    viewport.removeEventListener('dragstart', onDragStart)
    viewport.removeEventListener('pointerenter', onPointerEnter)
    viewport.removeEventListener('pointerleave', onPointerLeave)
    viewport.removeEventListener('touchstart', onTouchStart)
    viewport.removeEventListener('touchend', onTouchEnd)
  }
}

export default {
  extends: DefaultTheme,
  Layout: () => h(DefaultTheme.Layout, null, {
    'aside-outline-before': () => h(SmartOutline, { mode: 'desktop' }),
    'doc-before': () => [h(PageTools), h(SmartOutline, { mode: 'mobile' })]
  }),
  enhanceApp({ app }) {
    app.component('VPSidebarItem', CustomSidebarItem)
    app.component('TransferSelector', TransferSelector)
    app.component('AcademyJourney', AcademyJourney)
    app.component('BountyChecklist', BountyChecklist)
    app.component('BountyTarget', BountyTarget)
    app.component('BountyCommand', BountyCommand)
    app.component('LabVariables', LabVariables)
    app.component('LabCommand', LabCommand)
    enhanceAppWithTabs(app)
  },
  setup() {
    const route = useRoute()
    const initZoom = () => mediumZoom('.main img', {
      background: 'var(--vp-c-bg)',
      margin: 20
    })
    let cleanupMarquee: () => void = () => {}
    onMounted(() => {
      initZoom()
      cleanupMarquee = initInstitutionMarquee()
    })
    onUnmounted(() => cleanupMarquee())
    watch(() => route.path, () => nextTick(() => {
      initZoom()
      cleanupMarquee()
      cleanupMarquee = initInstitutionMarquee()
    }))
  }
} satisfies Theme
