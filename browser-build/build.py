"""Build yes-chef.html: the browser-only Yes, Chef.

Takes a copy of the Mac app's page (source.html) and swaps:
  - the server storage for a data file you pick on the device (File System Access API),
  - the Google Fonts links for fonts built into the file, so it works offline.
The Mac app itself is never touched.
"""
import base64, pathlib, re

here = pathlib.Path(__file__).parent
# In the repo the Mac page lives at ../public/index.html; a local source.html copy wins if present.
src = here / 'source.html'
if not src.exists(): src = here.parent / 'public' / 'index.html'  # repo layout: the Mac app sits at the top
s = src.read_text()

def rep(a, b, count=1):
    global s
    assert s.count(a) == count, (a[:80], s.count(a))
    s = s.replace(a, b)

# ---------- fonts built in ----------
faces = [
    ('Barlow', 400, 'barlow', 'barlow-latin-400-normal'),
    ('Barlow', 500, 'barlow', 'barlow-latin-500-normal'),
    ('Barlow', 600, 'barlow', 'barlow-latin-600-normal'),
    ('Barlow Condensed', 500, 'barlow-condensed', 'barlow-condensed-latin-500-normal'),
    ('Barlow Condensed', 600, 'barlow-condensed', 'barlow-condensed-latin-600-normal'),
    ('Barlow Condensed', 700, 'barlow-condensed', 'barlow-condensed-latin-700-normal'),
    ('Courier Prime', 400, 'courier-prime', 'courier-prime-latin-400-normal'),
    ('Courier Prime', 700, 'courier-prime', 'courier-prime-latin-700-normal'),
]
css = []
for fam, w, pkg, f in faces:
    data = base64.b64encode((here / f'node_modules/@fontsource/{pkg}/files/{f}.woff2').read_bytes()).decode()
    css.append(f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:swap;src:url(data:font/woff2;base64,{data}) format('woff2')}}")
rep('''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Barlow:wght@400;500;600&family=Courier+Prime:wght@400;700&display=swap" rel="stylesheet">''',
    '<style>/* fonts (OFL), built in so the app works offline */\n' + '\n'.join(css) + '\n</style>')

