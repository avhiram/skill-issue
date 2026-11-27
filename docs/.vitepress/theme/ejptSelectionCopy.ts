// Scoped to the eJPT cheatsheet. Copy a user-selected passage verbatim.
export function initEjptSelectionCopy(): () => void {
  let selectedCode: HTMLElement | null = null
  let selectedText = ''
  let active: HTMLButtonElement | null = null
  const clear = () => {
    selectedCode = null
    selectedText = ''
    if (active) {
      active.remove()
      active = null
    }
  }
  const update = () => {
    const selection = window.getSelection()
    if (!selection || selection.isCollapsed || !selection.rangeCount) {
      clear()
      return
    }
    const range = selection.getRangeAt(0)
    const element = (node: Node) => node instanceof Element ? node : node.parentElement
    const code = element(range.startContainer)?.closest<HTMLElement>('.ejpt-cheatsheet-content pre code')
    const end = element(range.endContainer)?.closest<HTMLElement>('.ejpt-cheatsheet-content pre code')
    if (!code || code !== end) { clear(); return }
    const text = selection.toString()
    if (!text.trim()) { clear(); return }
    const block = code.closest<HTMLElement>('div[class*="language-"]')
    if (!block) { clear(); return }
    if (selectedCode === code && active?.isConnected) {
      selectedText = text
      return
    }
    clear()
    selectedCode = code
    selectedText = text
    const button = document.createElement('button')
    button.type = 'button'
    button.className = 'ejpt-selection-copy'
    button.textContent = 'Copier la sélection'
    button.setAttribute('aria-label', 'Copier uniquement le texte sélectionné')
    // Keep the selection when a mouse presses the button.
    button.addEventListener('mousedown', event => event.preventDefault())
    button.addEventListener('click', async () => {
      if (!selectedText) return
      try {
        await navigator.clipboard.writeText(selectedText)
        button.textContent = 'Sélection copiée'
      } catch {
        button.textContent = 'Utiliser Ctrl+C ou Copier'
      }
    })
    block.append(button)
    active = button
  }
  // Delegated listener works for client-rendered chapters and SPA navigation.
  document.addEventListener('selectionchange', update)
  return () => {
    document.removeEventListener('selectionchange', update)
    clear()
  }
}
