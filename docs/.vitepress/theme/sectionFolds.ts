// Presentation-only accordions. Never move or rewrite Markdown/Vue content.
type Fold = { heading: HTMLElement; button: HTMLButtonElement; open: boolean }
let activeDoc: HTMLElement | null = null
let activeRoot: HTMLElement | null = null
let headings: HTMLElement[] = []
let folds: Fold[] = []
const owners = new Map<HTMLElement, Fold[]>()
const byHeading = new Map<HTMLElement, Fold>()
const genericDetails = new Map<HTMLDetailsElement, boolean>()
let report: ((count: number, allOpen: boolean) => void) | undefined
const selector = 'h2[id],h3[id],h4[id],h5[id],h6[id]'
function isHeading(node: HTMLElement) { return node.matches(selector) && !node.closest('.ignore-header,[data-outline-ignore]') }
function rootOf(doc: HTMLElement) {
  const ejpt = doc.querySelector<HTMLElement>(".ejpt-cheatsheet-content")
  if (ejpt) return ejpt
  if (doc.querySelector(':scope > h2[id],:scope > h3[id]')) return doc
  return Array.from(doc.children).find(el => el.querySelector(':scope > h2[id],:scope > h3[id]')) as HTMLElement || doc
}
function generic(node: HTMLElement): node is HTMLDetailsElement {
  return node instanceof HTMLDetailsElement && /^(afficher les commandes|voir les commandes)$/i.test(node.querySelector(':scope > summary')?.textContent?.trim() || '')
}
function render() {
  for (const [el, chain] of owners) {
    el.classList.toggle('skill-fold-hidden', chain.some(f => !f.open))
    const depth = Math.min(chain.length, 3)
    if (genericDetails.has(el as HTMLDetailsElement)) continue
    el.style.setProperty('--skill-fold-depth', String(depth))
    el.classList.toggle('skill-fold-nested', depth > 0)
  }
  for (const f of folds) {
    f.heading.classList.toggle('skill-fold-open', f.open)
    f.button.setAttribute('aria-expanded', String(f.open))
  }
  report?.(folds.length, folds.length > 0 && folds.every(f => f.open))
}
function set(f: Fold, open: boolean) { f.open = open; render() }
function build(container: HTMLElement, inherited: Fold[]) {
  const children = Array.from(container.children) as HTMLElement[]
  const stack: Fold[] = []
  for (let i=0;i<children.length;i++) {
    const node=children[i]
    if(isHeading(node)){
      const level=Number(node.tagName.slice(1))
      while(stack.length && Number(stack[stack.length-1].heading.tagName.slice(1))>=level) stack.pop()
      owners.set(node,[...inherited,...stack])
      const next=children[i+1]
      // A heading without any content or lower-level heading needs no control.
      if(!next || (isHeading(next)&&Number(next.tagName.slice(1))<=level)) continue
      const button=document.createElement('button')
      button.type='button'; button.className='skill-fold-toggle'
      button.setAttribute('aria-label', 'Afficher ou masquer : '+(node.textContent||'').replace(/\u200b/g,'').trim())
      const f:Fold={heading:node,button,open:false}
      button.addEventListener('click', event=>{event.stopPropagation();set(f,!f.open)})
      node.classList.add('skill-fold-title')
      node.append(button)
      folds.push(f);byHeading.set(node,f);stack.push(f)
    }else{
      const chain=[...inherited,...stack]
      if(chain.length) owners.set(node,chain)
      if(chain.length&&generic(node)){
        genericDetails.set(node,node.open)
        node.classList.add('skill-fold-generic')
        node.open=true
        build(node,chain)
      }
    }
  }
}
function headingClick(event: MouseEvent){
  if(!(event.target instanceof Element)||event.target.closest('a,button,input,select,textarea')||window.getSelection()?.toString())return
  const heading=event.target.closest<HTMLElement>('.skill-fold-title')
  const f=heading&&byHeading.get(heading)
  if(f)set(f,!f.open)
}
export function clearFolds(){
  activeRoot?.removeEventListener('click',headingClick)
  for(const [el] of owners){
    el.classList.remove('skill-fold-hidden','skill-fold-nested')
    el.style.removeProperty('--skill-fold-depth')
  }
  for(const f of folds){f.button.remove();f.heading.classList.remove('skill-fold-title','skill-fold-open')}
  for(const [el,open] of genericDetails){el.classList.remove('skill-fold-generic');el.open=open}
  owners.clear();byHeading.clear();genericDetails.clear();folds=[];headings=[];activeRoot=null;activeDoc=null
  report?.(0,false);report=undefined
}
export function initFolds(doc:HTMLElement, onChange:(count:number,allOpen:boolean)=>void){
  const root=rootOf(doc)
  const list=Array.from(root.querySelectorAll<HTMLElement>(selector))
  if(activeDoc===doc&&activeRoot===root&&list.length===headings.length&&list.every((x,i)=>x===headings[i]))return false
  clearFolds()
  activeDoc=doc;activeRoot=root;headings=list;report=onChange
  build(root,[])
  root.addEventListener('click',headingClick)
  render()
  return true
}
export function revealFoldTarget(target:HTMLElement|null|undefined){
  if(!target||!activeRoot?.contains(target))return
  let changed=false
  function open(f:Fold){if(!f.open){f.open=true;changed=true}}
  for(let el:HTMLElement|null=target;el&&el!==activeRoot;el=el.parentElement){
    for(const f of owners.get(el)||[])open(f)
    const own=byHeading.get(el);if(own)open(own)
  }
  if(changed)render()
}
export function toggleAllFolds(){
  const open=!folds.every(f=>f.open)
  for(const f of folds)f.open=open
  render()
}
