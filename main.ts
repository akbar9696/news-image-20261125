// news-image-20261125 — entrypoint.
//
// Copies the pre-rendered front page (entry.png, in this repository)
// into the output directory after checking it is a well-formed PNG of
// 1024x1024 pixels and no more than 1 MiB. The program takes no input,
// reads no network and writes exactly one file, so repeated runs agree.
//
// entry.png sha256: a1150638bc71fdf89b48263b0274bb3ab3926a487e4e2c07d64a6fb7fa3517ec
// entry.png bytes: 368575
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const REPO = dirname(fileURLToPath(import.meta.url));
const SOURCE = join(REPO, "entry.png");
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "out";
const TARGET = join(OUT_DIR, "entry.png");

function die(message: string): never {
  console.error(`entrypoint: ${message}`);
  process.exit(1);
}

function sha256Hex(bytes: Buffer): string {
  return createHash("sha256").update(bytes).digest("hex");
}

function checkPng(bytes: Buffer): void {
  const magic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  if (bytes.length < 33 || !bytes.subarray(0, 8).equals(magic)) {
    die("entry.png is not a PNG file");
  }
  if (bytes.subarray(12, 16).toString("ascii") !== "IHDR") {
    die("entry.png has no IHDR chunk where one belongs");
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width !== 1024 || height !== 1024) {
    die(`entry.png is ${width}x${height}, expected 1024x1024`);
  }
  if (bytes.length > 1048576) {
    die(`entry.png is ${bytes.length} bytes, over the 1 MiB limit`);
  }
}

const input = readFileSync(SOURCE);
checkPng(input);
const digest = sha256Hex(input);
mkdirSync(OUT_DIR, { recursive: true });
copyFileSync(SOURCE, TARGET);
const written = readFileSync(TARGET);
if (sha256Hex(written) !== digest) {
  die("copied file does not match entry.png");
}
const shown = statSync(TARGET).size;
console.log(`ok: entry.png ${shown} bytes sha256 ${digest} -> ${TARGET}`);
