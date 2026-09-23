// Encrypts the catalogue data with an access code.
// Usage: node protect.mjs "ACCESS-CODE" <plain data dir> <site data dir>
import { readdirSync, readFileSync, writeFileSync, mkdirSync, rmSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { webcrypto as crypto } from 'node:crypto';
const [code, plainDir, outDir] = process.argv.slice(2);
if (!code || !plainDir || !outDir) { console.error('usage: node protect.mjs CODE plainDir outDir'); process.exit(1); }
const enc = new TextEncoder();
const salt = crypto.getRandomValues(new Uint8Array(16));
const iterations = 300000;
const norm = code.trim().toUpperCase();
const base = await crypto.subtle.importKey('raw', enc.encode(norm), 'PBKDF2', false, ['deriveKey']);
const key = await crypto.subtle.deriveKey({ name: 'PBKDF2', salt, iterations, hash: 'SHA-256' }, base, { name: 'AES-GCM', length: 256 }, false, ['encrypt']);
async function seal(bytes) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ct = new Uint8Array(await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, bytes));
  const out = new Uint8Array(12 + ct.length); out.set(iv); out.set(ct, 12); return out;
}
if (existsSync(outDir)) rmSync(outDir, { recursive: true });
mkdirSync(outDir, { recursive: true });
let n = 0;
for (const f of readdirSync(plainDir)) {
  if (!f.endsWith('.json')) continue;
  writeFileSync(join(outDir, f.replace(/\.json$/, '.bin')), await seal(readFileSync(join(plainDir, f))));
  n++;
}
const b64 = a => Buffer.from(a).toString('base64');
writeFileSync(join(outDir, 'lock.json'), JSON.stringify({ salt: b64(salt), iterations, check: b64(await seal(enc.encode('HOUSEOFA1-OK'))) }));
console.log('encrypted', n, 'files into', outDir);
