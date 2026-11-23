#!/usr/bin/env node
// HTML → PNG with headless Chrome, at an exact canvas size. The designer agent writes HTML/CSS and this
// turns it into the deliverable, so the QA scripts have a real PNG to check.
//   node tools/html_png.mjs <file.html> <out.png> [WIDTHxHEIGHT]      default 1080x1350
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, statSync } from "node:fs";
import path from "node:path";

const CHROME = process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const die = (m) => { console.error(`html_png: ${m}`); process.exit(1); };
const [src, out, size = "1080x1350"] = process.argv.slice(2);
if (!src || !out) die("usage: html_png.mjs <file.html> <out.png> [WIDTHxHEIGHT]");
const html = path.resolve(src), png = path.resolve(out);
if (!html.endsWith(".html") || !existsSync(html)) die(`missing ${html}`);
if (!png.endsWith(".png")) die("output must be .png");
const m = size.match(/^(\d{2,4})x(\d{2,4})$/);
if (!m) die("size must be WIDTHxHEIGHT, e.g. 1080x1920");
if (!existsSync(CHROME)) die("Chrome not found (set CHROME_PATH)");
mkdirSync(path.dirname(png), { recursive: true });
execFileSync(CHROME, ["--headless=new", "--allow-file-access-from-files", "--hide-scrollbars", `--window-size=${m[1]},${m[2]}`, "--virtual-time-budget=6000", `--screenshot=${png}`, `file://${html}`], { stdio: "ignore", timeout: 60000 });
if (!existsSync(png)) die("Chrome produced no PNG");
console.log(`✓ ${png} (${m[1]}×${m[2]}, ${Math.round(statSync(png).size / 1024)} KB)`);
