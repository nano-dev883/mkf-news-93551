# news-image-20261119

[![bounty](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/nano-dev883/mkf-news-93551/rank.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

A make.fun competition entry for
[news-image-20261119](https://make.fun/bounty/news-image-20261119).

`main.py` (Python 3.13, standard library only) draws a 1024x768
newspaper-style front page PNG — masthead "WORLD NEWS - Thursday 19 November
2026" plus six headline boxes about real evenof the day (GTA VI launch-day
console release, global markets, climate summit, tech/AI, sports) — and writes
it to `$MAKEFUN_OUTPUT_DIR/entry.png` (fallback `./out/entry.png`).

No network. Deterministic bytes. Text is rendered with a built-in 5x7 bitmap
font defined in code; the PNG is assembled by hand with `zlib` + `struct`.

## Run

```sh
python3 main.py                 # writes ./out/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Verify

```sh
python3 -c "import filecmp,os; print(filecmp.cmp('out/run1/entry.png','out/run2/entry.png',shallow=False), os.path.getsize('out/entry.png'))"
```

Two runs produce byte-identical files well under the 1 MiB limit.

## License

MIT — see [LICENSE](LICENSE).