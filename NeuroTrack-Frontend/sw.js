const CACHE_NAME = 'neurotrack-v2';
const ASSETS = [
  '/',
  '/index.html',
  '/css/style.css',
  '/js/api.js'
];

self.addEventListener('install', (e) => {
  self.skipWaiting(); // Force the waiting service worker to become the active service worker.
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
});

self.addEventListener('activate', (e) => {
  // Clear old caches
  e.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
      );
    })
  );
  self.clients.claim(); // Take control of all open pages immediately
});

self.addEventListener('fetch', (e) => {
  // Network-First Strategy: Always fetch from network if possible, fallback to cache
  e.respondWith(
    fetch(e.request)
      .then(res => {
        // Clone the response and update the cache
        const resClone = res.clone();
        caches.open(CACHE_NAME).then(cache => {
          cache.put(e.request, resClone);
        });
        return res;
      })
      .catch(err => {
        // If network fails, try the cache
        return caches.match(e.request);
      })
  );
});
