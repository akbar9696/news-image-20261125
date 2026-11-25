/**
 * news-image-20261125 entry program (Node 22+, standard library only).
 *
 * The newspaper image is built by generate.py and stored in this repo as
 * entry.png (1024x1024, 279,129 bytes, sha256
 * d5fe8a1f0791bafec11c9a015e1f5afcaa77e6fccdaba004992343bdc4a525e2).
 * This program only checks that file and writes it to the
 * output directory make.fun provides, so both graded runs produce
 * identical bytes. It never generates, edits or fetches anything.
 */
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const LIMIT_BYTES = 1_048_576;
const SIDE = 1024;

const repoDir = dirname(fileURLToPath(import.meta.url));
const source = join(repoDir, "entry.png");
const targetDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const target = join(targetDir, "entry.png");

const PNG_MAGIC = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

function fail(message) {
  throw new Error(`entry.png rejected: ${message}`);
}

function validate(bytes, size) {
  if (size > LIMIT_BYTES) {
    fail(`is ${size} bytes, over the 1 MiB limit`);
  }
  if (!PNG_MAGIC.every((byte, i) => bytes[i] === byte)) {
    fail("does not start with the PNG signature");
  }
  if (bytes.toString("ascii", 12, 16) !== "IHDR") {
    fail("has no IHDR chunk");
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width !== SIDE || height !== SIDE) {
    fail(`is ${width}x${height}, expected ${SIDE}x${SIDE}`);
  }
  return { width, height };
}

function main() {
  const bytes = readFileSync(source);
  const size = statSync(source).size;
  const { width, height } = validate(bytes, size);
  mkdirSync(targetDir, { recursive: true });
  copyFileSync(source, target);
  console.log(`wrote ${target} (${size} bytes, ${width}x${height})`);
}

main();