# ---------- storage: a data file on this device ----------
start = s.index("let state = defaults();\nlet storeMode = 'file';")
end = s.index("// ---------- helpers ----------")
s = s[:start] + r'''let state = defaults();
let storeMode = 'file'; // 'file' (a data file you picked on this device) or 'browser' (fallback)
let saveTimer = null;
const LS_KEY = 'yes-chef-data'; // a safety copy kept in this browser too
let fileHandle = null;
const canUseFiles = 'showSaveFilePicker' in window && 'showOpenFilePicker' in window;
const FILE_TYPES = [{ description: 'Yes, Chef data', accept: { 'application/json': ['.json'] } }];

function lsGet(k) { try { return localStorage.getItem(k); } catch { return null; } }
function lsSet(k, v) { try { localStorage.setItem(k, v); } catch {} }

// Remember which file you picked (Chrome keeps the file "handle" in IndexedDB).
function idb(mode, fn) {
  return new Promise((resolve, reject) => {
    const open = indexedDB.open('yes-chef', 1);
    open.onupgradeneeded = () => open.result.createObjectStore('kv');
    open.onerror = () => reject(open.error);
    open.onsuccess = () => {
      try {
        const tx = open.result.transaction('kv', mode);
        const req = fn(tx.objectStore('kv'));
        tx.oncomplete = () => resolve(req && req.result);
        tx.onerror = tx.onabort = () => reject(tx.error);
      } catch (e) { reject(e); } // e.g. a handle Chrome can't store: carry on without remembering it
    };
  });
}
const idbGet = (k) => idb('readonly', (st) => st.get(k)).catch(() => null);
const idbSet = (k, v) => idb('readwrite', (st) => st.put(v, k)).catch(() => {});

function useData(raw) {
  // an older data format is about to be upgraded: keep the original in this browser first
  if (needsMigration(raw)) lsSet(`${LS_KEY}-before-v${raw.version}`, JSON.stringify(raw));
  state = normalize(raw);
  if (!raw || !raw.version) { addPractice(); state.tour = 'pending'; } // nothing saved yet: start with the walkthrough
  // if the cleanup removed anything, write it back right away
  if (raw && Array.isArray(raw.sessions) && raw.sessions.length !== state.sessions.length) setTimeout(() => save(true), 0);
}
async function readFile(h) {
  const text = (await (await h.getFile()).text()).trim();
  return text ? JSON.parse(text) : null;
}
async function connect(h, fresh) {
  fileHandle = h;
  storeMode = 'file';
  await idbSet('handle', h);
  if (fresh) { state = defaults(); addPractice(); state.tour = 'pending'; await writeNow(); } // new file: start with the walkthrough
  else useData(await readFile(h));
  $('#s-file').textContent = `Saving to ${h.name} on this device.`;
  hideBanner();
}
function useBrowser(message) {
  storeMode = 'browser';
  fileHandle = null;
  let raw = null;
  try { raw = JSON.parse(lsGet(LS_KEY) || 'null'); } catch {}
  useData(raw);
  showBanner(message);
  $('#s-file').textContent = 'Saving in this browser only.';
}

// The first screen: pick where your tickets live. Resolves once you're connected.
function gate(kind, handle) {
  const el = $('#gate');
  const reconnect = kind === 'reconnect';
  $('#gate-body').innerHTML = reconnect ? `
      <h2>Pick up where you left off</h2>
      <p>Your tickets are in <b>${esc(handle.name)}</b>. Chrome needs a quick OK to open it again.</p>
      <div class="gate-actions">
        <button class="btn go" data-g="allow">Open ${esc(handle.name)}</button>
        <button class="btn" data-g="open">Use a different file</button>
      </div>` : `
      <h2>Where should your tickets live?</h2>
      <p>Yes, Chef saves everything to a file on this device. Nothing is uploaded anywhere.</p>
      <div class="gate-actions">
        <button class="btn go" data-g="new">Create a new data file</button>
        <button class="btn" data-g="open">Open an existing file</button>
      </div>
      <p class="gate-hint">Opening works for a copy of <code>data.json</code> from the Mac version too.</p>
      <button class="btn quiet" data-g="browser">Just save in this browser for now</button>`;
  $('#gate-error').textContent = '';
  el.hidden = false;
  setTimeout(() => el.querySelector('.btn.go')?.focus(), 50);
  return new Promise((resolve) => {
    el.onclick = async (e) => {
      const g = e.target.closest('[data-g]')?.dataset.g;
      if (!g) return;
      try {
        if (g === 'allow') {
          if (await handle.requestPermission({ mode: 'readwrite' }) !== 'granted') return;
          await connect(handle);
        } else if (g === 'new') {
          await connect(await window.showSaveFilePicker({ suggestedName: 'yes-chef-data.json', types: FILE_TYPES }), true);
        } else if (g === 'open') {
          const [h] = await window.showOpenFilePicker({ types: FILE_TYPES, multiple: false });
          if (await h.requestPermission({ mode: 'readwrite' }) !== 'granted') return;
          await connect(h);
        } else if (g === 'browser') {
          useBrowser('Saving in this browser only. Pick a data file in Settings any time, or use Export data to keep a backup.');
        }
        el.hidden = true;
        el.onclick = null;
        resolve();
      } catch (err) {
        if (err && err.name === 'AbortError') return; // closed the file picker
        if (err instanceof SyntaxError) { $('#gate-error').textContent = 'That file isn\'t Yes, Chef data. Pick a .json file saved by Yes, Chef.'; return; }
        $('#gate-error').textContent = 'This device won\'t let Yes, Chef use files (a school or work setting can do that). Choose "Just save in this browser" instead.';
      }
    };
  });
}

async function load() {
  if (!canUseFiles) return useBrowser('This browser can\'t save to a file, so Yes, Chef is saving in this browser only. Use Settings → Export data to keep a backup.');
  const h = await idbGet('handle');
  if (h) {
    try {
      if (await h.queryPermission({ mode: 'readwrite' }) === 'granted') return await connect(h);
      return await gate('reconnect', h);
    } catch { /* the file moved or was deleted: ask again */ }
  }
  return gate('setup');
}

let writing = Promise.resolve();
function writeNow() {
  const body = JSON.stringify(state, null, 2);
  lsSet(LS_KEY, body);
  if (storeMode !== 'file' || !fileHandle) return writing;
  const h = fileHandle;
  writing = writing.then(async () => {
    const w = await h.createWritable();
    await w.write(body);
    await w.close();
  }).then(() => hideBanner(), () => {
    showBanner(`Couldn't save to ${h.name}. Your latest changes are kept in this browser for now. Open Settings to pick the file again.`);
  });
  return writing;
}
function save(now) {
  clearTimeout(saveTimer);
  if (now) writeNow(); else saveTimer = setTimeout(writeNow, 150);
}

''' + s[end:]

