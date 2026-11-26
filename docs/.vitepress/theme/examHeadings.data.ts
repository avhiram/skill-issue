import { createContentLoader } from 'vitepress'
import { examGroups } from './examNavigation'
type Heading = { label: string; id: string; level: number }
declare const data: Record<string, Heading[]>
export { data }
const names = [...new Set(examGroups.flatMap(group => group.links.map(link => link.path.split('#')[0].replace('/oscp/', ''))))]
const decode = (s: string) => s.replace(/&(#x[0-9a-f]+|#\d+|amp|lt|gt|quot|apos|nbsp);/gi, (whole, entity: string) => {
  const known: Record<string,string> = {amp:'&',lt:'<',gt:'>',quot:'"',apos:"'",nbsp:' '}
  if(entity.startsWith('#')) {
    const n = entity[1].toLowerCase()==='x' ? parseInt(entity.slice(2),16) : parseInt(entity.slice(1),10)
    return Number.isFinite(n) && n>=0 && n<=0x10ffff ? String.fromCodePoint(n) : whole
  }
  return known[entity] ?? whole
})
export default createContentLoader('oscp/{'+names.join(',')+'}.md', {
  render: true,
  transform(pages) {
    const result: Record<string, Heading[]> = {}
    for (const page of pages) {
      const path = '/oscp/' + page.url.split('/').filter(Boolean).pop()!.replace(/\.html$/, '')
      const seen = new Set<string>()
      const headings: Heading[] = []
      for (const match of (page.html || '').matchAll(/<h([2-6])\b([^>]*)>([\s\S]*?)<\/h\1>/gi)) {
        const idMatch = /\bid="([^"]+)"/.exec(match[2])
        if (!idMatch) continue
        const id = decode(idMatch[1])
        const label = decode(match[3].replace(/<a\b[^>]*class="[^"]*header-anchor[^"]*"[^>]*>[\s\S]*?<\/a>/gi,'').replace(/<[^>]*>/g,'')).replace(/\u200b/g,'').replace(/\s+/g,' ').trim()
        if (!label || seen.has(id)) continue
        seen.add(id)
        headings.push({ label, id, level: Number(match[1]) })
      }
      result[path] = headings
    }
    return result
  }
})
