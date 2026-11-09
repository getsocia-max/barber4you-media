#!/usr/bin/env python3
"""Barber4You publish times: 5 slots a day, each on a non-round minute that changes every day.

Usage:  python3 tools/slot_times.py            -> today + next 13 days (Israel dates)
        python3 tools/slot_times.py 2026-11-10 -> that day only
        python3 tools/slot_times.py 2026-11-10 14 -> that day, 14 days

Rule (user 9.11.2026): never post on a round minute, never the same minute pattern two days
running, so the account doesn't look automated. Shabbat rule still wins: Friday nothing after
14:00, Saturday nothing before 18:00. Keep this file and slotTimes() in the dashboard identical.
"""
import sys, datetime as dt

# minutes we may use: 1..24, never a multiple of 5
POOL = [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24]
STEPS = [3, 7, 9, 11, 13, 17]  # all coprime with 20 -> 5 different minutes per day
EPOCH = dt.date(2026, 1, 1)

# base hours per weekday (Python: Mon=0 .. Sun=6). "-" = the post goes up BEFORE that hour
# (Fri 14:00 must be before Shabbat, so that slot is 13:36-13:59).
BASE = {
    6: ["08", "12", "16", "18", "20"],  # Sun
    0: ["08", "12", "16", "18", "20"],
    1: ["08", "12", "16", "18", "20"],
    2: ["08", "12", "16", "18", "20"],
    3: ["08", "12", "16", "18", "20"],  # Thu
    4: ["08", "12", "-14"],             # Fri
    5: ["18", "20", "21"],             # Sat
}


def slot_times(day: dt.date):
    d = (day - EPOCH).days
    start, step = (d * 7 + 3) % 20, STEPS[d % 6]
    out = []
    for i, h in enumerate(BASE[day.weekday()]):
        m = POOL[(start + i * step) % 20]
        if h.startswith("-"):
            out.append((h[1:], f"{int(h[1:]) - 1:02d}:{60 - m:02d}"))
        else:
            out.append((h, f"{h}:{m:02d}"))
    return out  # [(slot hour "08", exact time "08:07"), ...]


if __name__ == "__main__":
    if len(sys.argv) > 1:
        first = dt.date.fromisoformat(sys.argv[1])
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    else:
        first = (dt.datetime.utcnow() + dt.timedelta(hours=2)).date()  # Israel (winter); fine for a listing
        n = 14
    names = ["ב", "ג", "ד", "ה", "ו", "ש", "א"]
    for k in range(n):
        day = first + dt.timedelta(days=k)
        print(day.isoformat(), names[day.weekday()], "  ".join(t for _, t in slot_times(day)))
