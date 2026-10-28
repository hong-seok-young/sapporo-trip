const V='sg-'+'20261029-0015';const IMG='sg-img',FONT='sg-font';
const CORE=['./','./index.html','./app.webmanifest','./icon-192.png','./icon-512.png','./icon-maskable.png','./apple-touch-icon.png','./bus.jpg'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('sg-')&&k!==V&&k!==IMG&&k!==FONT).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{const r=e.request;if(r.method!=='GET')return;const u=new URL(r.url);
  if(u.origin===location.origin){
    if(r.mode==='navigate'||u.pathname.endsWith('/index.html')||u.pathname.endsWith('/')){
      e.respondWith(fetch(u.href,{cache:'no-cache',credentials:'same-origin'}).then(res=>{if(res.ok){const c=res.clone();caches.open(V).then(x=>{x.put('./index.html',c.clone());x.put('./',c)})}return res}).catch(()=>caches.match('./index.html')));return}
    e.respondWith(caches.match(r).then(c=>c||fetch(r).then(res=>{if(res.ok){const cc=res.clone();caches.open(V).then(x=>x.put(r,cc))}return res})));return}
  if(u.hostname==='upload.wikimedia.org'){
    e.respondWith(caches.open(IMG).then(async c=>{const h=await c.match(r);if(h)return h;const res=await fetch(r);if(res.ok)c.put(r,res.clone());return res}).catch(()=>new Response('',{status:504})));return}
  if(u.hostname==='fonts.googleapis.com'||u.hostname==='fonts.gstatic.com'){
    e.respondWith(caches.open(FONT).then(async c=>{const h=await c.match(r);const n=fetch(r).then(res=>{if(res.ok)c.put(r,res.clone());return res}).catch(()=>h);return h||n}));return}
});
