// news-image-20261121 entry: "The World Today — Saturday 21 November 2026".
// A dense newspaper front page (32 dated stories, 6 regions) drawn by
// tools/render.py and held in this repo as entry.png. This program copies
// that image to the grader's output directory, after checking it is really
// a 1024x1024 PNG of at most 1 MiB. Node 22, standard library only, no
// network, no clock, no randomness: the same bytes come out every run.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const SOURCE = new URL('./entry.png', import.meta.url);
const TARGET = join(OUT_DIR, 'entry.png');

const bytes = readFileSync(SOURCE);

// A PNG starts with its 8-byte signature; bytes 16..24 hold the IHDR
// width and height as big-endian uint32s. Refuse anything that is not a
// 1024x1024 PNG, and refuse anything over the 1 MiB gate limit.
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!bytes.subarray(0, 8).equals(PNG_MAGIC)) {
  throw new Error('entry.png is not a PNG file');
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png is ${width}x${height}, expected 1024x1024`);
}
if (bytes.length > 1024 * 1024) {
  throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB limit`);
}

mkdirSync(OUT_DIR, { recursive: true });
copyFileSync(SOURCE, TARGET);

// The copy must be byte-for-byte the source image.
const copied = readFileSync(TARGET);
if (!copied.equals(bytes)) {
  throw new Error('entry.png copy differs from the source image');
}
console.log(`wrote ${TARGET} (${bytes.length} bytes, 1024x1024 PNG)`);
console.log(`source size on disk: ${statSync(SOURCE).size} bytes`);
