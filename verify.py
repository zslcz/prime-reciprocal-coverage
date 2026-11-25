"""Recompute full-prefix depths and first missing words with integer arithmetic."""

import argparse
import csv
from fractions import Fraction
from functools import lru_cache
from itertools import count
from math import isqrt
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SHELL_FIELDS = ("base", "j", "prime_depth", "integer_depth", "first_missing_count")
WORD_FIELDS = ("base", "j", "m", "word", "first", "last")


def ceil_div(a, b):
    return -(-a // b)


def atan_bounds(q, scale):
    """Consecutive partial sums of the alternating series for atan(1/q)."""
    total = Fraction(0)
    for k in count():
        term = Fraction((-1) ** k, (2 * k + 1) * q ** (2 * k + 1))
        following = total + term
        if abs(term) < Fraction(1, 100 * scale):
            return min(total, following), max(total, following)
        total = following


@lru_cache(maxsize=None)
def base_bounds(base, digits):
    if digits < 1:
        raise ValueError("digits must be positive")
    scale = 10 ** digits
    if base == "pi":
        a, b = atan_bounds(5, scale)
        c, d = atan_bounds(239, scale)
        low, high = 16 * a - 4 * d, 16 * b - 4 * c
    elif base == "e":
        term, low = Fraction(1), Fraction(1)
        for k in count(1):
            term /= k
            low += term
            # After 1/k!, the tail is bounded by a geometric series.
            high = low + term / k
            if (high - low) * scale <= 1:
                break
    else:
        raise ValueError("supported sample bases are pi and e")
    return int(low * scale), ceil_div(high.numerator * scale, high.denominator), scale


def floor_ratio(numerator, denominator):
    low = numerator[0] // denominator[1]
    high = numerator[1] // denominator[0]
    if low != high:
        raise ArithmeticError("unresolved integer endpoint; increase --digits")
    return low


def intervals(bounds, j, m):
    """Inclusive integer endpoints. Empty windows have first == last + 1."""
    if j < 1 or m < 1:
        raise ValueError("shell and depth must be positive")
    lo, hi, scale = bounds

    def multiply(pair):
        return pair[0] * lo // scale, ceil_div(pair[1] * hi, scale)

    power = (scale, scale)
    for _ in range(j + m - 1):
        power = multiply(power)
    # Clearing negative powers in I_w gives beta^(j+m-1)/(W+1) < n
    # <= beta^(j+m-1)/W, where W is the Horner polynomial for w.
    stack = [("1", (scale, scale))]
    while stack:
        word, value = stack.pop()
        if len(word) == m:
            lower = floor_ratio(power, (value[0] + scale, value[1] + scale))
            yield word, lower + 1, floor_ratio(power, value)
        else:
            child = multiply(value)
            stack.append((word + "1", (child[0] + scale, child[1] + scale)))
            stack.append((word + "0", child))


class PrimeSieve:
    def __init__(self, limit):
        self.limit = limit
        self.odd = bytearray([1]) * ((limit + 1) // 2)
        self.odd[0] = 0
        for p in range(3, isqrt(limit) + 1, 2):
            if self.odd[p // 2]:
                start = (p * p) // 2
                self.odd[start::p] = bytes(len(range(start, len(self.odd), p)))

    def has_prime(self, first, last):
        if last > self.limit:
            raise ValueError("interval outside the sieve")
        if first <= 2 <= last:
            return True
        return self.odd.find(b"\x01", max(1, first // 2), (last + 1) // 2) >= 0


def survey(limit, digits):
    if limit < 2:
        raise ValueError("limit must be at least 2")
    sieve = PrimeSieve(limit)
    shells, words = [], []
    for base in ("pi", "e"):
        bounds = base_bounds(base, digits)
        for j in count(1):
            _, _, end = next(intervals(bounds, j, 1))
            if end > limit:
                break
            for m in count(1):
                missing = [(base, j, m, w, a, b) for w, a, b in intervals(bounds, j, m)
                           if not sieve.has_prime(a, b)]
                if missing:
                    break
            words.extend(missing)
            for d in count(m):
                if any(a > b for _, a, b in intervals(bounds, j, d)):
                    break
            shells.append((base, j, m - 1, d - 1, len(missing)))
    return shells, words


def compare_or_write(path, fields, rows, write):
    if write:
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(fields)
            writer.writerows(rows)
    else:
        with path.open(encoding="utf-8", newline="") as stream:
            reference = list(csv.reader(stream))
        current = [list(fields)] + [[str(v) for v in row] for row in rows]
        if current != reference:
            raise ValueError(f"recomputed data differ from {path.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--digits", type=int, default=50)
    parser.add_argument("--limit", type=int, default=10**8)
    parser.add_argument("--write", type=Path, metavar="DIRECTORY",
                        help="write computed CSVs instead of comparing with the release")
    args = parser.parse_args()
    if args.write is None and args.limit != 10**8:
        parser.error("the reference tables use limit 100000000; use --write with another limit")
    shells, words = survey(args.limit, args.digits)
    target = args.write or ROOT / "data"
    if args.write is not None:
        target.mkdir(parents=True, exist_ok=True)
    compare_or_write(target / "shells.csv", SHELL_FIELDS, shells, args.write is not None)
    compare_or_write(target / "missing.csv", WORD_FIELDS, words, args.write is not None)
    print(f"{len(shells)} shells, {len(words)} first missing prefixes; "
          f"limit={args.limit}, digits={args.digits}")
