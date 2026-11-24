"""One Word, One Username, One Reward -- entry program.

A make.fun username is one word and nothing more: at most 30
characters, no explanation, no links, no pitch. The house judge reads
two usernames at a time and keeps the funnier or more interesting one,
weighing its brief in order: a smile on the first read, a name that
sticks after one look, character in the handle, a clean single word,
and a handle its owner wears gladly.

This program chooses its word by tournament, then writes the winner
alone to the entry file. Eight candidate words are scored on four
axes, each axis marked 1 to 5 by the author at build time:

    mirth      -- the word raises a smile on the first read
    memory     -- the word sticks in the mind after one look
    persona    -- the word carries character, a handle worth wearing
    trim       -- the word is short, tight, easy to say and type

Axis weights mirror the judge's order: mirth 3, memory 3, persona 2,
trim 1. The highest weighted total wins the tournament. Ties fall to
the shorter word, then to the earlier word alphabetically, which makes
the outcome deterministic for a fixed roster.

Author notes on each candidate:

    kerfuffle   a genuine word for a noisy commotion; funny the
                instant it is read, hard to forget, and a handle
                its owner wears with pride.
    blorp       a short invented pop; punchy at first, thin after
                the first laugh.
    bamboozle   a warm trickster classic; familiar enough to lose
                a little surprise.
    quixotic    literary and romantic; elegant, slightly bookish
                for a handle meant to land fast.
    frobnicate  hacker folklore; playful for insiders, opaque for
                a reader meeting it cold.
    snazzle     bright invented sparkle; cheerful, a touch generic.
    snafu       a dry old acronym-word; wry humour, modest charm.
    wobble      gentle and silly; sweet, low on staying power.

The winning word is written to the entry file as UTF-8 with no
trailing newline and no padding: the gate counts every character and
the brief rewards a clean single word. The program re-reads the file
afterwards and raises when the bytes differ from the chosen word, so
a silent bad write can never pass as a good run.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass


DEFAULT_TARGET = "/output/entry.txt"
TARGET_ENV = "MAKEFUN_OUTPUT"
CHAR_CEILING = 30
CHAR_FLOOR = 1

# Axis order is the judge's order. Weights ride alongside the names.
AXIS_TABLE = (
    ("mirth", 3),
    ("memory", 3),
    ("persona", 2),
    ("trim", 1),
)

# Roster rows: handle word, mirth, memory, persona, trim. The draft
# order is the author's own; the ranking key below decides all places.
HANDLE_ROSTER = (
    ("kerfuffle", 5, 5, 5, 3),
    ("blorp", 4, 4, 4, 5),
    ("bamboozle", 4, 4, 4, 4),
    ("quixotic", 3, 4, 4, 4),
    ("frobnicate", 4, 3, 4, 3),
    ("snazzle", 3, 3, 4, 4),
    ("snafu", 3, 3, 3, 5),
    ("wobble", 3, 3, 3, 5),
)


@dataclass(frozen=True)
class HandleBid:
    """One candidate handle with its four axis marks."""

    handle: str
    mirth: int
    memory: int
    persona: int
    trim: int

    def total(self):
        """Weighted tournament score, judge order first."""
        marks = {
            "mirth": self.mirth,
            "memory": self.memory,
            "persona": self.persona,
            "trim": self.trim,
        }
        tally = 0
        for axis_name, weight in AXIS_TABLE:
            tally += marks[axis_name] * weight
        return tally

    def rank_key(self):
        """Best first: highest total, then shortest, then alphabetical."""
        return (-self.total(), len(self.handle), self.handle)

    def table_row(self):
        """One line of the tournament table for this candidate."""
        return (
            f"{self.handle:<12} mirth={self.mirth} memory={self.memory} "
            f"persona={self.persona} trim={self.trim} total={self.total()}"
        )


def collect_bids(roster):
    """Turn raw roster rows into frozen HandleBid records."""
    bids = []
    for row in roster:
        bid = HandleBid(
            handle=row[0],
            mirth=row[1],
            memory=row[2],
            persona=row[3],
            trim=row[4],
        )
        bids.append(bid)
    return bids


def order_bids(bids):
    """Sort the bids best-first on the deterministic rank key."""
    ordered = sorted(bids, key=lambda bid: bid.rank_key())
    return ordered


def crown_winner(ordered):
    """Name the head of the ordered bids as the tournament winner."""
    winner = ordered[0]
    return winner


def gate_findings(handle):
    """List every gate violation for the handle; an empty list passes."""
    findings = []
    if len(handle) < CHAR_FLOOR:
        findings.append("handle is empty")
    if len(handle) > CHAR_CEILING:
        findings.append("handle runs past 30 characters")
    if handle.strip() != handle:
        findings.append("handle carries edge whitespace")
    if len(handle.split()) != 1:
        findings.append("handle is more than one token")
    if handle.isalpha() is False:
        findings.append("handle holds non-letter characters")
    if handle.islower() is False:
        findings.append("handle is not all lowercase")
    return findings


def enforce_gate(handle):
    """Raise with the full findings when the winner fails the gate."""
    findings = gate_findings(handle)
    if findings:
        detail = "; ".join(findings)
        raise ValueError(f"winning handle {handle!r} fails the gate: {detail}")


def choose_target():
    """Target path: env override for local runs, sandbox path by default."""
    override = os.environ.get(TARGET_ENV, "")
    if override:
        return override
    return DEFAULT_TARGET


def publish_handle(handle, target):
    """Write the handle alone, no newline, no padding, as UTF-8."""
    folder = os.path.dirname(target)
    if folder:
        os.makedirs(folder, exist_ok=True)
    try:
        with open(target, "w", encoding="utf-8", newline="") as stream:
            stream.write(handle)
    except OSError as publish_err:
        raise OSError(
            f"cannot publish handle to {target}: {publish_err}"
        ) from publish_err
    return len(handle.encode("utf-8"))


def confirm_handle(handle, target):
    """Re-read the file and demand it holds exactly the winning handle."""
    try:
        with open(target, "r", encoding="utf-8", newline="") as stream:
            recorded = stream.read()
    except OSError as confirm_err:
        raise OSError(
            f"cannot re-read entry file {target}: {confirm_err}"
        ) from confirm_err
    if recorded != handle:
        raise ValueError(
            f"entry file holds {recorded!r}, winning handle is {handle!r}"
        )


def show_tournament(ordered, winner):
    """Print the ranking table and the winner line to stdout."""
    print("one-word tournament: 8 handles, 4 axes, judge-order weights")
    for place, bid in enumerate(ordered, start=1):
        print(f"  {place}. {bid.table_row()}")
    print(f"winner: {winner.handle} (total {winner.total()})")


def main(argv):
    """Collect bids, crown the winner, gate it, publish it, confirm it."""
    bids = collect_bids(HANDLE_ROSTER)
    ordered = order_bids(bids)
    winner = crown_winner(ordered)
    enforce_gate(winner.handle)
    target = choose_target()
    byte_count = publish_handle(winner.handle, target)
    confirm_handle(winner.handle, target)
    show_tournament(ordered, winner)
    print(f"published {byte_count} bytes to {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
