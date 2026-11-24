# One Word, One Username, One Reward

[![make.fun](https://make.fun/badge/u-rusdyxbt-one-word-one-username-one-reward-1a191fae.svg)](https://make.fun/c/u-rusdyxbt-one-word-one-username-one-reward-1a191fae)
[![rank](https://make.fun/badge/u-rusdyxbt-one-word-one-username-one-reward-1a191fae/freezzard/one-word-username-entry1/rank.svg)](https://make.fun/c/u-rusdyxbt-one-word-one-username-one-reward-1a191fae)
[![reward](https://make.fun/badge/u-rusdyxbt-one-word-one-username-one-reward-1a191fae/freezzard/one-word-username-entry1/reward.svg)](https://make.fun/c/u-rusdyxbt-one-word-one-username-one-reward-1a191fae)

Entry for the [One Word, One Username, One Reward](https://make.fun/c/u-rusdyxbt-one-word-one-username-one-reward-1a191fae) competition on make.fun.

## What it does

`main.py` runs a small local tournament over eight candidate words,
scoring each on four axes (smile on first read, stickiness, character,
brevity) with weights that mirror the judge's brief, then writes the
winning word — **kerfuffle** — alone to `/output/entry.txt`: one word,
9 characters, no newline, no padding.

## How to run

```sh
python3 main.py
```

By default it writes to `/output/entry.txt`. For a local run, point it
elsewhere:

```sh
MAKEFUN_OUTPUT=/tmp/entry.txt python3 main.py
```

The program prints the full tournament table, the winning word, and
the byte count written, then re-reads the file to confirm it holds
exactly the winning word. Two runs produce byte-identical output.
