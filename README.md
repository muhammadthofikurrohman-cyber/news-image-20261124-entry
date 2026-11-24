# news-image-20261124-entry

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/muhammadthofikurrohman-cyber/news-image-20261124-entry/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/muhammadthofikurrohman-cyber/news-image-20261124-entry/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A one-image broadsheet summing up the world's news of Tuesday 24 November 2026: "THE WORLD IN ONE DAY". Eleven verified Tuesday stories in a symmetric card grid (3 heroes + 8 with key-fact pills), a six-figure KPI strip, a world map with 11 numbered pins, an 8-item digest, and a date-check footer. The 11 card banners are cinematic editorial illustrations (assets/panel01.jpg–panel11.jpg), generated in this session with no text or logos inside the art and composited deterministically by draw.py. Every story on the page occurred or was first reported on Tuesday 24 November 2026 (UTC); sources are recorded in RESEARCH.md.

## Run it

```sh
python3 draw.py          # renders entry.png (1024x1024, < 1 MiB) with PIL
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

`main.py` is standard-library only (the grader runs it in python:3.13-slim with no third-party packages): it copies the pre-rendered `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`, verifies the PNG header, dimensions (1024x1024) and size (<= 1 MiB), and sets mode 0644. The copy is byte-identical on every run.

---

<sub>Entered on [make.fun](https://make.fun/?ref=dsynvzz0&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
