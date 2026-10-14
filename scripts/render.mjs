// Render PNG previews of every SVG and turn video/demo.svg into video/demo.mp4.
// Needs Playwright (Chromium) and ffmpeg on PATH.  Usage: node scripts/render.mjs
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); }

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const browser = await chromium.launch();

async function pageFor(file) {
  const src = readFileSync(file, 'utf8');
  const [, w, h] = src.match(/viewBox="0 0 (\d+) (\d+)"/);
  const page = await browser.newPage({ viewport: { width: +w, height: +h } });
  await page.setContent(`<html><body style="margin:0">${src}</body></html>`);
  await page.evaluate(() => document.fonts.ready);
  return page;
}

for (const dir of ['posters', 'social']) {
  for (const f of readdirSync(path.join(root, dir)).filter((f) => f.endsWith('.svg'))) {
    const page = await pageFor(path.join(root, dir, f));
    const out = path.join(root, dir, 'png', f.replace('.svg', '.png'));
    await page.screenshot({ path: out });
    await page.close();
    console.log('png', path.relative(root, out));
  }
}

// Video: pause every CSS animation and scrub it frame by frame.
const FPS = 30, SECONDS = 30;
const page = await pageFor(path.join(root, 'video', 'demo.svg'));
const frames = mkdtempSync(path.join(tmpdir(), 'csequity-frames-'));
for (let i = 0; i < FPS * SECONDS; i++) {
  await page.evaluate((ms) => document.getAnimations().forEach((a) => { a.pause(); a.currentTime = ms; }), (i * 1000) / FPS);
  await page.screenshot({ path: path.join(frames, `f${String(i).padStart(4, '0')}.png`) });
}
await browser.close();
const mp4 = path.join(root, 'video', 'demo.mp4');
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(frames, 'f%04d.png'),
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'slow', '-crf', '24', '-movflags', '+faststart', mp4]);
rmSync(frames, { recursive: true });
console.log('mp4', path.relative(root, mp4));