# ---------- the first-run screen ----------
rep('<div class="banner" id="banner" hidden></div>', '''<div class="banner" id="banner" hidden></div>

<section class="gate" id="gate" hidden role="dialog" aria-modal="true" aria-label="Choose your data file">
  <div class="gate-card">
    <div class="gate-logo" id="gate-logo"></div>
    <div id="gate-body"></div>
    <p class="gate-error" id="gate-error" role="alert"></p>
    <p class="gate-code">Free and open source. <a href="https://github.com/KKubesh/yes-chef" target="_blank" rel="noopener noreferrer">View the code on GitHub</a></p>
  </div>
</section>''')
rep('/* ---------- dialogs ---------- */', '''/* ---------- first-run: pick a data file ---------- */
.gate { position: fixed; inset: 0; z-index: 200; display: grid; place-items: center; padding: 16px; background: var(--steel); }
.gate[hidden] { display: none; }
.gate-card {
  width: min(460px, 100%);
  background: var(--receipt); color: #2a2723;
  -webkit-mask: var(--torn); mask: var(--torn);
  padding: 40px 32px 44px;
  font: 16px/1.5 var(--print);
  filter: drop-shadow(0 12px 24px rgba(0,0,0,.18));
  rotate: -0.6deg;
}
.gate-logo .logo { height: 58px; width: auto; color: #2a2723; display: block; margin: 0 0 18px; }
.gate-card h2 { font: 700 24px/1.2 var(--print); margin: 0 0 10px; }
.gate-card p { margin: 0 0 20px; }
.gate-actions { display: grid; gap: 10px; margin-bottom: 14px; }
.gate-card .btn { border-color: #2a2723; color: #2a2723; font-family: var(--print); padding: 11px 16px; }
.gate-card .btn.go { background: var(--order); border-color: var(--order); color: var(--order-ink); font-weight: 700; }
.gate-card .gate-code { margin: 18px 0 0; padding-top: 14px; border-top: 1.5px dashed rgba(42,39,35,.3); font-size: 13px; color: #6b655b; }
.gate-card .gate-code a { color: #2a2723; }
.gate-card .btn.quiet { border-color: transparent; color: #6b655b; padding: 6px 0; text-decoration: underline; text-underline-offset: 3px; }
.gate-hint { font-size: 13px; color: #6b655b; }
.gate-hint code { font-family: var(--print); background: rgba(42,39,35,.08); padding: 0 4px; border-radius: 3px; }
.gate-error { color: #9a3a2a; font-size: 14px; margin: 10px 0 0 !important; }
.gate-error:empty { display: none; }

/* ---------- dialogs ---------- */''')

# Settings: show the file and let you switch
rep('<p class="hint" id="s-file"></p>', '<p class="hint" id="s-file"></p>\n    <button type="button" class="btn quiet" id="s-switch" style="margin-top:10px">Use a different data file</button>')

# startup: put the logo on the first screen, then load (which may show the first screen)
rep('''(async function init() {
  wire();
  await load();''', '''(async function init() {
  wire();
  $('#gate-logo').innerHTML = $('.wordmark .logo').outerHTML;
  $('#s-switch').addEventListener('click', async () => {
    $('#settings-dlg').close();
    if (!canUseFiles) return;
    await gate('setup');
    applyTheme(); render();
    if (state.tour === 'pending') beginOnboarding();
  });
  await load();''')

# ---------- lock it offline ----------
# Tells Chrome this page may never connect to anything: no network, no outside scripts,
# fonts or images. Everything it needs is already inside the file.
rep('<meta charset="utf-8">', '''<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; font-src data:; img-src data:; connect-src 'none'; form-action 'none'; base-uri 'none'">''')

assert '/api/' not in s, 'server calls left over'
(here / 'yes-chef.html').write_text(s)
print('wrote yes-chef.html', round(len(s) / 1024), 'KB')

# keep the README's fingerprint in step with the file
import hashlib
digest = hashlib.sha256((here / 'yes-chef.html').read_bytes()).hexdigest()
readme = here / 'README.md'
if not readme.exists(): readme = here.parent / 'README.md'  # repo layout: the README sits at the top
r = readme.read_text()
lock_line = "  Chrome enforces this, not just the code: a line at the top of the file (a Content Security Policy) tells Chrome to refuse any connection the page tries to make. Anyone technical can check that one line instead of reading the whole file."
anchor = 'It works with Wi-Fi turned off.'
if lock_line not in r and anchor in r: r = r.replace(anchor, anchor + '\n' + lock_line, 1)
a, z = '<!-- checksum:start -->\n', '\n<!-- checksum:end -->'
i, j = r.index(a) + len(a), r.index(z)
readme.write_text(r[:i] + f'`{digest}`' + r[j:])
print('README fingerprint', digest)
