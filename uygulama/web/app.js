'use strict';
const $ = id => document.getElementById(id);
const state = {path: '', entries: [], controller: null, loaded: false};
const collator = new Intl.Collator('tr', {numeric: true, sensitivity: 'base'});
function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
function category(entry) {
  if (entry.directory) return 'folder';
  const ext = entry.name.split('.').pop().toLowerCase();
  if (['pdf','txt','md','epub','doc','docx','odt','csv','xlsx'].includes(ext)) return 'document';
  if (['jpg','jpeg','png','gif','webp','svg'].includes(ext)) return 'image';
  if (['mp4','webm','mp3','wav','ogg','m4a','mkv','mov'].includes(ext)) return 'media';
  return 'other';
}
function sizeLabel(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  const units = ['KB','MB','GB','TB'];
  let n = bytes / 1024, i = 0;
  while (n >= 1024 && i < units.length - 1) { n /= 1024; i++; }
  return `${n.toLocaleString('tr-TR', {maximumFractionDigits: 1})} ${units[i]}`;
}
function go(path) { location.hash = encodeURIComponent(path); }
function breadcrumbs() {
  $('breadcrumbs').replaceChildren();
  const names = ['Ana klasör', ...state.path.split('/').filter(Boolean)];
  names.forEach((name, i) => {
    if (i) $('breadcrumbs').append(element('span', '', '/'));
    const button = element('button', '', name);
    button.type = 'button';
    button.addEventListener('click', () => go(names.slice(1, i + 1).join('/')));
    if (i === names.length - 1) button.setAttribute('aria-current', 'page');
    $('breadcrumbs').append(button);
  });
}
function card(entry) {
  const item = element('article', 'card');
  const type = category(entry);
  const top = element('div', 'card-top');
  const extension = entry.directory ? '' : entry.name.includes('.') ? entry.name.split('.').pop().slice(0,6).toUpperCase() : 'DOSYA';
  const icon = element('span', `symbol ${type}`, extension);
  icon.setAttribute('aria-hidden', 'true');
  top.append(icon, element('span', 'badge', entry.directory ? 'KLASÖR' : 'DOSYA'));
  const name = element(entry.directory ? 'button' : 'a', 'name', entry.name);
  if (entry.directory) { name.type = 'button'; name.addEventListener('click', () => go(entry.path)); }
  else { name.href = entry.url; name.target = '_blank'; name.rel = 'noopener'; name.setAttribute('aria-label', `${entry.name} dosyasını aç (yeni sekme)`); }
  item.append(top, name);
  const bottom = element('div', 'card-bottom');
  bottom.append(element('span', 'meta', entry.directory ? 'İçeriğe göz at' : sizeLabel(entry.size)));
  if (entry.directory) { const arrow = element('span', 'arrow', '↗'); arrow.setAttribute('aria-hidden','true'); bottom.append(arrow); }
  else { const link = element('a', 'download', '↓ İndir'); link.href = `${entry.url}?download=1`; link.download = entry.name; link.setAttribute('aria-label', `${entry.name} dosyasını indir`); bottom.append(link); }
  item.append(bottom);
  return item;
}
function render() {
  if (!state.loaded) return;
  const term = $('search').value.toLocaleLowerCase('tr').trim(), type = $('filter').value;
  const entries = state.entries.filter(e => e.name.toLocaleLowerCase('tr').includes(term) && (type === 'all' || category(e) === type));
  entries.sort((a,b) => Number(b.directory) - Number(a.directory) || collator.compare(a.name,b.name));
  const fragment = document.createDocumentFragment();
  entries.forEach(entry => fragment.append(card(entry)));
  $('grid').replaceChildren(fragment);
  $('count').textContent = `${entries.length} içerik${term || type !== 'all' ? ` · Toplam ${state.entries.length}` : ' · Bu klasörde'}`;
  $('message').hidden = entries.length > 0;
  $('message').textContent = state.entries.length === 0 ? 'Bu klasör henüz boş. Cihazdaki içerik klasörüne dosyalarını ekleyebilirsin.' : 'Eşleşen içerik yok. Aramanı veya tür seçimini değiştir.';
}
async function load() {
  state.controller?.abort();
  const controller = new AbortController();
  state.controller = controller;
  const timeout = setTimeout(() => controller.abort(), 15000);
  state.loaded = false;
  $('grid').replaceChildren(); $('grid').setAttribute('aria-busy','true');
  $('refresh').disabled = true; $('message').hidden = false;
  $('message').textContent = 'İçerikler yükleniyor…'; $('count').textContent = 'Depoya bağlanılıyor…';
  try {
    state.path = decodeURIComponent(location.hash.slice(1));
    breadcrumbs();
    const response = await fetch(`/api/list?path=${encodeURIComponent(state.path)}`, {signal:controller.signal, cache:'no-store'});
    const data = await response.json();
    if (state.controller !== controller) return;
    if (!response.ok) throw new Error(data.error || 'İçerik yüklenemedi.');
    state.entries = data.entries; state.loaded = true;
    $('connection').textContent = 'Depoya bağlı'; $('connection').className = 'connection online';
    $('version').textContent = `v${data.version}`;
    render();
  } catch (error) {
    if (state.controller !== controller) return;
    $('connection').textContent = 'Erişim kontrol edilmeli'; $('connection').className = 'connection error';
    $('message').hidden = false;
    $('message').textContent = error.name === 'TypeError' || error.name === 'AbortError' ? 'Depoya ulaşılamadı. Aynı ağa bağlı olduğunu kontrol et ve Yenile düğmesine bas.' : error.message;
    $('count').textContent = 'İçerikler gösterilemiyor';
  } finally {
    clearTimeout(timeout);
    if (state.controller === controller) { $('refresh').disabled = false; $('grid').setAttribute('aria-busy','false'); }
  }
}
document.querySelector('.skip').addEventListener('click', event => {
  event.preventDefault();
  $('files').focus();
  $('files').scrollIntoView();
});
$('search').addEventListener('input',render);
$('filter').addEventListener('change',render);
$('refresh').addEventListener('click',load);
window.addEventListener('hashchange', () => { $('search').value = ''; $('filter').value = 'all'; load(); });
load();
