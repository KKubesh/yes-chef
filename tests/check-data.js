// Checks that every sample data file in tests/fixtures still opens in the current app without losing anything.
// Run before shipping a build:  node tests/check-data.js   (needs Playwright with Chromium)
// For each file: the app loads it with no errors, shows the expected points, and anything it saves back
// still has every ticket and session from the original, at the current data version.
const path = require('path'), fs = require('fs');
let pw; try { pw = require('playwright'); } catch { pw = require('/opt/npm-tools/node_modules/playwright'); }
const page = fs.readFileSync(process.env.APP_PAGE || path.join(__dirname, '..', 'public', 'index.html'), 'utf8');
const dir = path.join(__dirname, 'fixtures');
(async () => {
  const browser = await pw.chromium.launch();
  let failed = 0;
  for (const name of fs.readdirSync(dir).filter(f => f.endsWith('.json'))) {
    const fixture = JSON.parse(fs.readFileSync(path.join(dir, name), 'utf8'));
    const expect = fixture._expect || {};
    let saved = null; const errors = [];
    const p = await browser.newPage();
    p.on('pageerror', e => errors.push(e.message));
    await p.route('**/*', async (route) => {
      const u = new URL(route.request().url());
      if (u.pathname === '/') return route.fulfill({ body: page, contentType: 'text/html' });
      if (u.pathname === '/api/data' && route.request().method() === 'GET') return route.fulfill({ body: JSON.stringify(fixture), contentType: 'application/json' });
      if (u.pathname === '/api/data') { saved = JSON.parse(route.request().postData()); return route.fulfill({ status: 204 }); }
      if (u.pathname === '/api/info') return route.fulfill({ body: '{"dataFile":"fixture"}', contentType: 'application/json' });
      return route.fulfill({ status: 404, body: '' });
    });
    await p.goto('http://app.test/'); await p.waitForTimeout(800);
    // make a harmless change so the app saves, then check what it wrote
    await p.evaluate(() => { const b = document.querySelector('#filter button[data-f=all]'); b && b.click(); });
    await p.fill('#add-name', 'check'); await p.press('#add-name', 'Enter'); await p.waitForTimeout(600);
    const points = Number((await p.textContent('#stats .stat b')).replace(/[^\d]/g, ''));
    const problems = [...errors];
    if (expect.points != null && points !== expect.points) problems.push(`points ${points}, expected ${expect.points}`);
    if (!saved) problems.push('nothing was saved');
    else {
      const ids = (arr) => new Set((arr || []).map(x => x.id));
      const st = ids(saved.tickets), ss = ids(saved.sessions);
      fixture.tickets.forEach(t => st.has(t.id) || problems.push(`lost ticket ${t.id}`));
      fixture.sessions.forEach(x => ss.has(x.id) || problems.push(`lost session ${x.id}`));
      (fixture.shifts || []).forEach(x => ids(saved.shifts).has(x.id) || problems.push(`lost shift ${x.id}`));
      (fixture.purchases || []).forEach(x => ids(saved.purchases).has(x.id) || problems.push(`lost claim ${x.id}`));
      const v = Number((page.match(/const DATA_VERSION = (\d+);/) || [])[1]);
      if (v && saved.version !== v) problems.push(`saved as version ${saved.version}, app is ${v}`);
    }
    console.log(`${problems.length ? 'FAIL' : 'ok  '} ${name}${problems.length ? ': ' + problems.join('; ') : ''}`);
    failed += problems.length ? 1 : 0;
    await p.close();
  }
  await browser.close();
  process.exit(failed ? 1 : 0);
})();
