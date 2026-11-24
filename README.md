# news-image-20261124 — The World Today: Tuesday, 24 November 2026

[![news](https://img.shields.io/badge/news-35%20stories-blue)](./entry.png)
[![regions](https://img.shields.io/badge/regions-7-green)](./entry.png)
[![format](https://img.shields.io/badge/format-1024x1024%20PNG-red)](./entry.png)

One image summing up the world's news of **Tuesday, 24 November 2026**:
1 hero (Asia rallies on Huang's return — Nikkei +4.5%, Kospi +7.5%, Taiex +9.1%),
3 leads, 31 briefs; 35 stories, 7 regions, UTC timeline. No map.

## Build

```sh
python3 render.py   # writes entry.png (1024x1024, <=1 MiB, deterministic)
node main.ts        # verifies entry.png and copies it to $MAKEFUN_OUTPUT_DIR
```

## Entry

- Competition: `news-image-20261124` — "Sum up 24 November's world news in one image"
- Prize: $100 (top 50 paid); deadline 26 Nov 2026 07:00 WIB; round 1 cutoff 24 Nov 19:00 WIB
- Research + date check (35 rows): `news-image-20261124-research.md`

## Verification
- Rendered twice, byte-identical (sha256 dcaf22fc…b0aa); GATE-D 300px passed.
