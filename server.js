// Yes, Chef — tiny local server. No dependencies.
// Serves the app and saves everything to data.json next to this file.
// Run:  node server.js   then open http://localhost:4747

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.env.PORT) || 4747;
const HOST = '127.0.0.1'; // only reachable from this computer
const DATA_FILE = process.env.FOCUS_DATA || path.join(__dirname, 'data.json');
const BACKUP_DIR = path.join(path.dirname(DATA_FILE), 'backups');
const PUBLIC_DIR = path.join(__dirname, 'public');
const MAX_BODY = 10 * 1024 * 1024;

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
};

function send(res, status, body, type = 'text/plain; charset=utf-8') {
  res.writeHead(status, { 'Content-Type': type, 'Cache-Control': 'no-store' });
  res.end(body);
}

function readData() {
  try {
    return fs.readFileSync(DATA_FILE, 'utf8');
  } catch (e) {
    if (e.code === 'ENOENT') return '{}';
    throw e;
  }
}

function dailyBackup(current) {
  // Keep one snapshot per day so a bad save never loses more than a day.
  try {
    fs.mkdirSync(BACKUP_DIR, { recursive: true });
    const day = new Date().toISOString().slice(0, 10);
    const file = path.join(BACKUP_DIR, `data-${day}.json`);
    if (!fs.existsSync(file) && current && current !== '{}') fs.writeFileSync(file, current);
  } catch (e) {
    console.warn('Backup skipped:', e.message);
  }
}

// Before a save that upgrades the data format, keep the original as backups/data-v<old>-<date>.json.
function upgradeBackup(current, incoming) {
  try {
    const was = JSON.parse(current || '{}').version, now = JSON.parse(incoming).version;
    if (!was || !now || now <= was) return;
    fs.mkdirSync(BACKUP_DIR, { recursive: true });
    const file = path.join(BACKUP_DIR, `data-v${was}-${new Date().toISOString().slice(0, 10)}.json`);
    if (!fs.existsSync(file)) fs.writeFileSync(file, current);
  } catch (e) {
    console.warn('Upgrade backup skipped:', e.message);
  }
}

function writeData(json) {
  const current = readData();
  upgradeBackup(current, json);
  dailyBackup(current);
  const tmp = DATA_FILE + '.tmp';
  fs.writeFileSync(tmp, json);
  fs.renameSync(tmp, DATA_FILE); // atomic swap, so a crash never leaves half a file
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);

  if (url.pathname === '/api/data') {
    if (req.method === 'GET') {
      try {
        return send(res, 200, readData(), TYPES['.json']);
      } catch (e) {
        return send(res, 500, `Could not read ${DATA_FILE}: ${e.message}`);
      }
    }
    if (req.method === 'PUT' || req.method === 'POST') {
      let size = 0;
      const chunks = [];
      req.on('data', (c) => {
        size += c.length;
        if (size > MAX_BODY) req.destroy();
        else chunks.push(c);
      });
      req.on('end', () => {
        const body = Buffer.concat(chunks).toString('utf8');
        try {
          const parsed = JSON.parse(body);
          if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) throw new Error('Expected an object');
          writeData(JSON.stringify(parsed, null, 2));
          send(res, 204, '');
        } catch (e) {
          send(res, 400, `Not saved: ${e.message}`);
        }
      });
      return;
    }
    return send(res, 405, 'Method not allowed');
  }

  if (url.pathname === '/api/info') {
    return send(res, 200, JSON.stringify({ dataFile: DATA_FILE }), TYPES['.json']);
  }

  if (req.method !== 'GET') return send(res, 405, 'Method not allowed');
  const rel = url.pathname === '/' ? 'index.html' : decodeURIComponent(url.pathname).replace(/^\/+/, '');
  const file = path.normalize(path.join(PUBLIC_DIR, rel));
  if (!file.startsWith(PUBLIC_DIR)) return send(res, 403, 'Forbidden');
  fs.readFile(file, (err, buf) => {
    if (err) return send(res, 404, 'Not found');
    send(res, 200, buf, TYPES[path.extname(file)] || 'application/octet-stream');
  });
});

server.on('error', (e) => {
  if (e.code === 'EADDRINUSE') {
    console.log(`Yes, Chef is already running at http://localhost:${PORT}`);
    process.exit(0);
  }
  throw e;
});

server.listen(PORT, HOST, () => {
  console.log(`Yes, Chef running at http://localhost:${PORT}`);
  console.log(`Saving to ${DATA_FILE}`);
});
