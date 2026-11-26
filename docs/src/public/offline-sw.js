/* Optional offline copy. Online navigation always uses the network first. */
const CACHE = 'skill-issue-offline-v1'
const scope = new URL(self.registration.scope)
self.addEventListener('install', event => event.waitUntil(self.skipWaiting()))
self.addEventListener('activate', event => event.waitUntil(self.clients.claim()))
function local(url) {
  return url.origin === scope.origin && url.pathname.startsWith(scope.pathname)
}
function normalized(url) {
  const value = new URL(url)
  for (const key of [...value.searchParams.keys()]) {
    if (key === 'v' || key === 'deployment' || key.startsWith('utm_')) value.searchParams.delete(key)
  }
  return value
}
async function fallback(cache, url, navigation) {
  const clean = normalized(url)
  let response = await cache.match(clean.href)
  if (response || !navigation || clean.search) return response
  if (clean.pathname.endsWith('/')) clean.pathname += 'index.html'
  else if (!clean.pathname.endsWith('.html')) {
    const dir = new URL(clean.href); dir.pathname += '/index.html'
    response = await cache.match(dir.href)
    if (response) return response
    clean.pathname += '.html'
  }
  return cache.match(clean.href)
}
self.addEventListener('fetch', event => {
  const request = event.request
  const url = new URL(request.url)
  if (request.method !== 'GET' || !local(url) || url.pathname.endsWith('/offline-sw.js') || url.pathname.endsWith('/offline-index.json')) return
  const navigation = request.mode === 'navigate'
  if (!navigation && !/\.(js|css|json|woff2?|svg)$/i.test(url.pathname)) return
  if (/\/(credentials|institutions|justificatifs|audit|database)\//.test(url.pathname)) return
  event.respondWith((async () => {
    let cache
    try { cache = await caches.open(CACHE) } catch {}
    // Fingerprinted build assets are immutable; all HTML and other assets are network-first.
    const immutable = /\/assets\/[^/]+\.[A-Za-z0-9_-]{8,}\.(js|css|woff2?)$/.test(url.pathname)
    if (immutable && cache) {
      const cached = await cache.match(url.href)
      if (cached) return cached
    }
    try {
      const response = await fetch(request, {cache: immutable ? 'default' : 'no-cache'})
      if (response.ok && cache) {
        try { await cache.put(normalized(url).href, response.clone()) } catch {}
      }
      return response
    } catch {
      const saved = cache && await fallback(cache, url, navigation)
      if (saved) return saved
      if (navigation) return new Response('<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SKILL-ISSUE · Hors ligne</title><body style="background:#09070e;color:#e5d8f4;font:16px system-ui;padding:24px"><h1>Fiche non enregistrée</h1><p>Reconnecte-toi pour télécharger la documentation depuis le menu Hors ligne.</p><a style="color:#b39aff" href="'+scope.pathname+'">Accueil</a></body></html>',{status:503,headers:{'Content-Type':'text/html; charset=utf-8'}})
      return new Response('',{status:503})
    }
  })())
})
