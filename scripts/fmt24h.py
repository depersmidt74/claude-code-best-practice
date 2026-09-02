#!/usr/bin/env python3
"""Format Binance 24h ticker JSON as a table, sorted by absolute 24h move.

Reads the response of /api/v3/ticker/24hr on stdin — one object or a list:

    curl -sS -g 'https://api.binance.com/api/v3/ticker/24hr?symbols=["BTCUSDT","ETHUSDT"]' \\
      | python3 scripts/fmt24h.py

Batch symbols into a single request: it costs one weight unit instead of
several and gives one consistent snapshot rather than several moments in time.

`-g` (--globoff) is required for the multi-symbol form: curl otherwise reads the
brackets as its own URL-range syntax and dies with "bad range specification"
before the request ever leaves the machine. `-sS` keeps the progress meter off
while letting curl report why it failed — without it that error is invisible and
the empty pipe looks like a problem in this script.

Exit codes: 0 ok · 1 the exchange returned an error · 2 unusable input.
"""

import datetime
import json
import sys

FIELDS = ("symbol", "lastPrice", "priceChangePercent", "lowPrice", "highPrice",
          "quoteVolume", "closeTime")


def die(msg, code=2):
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def main():
    raw = sys.stdin.read().strip()
    if not raw:
        die("Пустой ввод: нечего форматировать.")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        die(f"Ответ не является JSON ({e}). Первые 200 символов:\n{raw[:200]}")

    # An error from Binance arrives as {"code": -1121, "msg": "Invalid symbol."}
    if isinstance(data, dict) and "code" in data and "msg" in data:
        die(f"Binance вернул ошибку {data['code']}: {data['msg']}", 1)

    rows = [data] if isinstance(data, dict) else data
    if not rows:
        die("Ответ пуст: ни одного символа.")

    missing = {f for r in rows if isinstance(r, dict) for f in FIELDS if f not in r}
    if missing or not all(isinstance(r, dict) for r in rows):
        die(f"Ответ не похож на /api/v3/ticker/24hr — нет полей: {', '.join(sorted(missing)) or '?'}")

    w = max(len(r["symbol"]) for r in rows)
    print(f"{'СИМВОЛ'.ljust(w)}  {'ЦЕНА':>14}  {'24ч %':>8}  "
          f"{'МИН 24ч':>14}  {'МАКС 24ч':>14}  {'ОБЪЁМ (quote)':>16}")
    for r in sorted(rows, key=lambda r: -abs(float(r["priceChangePercent"]))):
        print(f"{r['symbol'].ljust(w)}  {float(r['lastPrice']):>14,.4f}  "
              f"{float(r['priceChangePercent']):>+7.2f}%  "
              f"{float(r['lowPrice']):>14,.4f}  {float(r['highPrice']):>14,.4f}  "
              f"{float(r['quoteVolume']):>16,.0f}")

    # closeTime is milliseconds; timezone.utc keeps this working before 3.11.
    snapshot = datetime.datetime.fromtimestamp(
        max(int(r["closeTime"]) for r in rows) / 1000, datetime.timezone.utc)
    print(f"\nсрез: {snapshot:%Y-%m-%d %H:%M:%S} UTC · "
          f"источник api.binance.com/api/v3/ticker/24hr")


if __name__ == "__main__":
    main()
