# news-image-20261125 — "The World Today"

[![make.fun](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/c/news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/akbar9696/news-image-20261125/rank.svg)](https://make.fun/c/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/akbar9696/news-image-20261125/reward.svg)](https://make.fun/c/news-image-20261125)

Entry for make.fun competition `news-image-20261125`: sum up the world news
of **Wednesday, 25 November 2026** in one image. Pot $100; entries close
27 November 2026 07:00 WIB.

## The image

`entry.png` (1024×1024) is a deterministic newspaper front page drawn by
`generate.py` (Python + Pillow, flat shapes and DejaVu fonts, plus one
generated illustration `lead-art.png` cropped into the lead panel; no
network, no randomness):

- Masthead **"THE WORLD TODAY"** with the date **"WEDNESDAY, 25 NOVEMBER
  2026"** in red.
- Six stories, each with a headline, a short factual summary and an
  illustration:
  1. **Lead — Mines hit two tankers in Hormuz as war widens** (Iran's
     Guards said two tankers hit mines in the Strait of Hormuz; a
     Saudi-led coalition struck Yemen's Hodeidah port; Trump warned
     Tehran of a "very traumatic" outcome if no nuclear deal is reached).
  2. **Nvidia slides 7% as AI rally fades** (shares fell 7% as lawmakers
     questioned Trump's role in Huang's return; Nikkei -2.76%).
  3. **Ukraine hits Russian warship off Libya** (leaked records put
     Russian war dead at 720,000).
  4. **Oil states killed COP31 — now what?** (after COP31 collapsed,
     Saudi Arabia and oil states blocked any fossil-fuel phaseout
     mention).
  5. **Gunmen hold 20 hostage in Cartagena shop** (armed men held about
     20 people hostage in a Cartagena supermarket; a car bomb injured
     23).
  6. **Pakistan's first astronaut reaches China's station** (Zeeshan Ali
     became Pakistan's first astronaut aboard China's Shenzhou-24
     spacecraft, reaching the Tiangong space station).

All facts were verified from live wire reports on 25 November 2026; no
numbers invented.

## Files

- `generate.py` — deterministic generator (run twice → identical sha256).
- `lead-art.png` — generated illustration for the lead panel.
- `entry.png` — the submitted image.
- `main.ts` — validates entry.png (PNG signature, IHDR, 1024×1024,
  ≤ 1 MiB) and copies it to `$MAKEFUN_OUTPUT_DIR/entry.png`.
- `LICENSE` — MIT.

## Verify

```sh
python3 generate.py            # regenerates entry.png deterministically
MAKEFUN_OUTPUT_DIR=/tmp/out node main.ts   # validates + copies
```
